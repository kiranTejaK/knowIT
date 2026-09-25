import uuid
from typing import List
import structlog
from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.collection import Collection
from app.repositories.collection_repository import CollectionRepository
from app.schemas.collection import CollectionCreate, CollectionUpdate

logger = structlog.get_logger(__name__)


class CollectionService:
    def __init__(self, collection_repo: CollectionRepository):
        self.collection_repo = collection_repo

    async def create_collection(self, user_id: uuid.UUID, collection_in: CollectionCreate) -> Collection:
        existing = await self.collection_repo.get_by_user_and_name(user_id, collection_in.name)
        if existing:
            raise ConflictException(f"Collection with name '{collection_in.name}' already exists")

        collection = Collection(
            user_id=user_id,
            name=collection_in.name,
            description=collection_in.description,
            color=collection_in.color or "#4F46E5",
        )
        collection = await self.collection_repo.create(collection)
        logger.info("Collection created", collection_id=str(collection.id), user_id=str(user_id))
        return collection

    async def list_collections(self, user_id: uuid.UUID) -> List[Collection]:
        return await self.collection_repo.list_by_user(user_id)

    async def get_collection(self, user_id: uuid.UUID, collection_id: uuid.UUID) -> Collection:
        collection = await self.collection_repo.get_by_id(collection_id)
        if not collection:
            raise NotFoundException("Collection", collection_id)
        if collection.user_id != user_id:
            raise ForbiddenException("You do not have permission to access this collection")
        return collection

    async def update_collection(
        self, user_id: uuid.UUID, collection_id: uuid.UUID, update_in: CollectionUpdate
    ) -> Collection:
        collection = await self.get_collection(user_id, collection_id)

        if update_in.name is not None and update_in.name != collection.name:
            existing = await self.collection_repo.get_by_user_and_name(user_id, update_in.name)
            if existing and existing.id != collection_id:
                raise ConflictException(f"Collection with name '{update_in.name}' already exists")
            collection.name = update_in.name

        if update_in.description is not None:
            collection.description = update_in.description

        if update_in.color is not None:
            collection.color = update_in.color

        updated = await self.collection_repo.update(collection)
        logger.info("Collection updated", collection_id=str(collection.id), user_id=str(user_id))
        return updated

    async def delete_collection(self, user_id: uuid.UUID, collection_id: uuid.UUID) -> None:
        collection = await self.get_collection(user_id, collection_id)
        await self.collection_repo.delete(collection)
        logger.info("Collection deleted", collection_id=str(collection_id), user_id=str(user_id))
