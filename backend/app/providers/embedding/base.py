from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingProvider(ABC):
    """Abstract interface for swappable embedding model providers."""

    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of text strings."""
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generates an embedding vector for a single search query."""
        pass
