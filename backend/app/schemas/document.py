# Document Model
from uuid import UUID
from app.schemas.base import BaseSchema
from datetime import datetime
from app.core.constants import DocumentStatus, DocumentType
from pydantic import Field
from uuid import uuid4


class Document(BaseSchema):
    id: UUID = Field(default_factory=uuid4)
    chat_id: UUID
    file_name: str
    file_size: int
    file_type: DocumentType
    checksum: str
    status: DocumentStatus
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
