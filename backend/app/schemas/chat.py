# Chat Model
from uuid import UUID
from app.schemas.base import BaseSchema
from datetime import datetime
from app.core.constants import ChatStatus
from pydantic import Field
from uuid import uuid4


class Chat(BaseSchema):
    id: UUID = Field(default_factory=uuid4)
    title: str
    status: ChatStatus
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
