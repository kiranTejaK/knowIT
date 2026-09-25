import uuid
from typing import List
from fastapi import BackgroundTasks
import structlog
from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.loaders.chunker import chunk_text_pages
from app.loaders.text_extractors import TextExtractor
from app.models.chunk import Chunk
from app.models.document import Document, DocumentStatus
from app.providers.embedding.base import BaseEmbeddingProvider
from app.providers.storage.s3 import S3StorageProvider
from app.repositories.document_repository import DocumentRepository
from app.services.collection_service import CollectionService
from app.utils.file_validation import validate_document_file

logger = structlog.get_logger(__name__)


class DocumentService:
    def __init__(
        self,
        document_repo: DocumentRepository,
        collection_service: CollectionService,
        storage_provider: S3StorageProvider,
        embedding_provider: BaseEmbeddingProvider,
    ):
        self.document_repo = document_repo
        self.collection_service = collection_service
        self.storage_provider = storage_provider
        self.embedding_provider = embedding_provider

    async def upload_document(
        self,
        user_id: uuid.UUID,
        collection_id: uuid.UUID,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        background_tasks: BackgroundTasks,
    ) -> Document:
        ext, validated_content_type = validate_document_file(filename, content_type, len(file_bytes))
        collection = await self.collection_service.get_collection(user_id, collection_id)

        document_id = uuid.uuid4()
        storage_key = f"documents/{user_id}/{collection_id}/{document_id}_{filename}"

        doc = Document(
            id=document_id,
            collection_id=collection.id,
            title=filename,
            original_filename=filename,
            extension=ext,
            mime_type=validated_content_type,
            file_size=len(file_bytes),
            storage_key=storage_key,
            storage_provider="S3",
            status=DocumentStatus.UPLOADING,
            progress=10,
            current_step="Uploading to S3",
        )
        doc = await self.document_repo.create_document(doc)

        import io
        s3_success = self.storage_provider.upload(io.BytesIO(file_bytes), storage_key, content_type=validated_content_type)
        if not s3_success:
            doc.status = DocumentStatus.FAILED
            doc.error_message = "S3 storage upload failed"
            await self.document_repo.update_document(doc)
            raise ValidationException("Failed to store file in object storage")

        doc.status = DocumentStatus.PROCESSING
        doc.progress = 20
        doc.current_step = "Queued for Processing"
        await self.document_repo.update_document(doc)

        background_tasks.add_task(self.process_document_background, doc.id, file_bytes)
        logger.info("Document upload initiated", document_id=str(doc.id), collection_id=str(collection_id))
        return doc

    async def process_document_background(self, document_id: uuid.UUID, file_bytes: bytes) -> None:
        doc = await self.document_repo.get_by_id(document_id)
        if not doc:
            return

        try:
            # Step 1: Text Extraction
            doc.status = DocumentStatus.PROCESSING
            doc.progress = 30
            doc.current_step = "Extracting Text"
            await self.document_repo.update_document(doc)

            pages, total_pages = TextExtractor.extract_text(file_bytes, doc.extension)

            # Step 2: Chunking Document
            doc.progress = 55
            doc.current_step = "Chunking Document"
            doc.total_pages = total_pages
            await self.document_repo.update_document(doc)

            extracted_chunks = chunk_text_pages(pages)
            chunk_texts = [ec.content for ec in extracted_chunks]

            # Step 3: Generating Embeddings
            doc.progress = 80
            doc.current_step = "Generating Embeddings"
            await self.document_repo.update_document(doc)

            embeddings = []
            if chunk_texts:
                embeddings = await self.embedding_provider.embed_texts(chunk_texts)

            db_chunks = [
                Chunk(
                    document_id=doc.id,
                    collection_id=doc.collection_id,
                    content=ec.content,
                    chunk_index=ec.chunk_index,
                    page_number=ec.page_number,
                    token_count=ec.token_count,
                    embedding=embeddings[i] if i < len(embeddings) else None,
                    metadata_json={"source_page": ec.page_number, "filename": doc.original_filename},
                )
                for i, ec in enumerate(extracted_chunks)
            ]

            if db_chunks:
                await self.document_repo.create_chunks(db_chunks)

            # Step 4: Complete Processing
            doc.status = DocumentStatus.READY
            doc.progress = 100
            doc.current_step = "Ready"
            doc.total_chunks = len(db_chunks)
            await self.document_repo.update_document(doc)

            logger.info("Document processed successfully", document_id=str(doc.id), total_chunks=len(db_chunks))

        except Exception as exc:
            logger.exception("Document processing failed", document_id=str(doc.id), error=str(exc))
            doc.status = DocumentStatus.FAILED
            doc.progress = 0
            doc.current_step = "Error"
            doc.error_message = str(exc)
            await self.document_repo.update_document(doc)

    async def get_document(self, user_id: uuid.UUID, document_id: uuid.UUID) -> Document:
        doc = await self.document_repo.get_by_id(document_id)
        if not doc:
            raise NotFoundException("Document", document_id)
        await self.collection_service.get_collection(user_id, doc.collection_id)
        return doc

    async def get_document_status(self, user_id: uuid.UUID, document_id: uuid.UUID) -> Document:
        return await self.get_document(user_id, document_id)

    async def list_documents(self, user_id: uuid.UUID, collection_id: uuid.UUID) -> List[Document]:
        await self.collection_service.get_collection(user_id, collection_id)
        return await self.document_repo.list_by_collection(collection_id)

    async def delete_document(self, user_id: uuid.UUID, document_id: uuid.UUID) -> None:
        doc = await self.get_document(user_id, document_id)
        self.storage_provider.delete(doc.storage_key)
        await self.document_repo.delete_chunks_by_document(doc.id)
        await self.document_repo.delete_document(doc)
        logger.info("Document deleted successfully", document_id=str(document_id))

    async def retry_processing(
        self, user_id: uuid.UUID, document_id: uuid.UUID, background_tasks: BackgroundTasks
    ) -> Document:
        doc = await self.get_document(user_id, document_id)
        if doc.status != DocumentStatus.FAILED:
            raise ValidationException("Only FAILED documents can be retried")

        await self.document_repo.delete_chunks_by_document(doc.id)
        
        doc.status = DocumentStatus.PROCESSING
        doc.progress = 10
        doc.current_step = "Retrying Processing"
        doc.error_message = None
        await self.document_repo.update_document(doc)

        logger.info("Document processing retry initiated", document_id=str(document_id))
        return doc
