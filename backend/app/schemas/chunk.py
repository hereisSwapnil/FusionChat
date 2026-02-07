# Entity Model
from uuid import UUID
from app.schemas.base import BaseSchema
from datetime import datetime
from pydantic import Field
from uuid import uuid4


class Chunk(BaseSchema):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    chat_id: UUID
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
