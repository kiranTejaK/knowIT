import pytest
from app.providers.embedding.mock_embedding import MockEmbeddingProvider
from app.loaders.chunker import chunk_text_pages


@pytest.mark.asyncio
async def test_mock_embedding_provider():
    provider = MockEmbeddingProvider(dimension=384)
    vector = await provider.embed_query("What is KnowIT RAG?")
    assert len(vector) == 384
    # Check L2 normalization
    norm = sum(x * x for x in vector)
    assert abs(norm - 1.0) < 1e-4


def test_chunking_utility():
    pages = [(1, "KnowIT is a production-inspired RAG application built with FastAPI and React.")]
    chunks = chunk_text_pages(pages, chunk_size=50, chunk_overlap=10)
    assert len(chunks) > 0
    assert chunks[0].page_number == 1
    assert chunks[0].token_count > 0
