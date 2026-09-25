import uuid
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import security
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.db.session import get_async_db
from app.models.user import User
from app.providers.email.email_provider import EmailProvider
from app.providers.embedding.base import BaseEmbeddingProvider
from app.providers.embedding.mock_embedding import MockEmbeddingProvider
from app.providers.llm.base import BaseLLMProvider
from app.providers.llm.groq_provider import GroqLLMProvider
from app.providers.storage.s3 import S3StorageProvider
from app.repositories.chat_repository import ChatRepository
from app.repositories.collection_repository import CollectionRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.collection_service import CollectionService
from app.services.document_service import DocumentService
from app.services.rag_service import RAGService
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_user_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> UserRepository:
    return UserRepository(db)


def get_collection_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> CollectionRepository:
    return CollectionRepository(db)


def get_document_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> DocumentRepository:
    return DocumentRepository(db)


def get_chat_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> ChatRepository:
    return ChatRepository(db)


def get_email_provider() -> EmailProvider:
    return EmailProvider()


def get_storage_provider() -> S3StorageProvider:
    return S3StorageProvider()


def get_embedding_provider() -> BaseEmbeddingProvider:
    return MockEmbeddingProvider(dimension=384)


def get_llm_provider() -> BaseLLMProvider:
    return GroqLLMProvider(api_key=settings.GROQ_API_KEY)


def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    email_provider: Annotated[EmailProvider, Depends(get_email_provider)],
) -> AuthService:
    return AuthService(user_repo, email_provider)


def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repo)


def get_collection_service(
    collection_repo: Annotated[CollectionRepository, Depends(get_collection_repository)],
) -> CollectionService:
    return CollectionService(collection_repo)


def get_document_service(
    document_repo: Annotated[DocumentRepository, Depends(get_document_repository)],
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
    storage_provider: Annotated[S3StorageProvider, Depends(get_storage_provider)],
    embedding_provider: Annotated[BaseEmbeddingProvider, Depends(get_embedding_provider)],
) -> DocumentService:
    return DocumentService(document_repo, collection_service, storage_provider, embedding_provider)


def get_rag_service(
    document_repo: Annotated[DocumentRepository, Depends(get_document_repository)],
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
    embedding_provider: Annotated[BaseEmbeddingProvider, Depends(get_embedding_provider)],
    llm_provider: Annotated[BaseLLMProvider, Depends(get_llm_provider)],
) -> RAGService:
    return RAGService(document_repo, collection_service, embedding_provider, llm_provider)


def get_chat_service(
    chat_repo: Annotated[ChatRepository, Depends(get_chat_repository)],
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
    rag_service: Annotated[RAGService, Depends(get_rag_service)],
) -> ChatService:
    return ChatService(chat_repo, collection_service, rag_service)


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_exception = UnauthorizedException("Could not validate credentials")

    payload = security.decode_access_token(token)
    if not payload or "sub" not in payload:
        raise credentials_exception

    try:
        user_id = uuid.UUID(payload["sub"])
    except ValueError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise credentials_exception

    return user
