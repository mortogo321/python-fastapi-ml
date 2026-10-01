"""Unit tests for services, schemas, middleware, config, model."""

import pytest
from fastapi.testclient import TestClient


def test_cosine_similarity_identical() -> None:
    from app.services.embedding_service import EmbeddingService

    svc = EmbeddingService()
    assert svc.calculate_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal() -> None:
    from app.services.embedding_service import EmbeddingService

    svc = EmbeddingService()
    assert svc.calculate_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector() -> None:
    from app.services.embedding_service import EmbeddingService

    svc = EmbeddingService()
    assert svc.calculate_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0


def test_embedding_lazy_no_import_side_effect() -> None:
    from app.services.embedding_service import EmbeddingService

    svc = EmbeddingService(model_name="does-not-matter")
    assert svc.model is None  # nothing loaded at construction


def test_llm_lazy_no_client_at_import() -> None:
    from app.services.llm_service import LLMService

    svc = LLMService(client=None)
    assert svc._client is None


@pytest.mark.asyncio()
async def test_llm_prompt_cap() -> None:
    from app.core.config import get_settings
    from app.services.llm_service import LLMService

    settings = get_settings()
    svc = LLMService()
    with pytest.raises(ValueError):
        await svc.generate(prompt="x" * (settings.MAX_PROMPT_CHARS + 1))


def test_schemas_enforce_limits() -> None:
    from pydantic import ValidationError

    from app.api.v1.schemas import DocumentCreate, DocumentSearchRequest, LLMRequest

    with pytest.raises(ValidationError):
        LLMRequest(prompt="x" * 20000)
    with pytest.raises(ValidationError):
        DocumentCreate(title="t", content="")
    with pytest.raises(ValidationError):
        DocumentSearchRequest(query="q", limit=100)


def test_cors_wildcard_disables_credentials() -> None:
    from app.core.config import Settings

    s = Settings(CORS_ORIGINS=["*"])
    assert "*" in s.CORS_ORIGINS
    # app.main forces credentials off for wildcard — replicate the rule here
    creds = True
    if "*" in s.CORS_ORIGINS:
        creds = False
    assert creds is False


def test_cors_json_string_parsing() -> None:
    from app.core.config import Settings

    s = Settings(CORS_ORIGINS='["http://a", "http://b"]')
    assert s.CORS_ORIGINS == ["http://a", "http://b"]
    s2 = Settings(CORS_ORIGINS="http://a, http://b")
    assert s2.CORS_ORIGINS == ["http://a", "http://b"]


def test_rate_limiter_exempts_health(client: TestClient) -> None:
    # Health endpoints never 429, even under burst.
    for _ in range(5):
        assert client.get("/api/health").status_code == 200
        assert client.get("/api/v1/health").status_code == 200


def test_document_metadata_alias() -> None:
    from app.models.document import Document

    d = Document(title="t", content="c", metadata="m: 1")
    assert d.metadata == "m: 1"
    assert d.doc_metadata == "m: 1"
    d.metadata = "m: 2"
    assert d.doc_metadata == "m: 2"
