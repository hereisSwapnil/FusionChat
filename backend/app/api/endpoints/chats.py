from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from app.services.chat_service import ChatService
from app.schemas.api import ChatCreate, ChatUpdate, MessageCreate, ChatDetailed
from app.schemas.chat import Chat
from app.schemas.message import Message as MessageSchema

router = APIRouter(prefix="/chats", tags=["chats"])


# Dependency to get ChatService
def get_chat_service():
    return ChatService()


@router.post("", response_model=Chat, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: ChatCreate, service: ChatService = Depends(get_chat_service)
):
    return await service.create_chat(title=chat_data.title)


@router.get("", response_model=List[Chat])
async def list_chats(
    status: Optional[str] = None, service: ChatService = Depends(get_chat_service)
):
    return await service.get_chats(status=status)


@router.get("/{chat_id}", response_model=ChatDetailed)
async def get_chat(chat_id: UUID, service: ChatService = Depends(get_chat_service)):
    chat = await service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.patch("/{chat_id}", response_model=Chat)
async def update_chat(
    chat_id: UUID,
    chat_data: ChatUpdate,
    service: ChatService = Depends(get_chat_service),
):
    chat = await service.update_chat(
        chat_id, title=chat_data.title, status=chat_data.status
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(chat_id: UUID, service: ChatService = Depends(get_chat_service)):
    success = await service.delete_chat(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    return None


@router.post("/{chat_id}/messages", response_model=MessageSchema)
async def send_message(
    chat_id: UUID,
    message: MessageCreate,
    service: ChatService = Depends(get_chat_service),
):
    # Note: message schema has chat_id, but we use the one from the URL
    return await service.handle_user_message(chat_id=chat_id, content=message.content)
