# Entity Model
from uuid import UUID
from app.schemas.base import BaseSchema
from typing import Optional
from datetime import datetime
from pydantic import Field
from uuid import uuid4


class Entity(BaseSchema):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    chat_id: UUID
    type: str
    name: str
    confidence: Optional[float]
    chunk_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)
