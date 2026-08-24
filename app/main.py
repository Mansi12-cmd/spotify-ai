from contextlib import asynccontextmanager
import uuid

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, get_db
from app.models import User
from app.models.base import Base
from app.schemas import (
    CreateConversationResponse,
    SendMessageResponse,
)
from app.services.chat_service import ChatService


class LoginRequest(BaseModel):
    username: str


class CreateConversationRequest(BaseModel):
    user_id: uuid.UUID
    title: str | None = None


class SendMessageRequest(BaseModel):
    content: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # PostgreSQL extensions required by the application.
        #
        # pgvector provides the "vector" type used by
        # MemoryFact.embedding.
        await conn.execute(
            text('CREATE EXTENSION IF NOT EXISTS "vector"')
        )

        # uuid-ossp provides uuid_generate_v4(), which is used
        # by several database/model definitions.
        await conn.execute(
            text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        )

        # Create all SQLAlchemy tables after the required
        # PostgreSQL extensions are available.
        await conn.run_sync(
            Base.metadata.create_all
        )

    yield

    await engine.dispose()


app = FastAPI(
    title="Spotify AI Personalization API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "spotify-ai-api",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }


@app.post("/login")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    username = request.username.strip()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty.",
        )

    result = await db.execute(
        select(User).where(
            User.external_id == username
        )
    )

    user = result.scalar_one_or_none()

    if user is not None:
        return {
            "user_id": str(user.id),
            "username": user.external_id,
            "is_new_user": False,
        }

    user = User(
        external_id=username,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "user_id": str(user.id),
        "username": user.external_id,
        "is_new_user": True,
    }


@app.post(
    "/conversations",
    response_model=CreateConversationResponse,
)
async def create_conversation(
    request: CreateConversationRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(
            User.id == request.user_id
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    chat_service = ChatService(db)

    conversation = await chat_service.create_conversation(
        user_id=request.user_id,
        title=request.title,
    )

    return conversation


@app.post(
    "/conversations/{conversation_id}/messages",
    response_model=SendMessageResponse,
)
async def send_message(
    conversation_id: uuid.UUID,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    chat_service = ChatService(db)

    try:
        assistant_message = await chat_service.process_message(
            conversation_id=conversation_id,
            content=request.content,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return assistant_message