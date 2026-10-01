from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Health check
class HealthCheck(BaseModel):
    status: str
    environment: str
    version: str


class OllamaHealthCheck(BaseModel):
    status: str
    host: str
    model: str | None = None
    available_models: list[str] | None = None
    error: str | None = None


# LLM
class LLMRequest(BaseModel):
    prompt: str = Field(
        ..., min_length=1, max_length=10000, description="The prompt to send to the LLM"
    )
    system_prompt: str | None = Field(
        default=None, max_length=5000, description="System prompt for context"
    )
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: int | None = Field(
        default=None, ge=1, le=4096, description="Maximum tokens to generate"
    )


class LLMResponse(BaseModel):
    response: str
    model: str


# Documents
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, max_length=50000)
    metadata: str | None = Field(default=None, max_length=5000)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    metadata: str | None = None
    created_at: datetime
    updated_at: datetime


class DocumentSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000, description="Search query")
    limit: int = Field(5, ge=1, le=50, description="Number of results to return")


class DocumentSearchResult(BaseModel):
    id: int
    title: str
    content: str
    metadata: str | None = None
    similarity: float


class DocumentSearchResponse(BaseModel):
    query: str
    results: list[DocumentSearchResult]
    count: int
