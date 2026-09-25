from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.api.deps import get_auth_service
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.schemas.response import APIResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
@router.post("/signup", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.register(user_in)
    return APIResponse.ok(data=UserResponse.model_validate(user))


@router.post("/verify-email", response_model=APIResponse[dict])
async def verify_email(
    verify_in: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    await auth_service.verify_email(verify_in.token)
    return APIResponse.ok(data={"message": "Email verified successfully"})


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    login_in: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    access_token, refresh_token, user = await auth_service.login(login_in)
    return APIResponse.ok(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )
    )


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh(
    refresh_in: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    access_token, refresh_token, user = await auth_service.refresh_tokens(refresh_in.refresh_token)
    return APIResponse.ok(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )
    )


@router.post("/forgot-password", response_model=APIResponse[dict])
async def forgot_password(
    forgot_in: ForgotPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    await auth_service.forgot_password(forgot_in.email)
    return APIResponse.ok(data={"message": "Password reset email sent if account exists"})


@router.post("/reset-password", response_model=APIResponse[dict])
async def reset_password(
    reset_in: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    await auth_service.reset_password(reset_in.token, reset_in.new_password)
    return APIResponse.ok(data={"message": "Password reset successfully"})
