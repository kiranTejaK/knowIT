import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: uuid.UUID
    collection_id: uuid.UUID
    title: str
    original_filename: str
    extension: str
    mime_type: str
    file_size: int
    storage_key: str
    storage_provider: str
    status: str
    current_step: Optional[str] = None
    progress: int = 0
    total_pages: int = 0
    total_chunks: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentStatusResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    progress: int
    current_step: Optional[str] = None
    total_chunks: int = 0
    total_pages: int = 0
    error_message: Optional[str] = None
