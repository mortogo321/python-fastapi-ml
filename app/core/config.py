import json
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment-specific configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "FastAPI ML Demo"
    APP_VERSION: str = "1.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server (bind-all is intentional for containers; restrict via firewall/SG)
    HOST: str = "0.0.0.0"  # noqa: S104
    PORT: int = 8000

    # Database (local-dev defaults; override via environment in production)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"  # noqa: S105
    POSTGRES_DB: str = "fastapi_ml_db"

    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # Vector settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_DIMENSION: int = Field(default=384, ge=1, le=4096)

    # Request limits (DoS hardening)
    MAX_UPLOAD_BYTES: int = Field(default=10 * 1024 * 1024, ge=1024)
    MAX_PROMPT_CHARS: int = Field(default=10000, ge=100, le=100000)
    MAX_CONTENT_CHARS: int = Field(default=50000, ge=100, le=500000)
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=1000)

    # CORS — explicit origins in production. Wildcard "*" is allowed
    # for local demo use only and must NOT be combined with credentials.
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def database_url(self) -> str:
        """Construct sync database URL (psycopg2, used for init/migrations)."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def async_database_url(self) -> str:
        """Construct async database URL (asyncpg, used by the app)."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    """Cached settings factory (avoids re-parsing env per request)."""
    return Settings()


# Backwards-compatible module-level instance (existing imports keep working).
settings = get_settings()
