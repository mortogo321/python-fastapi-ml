from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging_config import logger


class LLMService:
    """Service for interacting with local LLM via Ollama.

    The client is created lazily so importing this module never
    requires a running Ollama service (CI-friendly).
    """

    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
        client: Any = None,
    ) -> None:
        settings = get_settings()
        self._host = host or settings.OLLAMA_HOST
        self.model = model or settings.OLLAMA_MODEL
        self._client = client

    def _get_client(self) -> Any:
        if self._client is None:
            import ollama

            self._client = ollama.Client(host=self._host)
        return self._client

    @property
    def host(self) -> str:
        return self._host

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """Generate text using the local LLM."""
        settings = get_settings()
        if len(prompt) > settings.MAX_PROMPT_CHARS:
            raise ValueError(
                f"Prompt too long: {len(prompt)} chars > {settings.MAX_PROMPT_CHARS} max."
            )
        return await self._generate_with_retry(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _generate_with_retry(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """LLM call with retry (input validation happens in generate())."""
        try:
            messages: list[dict[str, str]] = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response = self._get_client().chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    **({"num_predict": max_tokens} if max_tokens else {}),
                },
            )

            result: str = response["message"]["content"]
            return result

        except Exception as e:
            logger.error("Error generating LLM response: %s", e)
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def generate_embeddings(self, text: str) -> list[float]:
        """Generate embeddings for text using Ollama."""
        try:
            response = self._get_client().embeddings(
                model=self.model,
                prompt=text,
            )
            result: list[float] = response["embedding"]
            return result

        except Exception as e:
            logger.error("Error generating embeddings: %s", e)
            raise

    async def check_health(self) -> dict[str, Any]:
        """Check if Ollama service is healthy."""
        try:
            models = self._get_client().list()
            raw_models = models.get("models", []) if isinstance(models, dict) else []
            names: list[str] = []
            for m in raw_models:
                if isinstance(m, dict) and "name" in m:
                    names.append(str(m["name"]))
                else:
                    name = getattr(m, "model", None) or getattr(m, "name", None)
                    if name:
                        names.append(str(name))
            return {
                "status": "healthy",
                "host": self._host,
                "model": self.model,
                "available_models": names,
            }
        except Exception as e:
            logger.error("Ollama health check failed: %s", e)
            return {
                "status": "unhealthy",
                "error": str(e),
                "host": self._host,
            }


# Singleton instance — cheap to construct (no connection until first use).
llm_service = LLMService()
