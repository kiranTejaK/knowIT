import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    color: Optional[str] = Field(default="#4F46E5", max_length=50)


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=50)


class CollectionResponse(CollectionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
