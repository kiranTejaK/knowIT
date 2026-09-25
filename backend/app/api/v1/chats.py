import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_chat_service, get_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatCreate,
    ChatResponse,
    ChatUpdate,
    MessageCreate,
    MessageResponse,
    PaginatedMessagesResponse,
)
from app.schemas.response import APIResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("", response_model=APIResponse[ChatResponse], status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_in: ChatCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    chat = await chat_service.create_chat(current_user.id, chat_in)
    return APIResponse.ok(data=ChatResponse.model_validate(chat))


@router.get("", response_model=APIResponse[List[ChatResponse]])
async def list_chats(
    current_user: Annotated[User, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    chats = await chat_service.list_chats(current_user.id)
    return APIResponse.ok(data=[ChatResponse.model_validate(c) for c in chats])


@router.get("/{chat_id}", response_model=APIResponse[ChatResponse])
async def get_chat(
    chat_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    chat = await chat_service.get_chat(current_user.id, chat_id)
    return APIResponse.ok(data=ChatResponse.model_validate(chat))


@router.patch("/{chat_id}", response_model=APIResponse[ChatResponse])
async def rename_chat(
    chat_id: uuid.UUID,
    update_in: ChatUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    chat = await chat_service.rename_chat(current_user.id, chat_id, update_in)
    return APIResponse.ok(data=ChatResponse.model_validate(chat))


@router.delete("/{chat_id}", response_model=APIResponse[dict])
async def delete_chat(
    chat_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    await chat_service.delete_chat(current_user.id, chat_id)
    return APIResponse.ok(data={"message": "Chat deleted successfully"})


@router.post("/{chat_id}/messages", response_model=APIResponse[MessageResponse])
async def send_message(
    chat_id: uuid.UUID,
    message_in: MessageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    message = await chat_service.send_message(
        user_id=current_user.id,
        chat_id=chat_id,
        content=message_in.content,
        top_k=message_in.top_k,
    )
    return APIResponse.ok(data=MessageResponse.model_validate(message))


@router.get("/{chat_id}/messages", response_model=APIResponse[PaginatedMessagesResponse])
async def list_messages(
    chat_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    messages, total = await chat_service.list_messages(
        user_id=current_user.id,
        chat_id=chat_id,
        limit=limit,
        offset=offset,
    )
    paginated = PaginatedMessagesResponse(
        items=[MessageResponse.model_validate(m) for m in messages],
        total=total,
        limit=limit,
        offset=offset,
    )
    return APIResponse.ok(data=paginated)
