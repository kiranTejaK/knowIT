import os
from typing import Optional
import httpx
import structlog
from app.core.config import settings
from app.providers.llm.base import BaseLLMProvider, LLMResponse

logger = structlog.get_logger(__name__)


class GroqLLMProvider(BaseLLMProvider):
    """Groq LLM provider implementation."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or getattr(settings, "GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY", "")
        self.model = model or getattr(settings, "GROQ_MODEL", "openai/gpt-oss-20b")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        if not self.api_key:
            logger.warning("GROQ_API_KEY not configured, returning mock response")
            return LLMResponse(
                content=f"Based on the provided context: {prompt[:100]}...",
                model=self.model,
                prompt_tokens=50,
                completion_tokens=30,
                total_tokens=80,
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "KnowIT/1.0",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(self.api_url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                choice = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                return LLMResponse(
                    content=choice,
                    model=self.model,
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                )
        except Exception as exc:
            logger.error("Error communicating with Groq API", error=str(exc))
            raise exc

    async def health_check(self) -> bool:
        return bool(self.api_key)
