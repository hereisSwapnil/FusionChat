# Entity Model
from uuid import UUID
from app.schemas.base import BaseSchema
from datetime import datetime
from pydantic import Field
from uuid import uuid4
from typing import Optional, List, Dict, Any


class Chunk(BaseSchema):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    chat_id: UUID
    content: str
    index: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # Metadata fields for semantic chunking
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    position_ratio: Optional[float] = None  # 0.0 to 1.0, position in document
    content_type: Optional[str] = None  # narrative, code, list, table
    headings: Optional[List[str]] = None  # Markdown headings in this chunk
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata
