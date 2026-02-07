from enum import Enum


class ChatStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    TEXT = "text"
