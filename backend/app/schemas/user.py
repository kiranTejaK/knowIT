import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool = Field(validation_alias="is_email_verified")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


UserResponse = UserProfileResponse


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
