from datetime import datetime
from uuid import UUID, uuid4
from typing import List
from sqlalchemy import String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    messages: Mapped[List["Message"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan"
    )
    documents: Mapped[List["Document"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id"))
    role: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chat: Mapped["Chat"] = relationship(back_populates="messages")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id"))
    file_name: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[int] = mapped_column(Integer)
    file_type: Mapped[str] = mapped_column(String(50))
    checksum: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    chat: Mapped["Chat"] = relationship(back_populates="documents")
