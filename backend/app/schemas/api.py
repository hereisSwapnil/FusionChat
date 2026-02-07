from typing import Optional, List
from pydantic import BaseModel
from app.schemas.chat import Chat
from app.schemas.message import Message
from app.schemas.document import Document


class ChatCreate(BaseModel):
    title: str


class ChatUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None


class MessageCreate(BaseModel):
    content: str
    role: Optional[str] = "user"


class ChatDetailed(Chat):
    messages: List[Message] = []
    documents: List[Document] = []
