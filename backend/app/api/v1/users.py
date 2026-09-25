from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, get_user_service
from app.models.user import User
from app.schemas.response import APIResponse
from app.schemas.user import UserProfileResponse, UserProfileUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=APIResponse[UserProfileResponse])
async def get_my_profile(current_user: Annotated[User, Depends(get_current_user)]):
    return APIResponse.ok(data=UserProfileResponse.model_validate(current_user))


@router.patch("/me", response_model=APIResponse[UserProfileResponse])
async def update_my_profile(
    update_in: UserProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    updated_user = await user_service.update_profile(current_user.id, update_in)
    return APIResponse.ok(data=UserProfileResponse.model_validate(updated_user))
