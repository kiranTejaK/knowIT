import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chunk import Chunk
from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        return result.scalars().first()

    async def list_by_collection(self, collection_id: uuid.UUID) -> List[Document]:
        result = await self.db.execute(
            select(Document).where(Document.collection_id == collection_id).order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_document(self, document: Document) -> Document:
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def update_document(self, document: Document) -> Document:
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete_document(self, document: Document) -> None:
        await self.db.delete(document)
        await self.db.commit()

    # Chunk operations
    async def create_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        self.db.add_all(chunks)
        await self.db.commit()
        return chunks

    async def delete_chunks_by_document(self, document_id: uuid.UUID) -> None:
        result = await self.db.execute(select(Chunk).where(Chunk.document_id == document_id))
        chunks = result.scalars().all()
        for c in chunks:
            await self.db.delete(c)
        await self.db.commit()

    async def semantic_search(
        self, collection_id: uuid.UUID, query_vector: List[float], top_k: int = 5
    ) -> List[Tuple[Chunk, float]]:
        """PGVector Semantic Similarity Search by Cosine Distance."""
        stmt = (
            select(Chunk, Chunk.embedding.cosine_distance(query_vector).label("distance"))
            .where(Chunk.collection_id == collection_id, Chunk.embedding.is_not(None))
            .order_by("distance")
            .limit(top_k)
        )
        result = await self.db.execute(stmt)
        return [(row.Chunk, float(row.distance)) for row in result.all()]
