# Relationship Model
from uuid import UUID
from app.schemas.base import BaseSchema
from datetime import datetime
from pydantic import Field
from typing import Optional
from uuid import uuid4


class Relationship(BaseSchema):
    id: UUID = Field(default_factory=uuid4)
    chat_id: UUID
    source_id: UUID
    target_id: UUID
    type: str
    confidence: Optional[float]
    chunk_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)
