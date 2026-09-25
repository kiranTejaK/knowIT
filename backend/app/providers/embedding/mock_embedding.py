import hashlib
import math
from typing import List
from app.providers.embedding.base import BaseEmbeddingProvider


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """Deterministic, zero-dependency 384-dimensional embedding provider for local dev & testing."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def _generate_vector(self, text: str) -> List[float]:
        # Hash text to seed float values
        vector = []
        for i in range(self.dimension):
            seed = f"{text}_{i}".encode("utf-8")
            val = int(hashlib.sha256(seed).hexdigest(), 16) % 10000 / 5000.0 - 1.0
            vector.append(val)

        # L2 Normalize vector
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]
        return vector

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self._generate_vector(t) for t in texts]

    async def embed_query(self, text: str) -> List[float]:
        return self._generate_vector(text)
