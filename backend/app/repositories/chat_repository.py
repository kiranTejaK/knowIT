import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import Chat
from app.models.message import Message


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, chat: Chat) -> Chat:
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def get_by_id(self, chat_id: uuid.UUID) -> Optional[Chat]:
        result = await self.db.execute(select(Chat).where(Chat.id == chat_id))
        return result.scalars().first()

    async def list_by_user(self, user_id: uuid.UUID) -> List[Chat]:
        result = await self.db.execute(
            select(Chat).where(Chat.user_id == user_id).order_by(Chat.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_chat(self, chat: Chat) -> Chat:
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def delete_chat(self, chat: Chat) -> None:
        await self.db.delete(chat)
        await self.db.commit()

    # Message operations
    async def create_message(self, message: Message) -> Message:
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def list_messages(
        self, chat_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> Tuple[List[Message], int]:
        total_stmt = select(func.count()).select_from(Message).where(Message.chat_id == chat_id)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar_one()

        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total
