from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.crm import Channel


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_id: int
    channel: Channel
    unread_count: int
    created_at: datetime


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    sender: str
    content: str
    status: str
