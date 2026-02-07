from app.services.retrieval_service import RetrievalService
from app.services.answer_service import AnswerService
from app.schemas.message import Message as MessageSchema
from app.core.constants import MessageRole, ChatStatus
from app.models.chat import Message as MessageModel, Chat as ChatModel
from app.db.session import SessionLocal
from uuid import UUID, uuid4
from sqlalchemy import select, desc
from typing import List, Optional


class ChatService:
    def __init__(self):
        self.retrieval = RetrievalService()
        self.answer_service = AnswerService()

    async def create_chat(self, title: str) -> ChatModel:
        async with SessionLocal() as db:
            chat = ChatModel(id=uuid4(), title=title, status=ChatStatus.ACTIVE)
            db.add(chat)
            await db.commit()
            await db.refresh(chat)
            return chat

    async def get_chats(self, status: Optional[str] = None) -> List[ChatModel]:
        async with SessionLocal() as db:
            query = select(ChatModel).order_by(desc(ChatModel.created_at))
            if status:
                query = query.where(ChatModel.status == status)
            else:
                query = query.where(ChatModel.status != ChatStatus.DELETED)

            result = await db.execute(query)
            return result.scalars().all()

    async def get_chat(self, chat_id: UUID) -> Optional[ChatModel]:
        async with SessionLocal() as db:
            from sqlalchemy.orm import selectinload

            result = await db.execute(
                select(ChatModel)
                .where(ChatModel.id == chat_id)
                .options(
                    selectinload(ChatModel.messages), selectinload(ChatModel.documents)
                )
            )
            return result.scalar_one_or_none()

    async def update_chat(
        self, chat_id: UUID, title: Optional[str] = None, status: Optional[str] = None
    ) -> Optional[ChatModel]:
        async with SessionLocal() as db:
            result = await db.execute(select(ChatModel).where(ChatModel.id == chat_id))
            chat = result.scalar_one_or_none()
            if not chat:
                return None

            if title:
                chat.title = title
            if status:
                chat.status = status

            await db.commit()
            await db.refresh(chat)
            return chat

    async def delete_chat(self, chat_id: UUID) -> bool:
        async with SessionLocal() as db:
            result = await db.execute(select(ChatModel).where(ChatModel.id == chat_id))
            chat = result.scalar_one_or_none()
            if not chat:
                return False

            chat.status = ChatStatus.DELETED
            await db.commit()
            return True

    async def handle_user_message(self, chat_id, content: str) -> MessageSchema:
        # 1. Retrieve context
        context = self.retrieval.retrieve_context(chat_id, content)

        # 2. Generate answer
        answer = self.answer_service.generate_answer(content, context)

        # 3. Create assistant message and save to DB
        async with SessionLocal() as db:
            # Save user message (assuming it's not saved elsewhere yet)
            user_msg = MessageModel(
                chat_id=chat_id, role=MessageRole.USER, content=content
            )
            db.add(user_msg)

            # Save assistant message
            assistant_msg = MessageModel(
                chat_id=chat_id, role=MessageRole.ASSISTANT, content=answer
            )
            db.add(assistant_msg)
            await db.commit()

            return MessageSchema(
                id=assistant_msg.id,
                chat_id=chat_id,
                role=MessageRole.ASSISTANT,
                content=answer,
                created_at=assistant_msg.created_at,
            )
