import ollama
from typing import Optional, Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.core.logging_config import logger


class LLMService:
    """Service for interacting with local LLM via Ollama."""

    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_HOST)
        self.model = settings.OLLAMA_MODEL

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text using the local LLM."""
        try:
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    **({"num_predict": max_tokens} if max_tokens else {})
                }
            )

            return response["message"]["content"]

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text using Ollama."""
        try:
            response = self.client.embeddings(
                model=self.model,
                prompt=text
            )
            return response["embedding"]

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    async def check_health(self) -> Dict[str, Any]:
        """Check if Ollama service is healthy."""
        try:
            # Try to list available models
            models = self.client.list()
            return {
                "status": "healthy",
                "host": settings.OLLAMA_HOST,
                "model": self.model,
                "available_models": [m["name"] for m in models.get("models", [])]
            }
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "host": settings.OLLAMA_HOST
            }


# Singleton instance
llm_service = LLMService()
