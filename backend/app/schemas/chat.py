import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatCreate(BaseModel):
    collection_id: uuid.UUID
    title: Optional[str] = Field(None, max_length=255)


class ChatUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class ChatResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    collection_id: uuid.UUID
    title: str
    model: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class MessageResponse(BaseModel):
    id: uuid.UUID
    chat_id: uuid.UUID
    role: str
    content: str
    citations: Optional[List[Dict[str, Any]]] = None
    token_count: int = 0
    latency_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedMessagesResponse(BaseModel):
    items: List[MessageResponse]
    total: int
    limit: int
    offset: int
