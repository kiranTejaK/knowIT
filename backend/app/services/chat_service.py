import uuid
from typing import List, Tuple
import structlog
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.chat import Chat
from app.models.message import Message, MessageRole
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import ChatCreate, ChatUpdate
from app.services.collection_service import CollectionService
from app.services.rag_service import RAGService

logger = structlog.get_logger(__name__)


class ChatService:
    def __init__(
        self,
        chat_repo: ChatRepository,
        collection_service: CollectionService,
        rag_service: RAGService,
    ):
        self.chat_repo = chat_repo
        self.collection_service = collection_service
        self.rag_service = rag_service

    async def create_chat(self, user_id: uuid.UUID, chat_in: ChatCreate) -> Chat:
        # Verify collection access
        collection = await self.collection_service.get_collection(user_id, chat_in.collection_id)

        chat = Chat(
            user_id=user_id,
            collection_id=collection.id,
            title=chat_in.title or f"Chat on {collection.name}",
            model="llama-3.3-70b-versatile",
        )
        chat = await self.chat_repo.create_chat(chat)
        logger.info("Chat created", chat_id=str(chat.id), user_id=str(user_id))
        return chat

    async def list_chats(self, user_id: uuid.UUID) -> List[Chat]:
        return await self.chat_repo.list_by_user(user_id)

    async def get_chat(self, user_id: uuid.UUID, chat_id: uuid.UUID) -> Chat:
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat:
            raise NotFoundException("Chat", chat_id)
        if chat.user_id != user_id:
            raise ForbiddenException("You do not have permission to access this chat")
        return chat

    async def rename_chat(self, user_id: uuid.UUID, chat_id: uuid.UUID, update_in: ChatUpdate) -> Chat:
        chat = await self.get_chat(user_id, chat_id)
        chat.title = update_in.title
        updated = await self.chat_repo.update_chat(chat)
        logger.info("Chat renamed", chat_id=str(chat.id), title=update_in.title)
        return updated

    async def delete_chat(self, user_id: uuid.UUID, chat_id: uuid.UUID) -> None:
        chat = await self.get_chat(user_id, chat_id)
        await self.chat_repo.delete_chat(chat)
        logger.info("Chat deleted", chat_id=str(chat_id))

    async def send_message(
        self, user_id: uuid.UUID, chat_id: uuid.UUID, content: str, top_k: int = 5
    ) -> Message:
        chat = await self.get_chat(user_id, chat_id)

        # 1. Store User Message
        user_msg = Message(
            chat_id=chat.id,
            role=MessageRole.USER,
            content=content,
            token_count=max(1, len(content) // 4),
        )
        await self.chat_repo.create_message(user_msg)

        # 2. Execute RAG Pipeline
        rag_result = await self.rag_service.execute_rag_pipeline(
            user_id=user_id,
            collection_id=chat.collection_id,
            question=content,
            top_k=top_k,
        )

        # Format citations to dict list
        citations_data = [
            {
                "document_id": str(c.document_id),
                "chunk_id": str(c.chunk_id),
                "page_number": c.page_number,
                "content_snippet": c.content_snippet,
                "similarity_score": c.similarity_score,
            }
            for c in rag_result.citations
        ]

        # 3. Store Assistant Response Message
        assistant_msg = Message(
            chat_id=chat.id,
            role=MessageRole.ASSISTANT,
            content=rag_result.answer,
            citations=citations_data,
            token_count=rag_result.completion_tokens,
            latency_ms=int(rag_result.total_latency_ms),
        )
        assistant_msg = await self.chat_repo.create_message(assistant_msg)
        logger.info("Assistant message generated", message_id=str(assistant_msg.id), chat_id=str(chat_id))
        return assistant_msg

    async def list_messages(
        self, user_id: uuid.UUID, chat_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> Tuple[List[Message], int]:
        await self.get_chat(user_id, chat_id)
        return await self.chat_repo.list_messages(chat_id, limit=limit, offset=offset)
