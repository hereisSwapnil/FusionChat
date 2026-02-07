# Message Model
from uuid import UUID
from app.schemas.base import BaseSchema
from app.core.constants import MessageRole
from datetime import datetime
from pydantic import Field
from uuid import uuid4


class Message(BaseSchema):
    id: UUID = Field(default_factory=uuid4)
    chat_id: UUID
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
