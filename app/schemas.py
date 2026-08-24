import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateConversationRequest(BaseModel):
    user_id: uuid.UUID
    title: str | None = None


class CreateConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime


class SendMessageRequest(BaseModel):
    content: str


class SendMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    created_at: datetime