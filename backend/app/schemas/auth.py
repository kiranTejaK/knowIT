from typing import Optional
from pydantic import BaseModel, EmailStr
from app.schemas.user import UserResponse


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


UserCreate = SignupRequest


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class VerifyEmailRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
