from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Health Check
class HealthCheck(BaseModel):
    status: str
    environment: str
    version: str


# LLM
class LLMRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to send to the LLM")
    system_prompt: Optional[str] = Field(None, description="System prompt for context")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum tokens to generate")


class LLMResponse(BaseModel):
    response: str
    model: str


# Documents
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    metadata: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    metadata: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(5, ge=1, le=50, description="Number of results to return")


class DocumentSearchResult(BaseModel):
    id: int
    title: str
    content: str
    metadata: Optional[str]
    similarity: float


class DocumentSearchResponse(BaseModel):
    query: str
    results: List[DocumentSearchResult]
    count: int
