from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class BaseLLMProvider(ABC):
    """Abstract interface for swappable LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generates a text completion response from an LLM model."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verifies connection and availability of the LLM provider API."""
        pass
