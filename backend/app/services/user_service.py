import uuid
import structlog
from app.core.exceptions import NotFoundException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserProfileUpdate

logger = structlog.get_logger(__name__)


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_profile(self, user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user

    async def update_profile(self, user_id: uuid.UUID, update_in: UserProfileUpdate) -> User:
        user = await self.get_profile(user_id)
        if update_in.full_name is not None:
            user.full_name = update_in.full_name
        updated = await self.user_repo.update(user)
        logger.info("User profile updated", user_id=str(user_id))
        return updated
