import uuid
from typing import Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Chat(Base):
    __tablename__ = "chats"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), default="New Chat", nullable=False)
    model: Mapped[str] = mapped_column(String(100), default="llama-3.3-70b-versatile", nullable=False)

    user = relationship("User", backref="chats")
    collection = relationship("Collection", backref="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
