import time
import uuid
from typing import Any, Dict, List
from pydantic import BaseModel
import structlog
from app.providers.embedding.base import BaseEmbeddingProvider
from app.providers.llm.base import BaseLLMProvider
from app.repositories.document_repository import DocumentRepository
from app.services.collection_service import CollectionService

logger = structlog.get_logger(__name__)


class Citation(BaseModel):
    document_id: uuid.UUID
    chunk_id: uuid.UUID
    page_number: int
    content_snippet: str
    similarity_score: float


class RAGResult(BaseModel):
    answer: str
    citations: List[Citation]
    retrieved_chunk_ids: List[uuid.UUID]
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    retrieval_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float


class RAGService:
    def __init__(
        self,
        document_repo: DocumentRepository,
        collection_service: CollectionService,
        embedding_provider: BaseEmbeddingProvider,
        llm_provider: BaseLLMProvider,
    ):
        self.document_repo = document_repo
        self.collection_service = collection_service
        self.embedding_provider = embedding_provider
        self.llm_provider = llm_provider

    async def semantic_search_debug(
        self, user_id: uuid.UUID, collection_id: uuid.UUID, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        # Authorize collection access
        await self.collection_service.get_collection(user_id, collection_id)

        query_vector = await self.embedding_provider.embed_query(query)
        results = await self.document_repo.semantic_search(collection_id, query_vector, top_k=top_k)

        search_results = []
        for chunk, distance in results:
            similarity = round(1.0 - distance, 4)
            search_results.append({
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "page_number": chunk.page_number,
                "content": chunk.content,
                "similarity_score": similarity,
                "metadata": chunk.metadata_json or {},
            })
        return search_results

    async def execute_rag_pipeline(
        self, user_id: uuid.UUID, collection_id: uuid.UUID, question: str, top_k: int = 5
    ) -> RAGResult:
        start_time = time.perf_counter()
        
        # 1. Authorize collection access
        collection = await self.collection_service.get_collection(user_id, collection_id)

        # 2. Semantic Search Retrieval
        retrieval_start = time.perf_counter()
        query_vector = await self.embedding_provider.embed_query(question)
        search_results = await self.document_repo.semantic_search(collection_id, query_vector, top_k=top_k)
        retrieval_latency = (time.perf_counter() - retrieval_start) * 1000

        # 3. Construct Context & Citations
        context_blocks = []
        citations = []
        retrieved_chunk_ids = []

        for chunk, distance in search_results:
            similarity = round(1.0 - distance, 4)
            retrieved_chunk_ids.append(chunk.id)
            context_blocks.append(f"[Page {chunk.page_number}]: {chunk.content}")
            citations.append(
                Citation(
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    page_number=chunk.page_number or 1,
                    content_snippet=chunk.content[:150] + "...",
                    similarity_score=similarity,
                )
            )

        context_str = "\n\n".join(context_blocks) if context_blocks else "No relevant documents found."

        # 4. Prompt Construction & LLM Generation
        system_prompt = (
            f"You are KnowIT AI, an intelligent assistant answering questions based on knowledge collection '{collection.name}'. "
            "Use ONLY the retrieved context below to answer accurately. If context is insufficient, state that clearly."
        )
        user_prompt = f"Retrieved Context:\n{context_str}\n\nUser Question:\n{question}"

        generation_start = time.perf_counter()
        llm_response = await self.llm_provider.generate(user_prompt, system_prompt=system_prompt)
        generation_latency = (time.perf_counter() - generation_start) * 1000

        total_latency = (time.perf_counter() - start_time) * 1000

        logger.info(
            "RAG pipeline executed",
            collection_id=str(collection_id),
            retrieved_chunks=len(search_results),
            retrieval_latency_ms=round(retrieval_latency, 2),
            generation_latency_ms=round(generation_latency, 2),
            total_latency_ms=round(total_latency, 2),
        )

        return RAGResult(
            answer=llm_response.content,
            citations=citations,
            retrieved_chunk_ids=retrieved_chunk_ids,
            model=llm_response.model,
            prompt_tokens=llm_response.prompt_tokens,
            completion_tokens=llm_response.completion_tokens,
            total_tokens=llm_response.total_tokens,
            retrieval_latency_ms=round(retrieval_latency, 2),
            generation_latency_ms=round(generation_latency, 2),
            total_latency_ms=round(total_latency, 2),
        )
