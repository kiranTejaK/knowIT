import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.collection import Collection


class CollectionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, collection_id: uuid.UUID) -> Optional[Collection]:
        result = await self.db.execute(select(Collection).where(Collection.id == collection_id))
        return result.scalars().first()

    async def get_by_user_and_name(self, user_id: uuid.UUID, name: str) -> Optional[Collection]:
        result = await self.db.execute(
            select(Collection).where(
                Collection.user_id == user_id,
                Collection.name == name
            )
        )
        return result.scalars().first()

    async def list_by_user(self, user_id: uuid.UUID) -> List[Collection]:
        result = await self.db.execute(
            select(Collection).where(Collection.user_id == user_id).order_by(Collection.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, collection: Collection) -> Collection:
        self.db.add(collection)
        await self.db.commit()
        await self.db.refresh(collection)
        return collection

    async def update(self, collection: Collection) -> Collection:
        await self.db.commit()
        await self.db.refresh(collection)
        return collection

    async def delete(self, collection: Collection) -> None:
        await self.db.delete(collection)
        await self.db.commit()
