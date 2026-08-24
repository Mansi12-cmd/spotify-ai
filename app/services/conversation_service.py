import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Message


class ConversationService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(
        self,
        user_id: uuid.UUID,
        title: str | None = None,
    ) -> Conversation:

        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        self.db.add(conversation)

        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
    ) -> Message:

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        self.db.add(message)

        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def get_conversation(
        self,
        conversation_id: uuid.UUID,
    ) -> Conversation | None:

        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.id == conversation_id
            )
        )

        return result.scalar_one_or_none()

    async def get_messages(
        self,
        conversation_id: uuid.UUID,
    ) -> list[Message]:

        result = await self.db.execute(
            select(Message)
            .where(
                Message.conversation_id == conversation_id
            )
            .order_by(Message.created_at.asc())
        )

        return list(result.scalars().all())