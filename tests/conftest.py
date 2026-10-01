"""Shared fixtures: stub heavy deps, mock DB/services, test client."""

import sys
import types
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient


def _ensure_sentence_transformers_stub() -> None:
    if "sentence_transformers" not in sys.modules:
        try:
            import sentence_transformers  # noqa: F401
        except Exception:
            stub = types.ModuleType("sentence_transformers")

            class _SentenceTransformer:
                def __init__(self, *args: Any, **kwargs: Any) -> None:
                    raise RuntimeError("sentence-transformers not installed in test env")

                def encode(self, *args: Any, **kwargs: Any) -> Any:
                    raise RuntimeError("sentence-transformers not installed in test env")

            stub.SentenceTransformer = _SentenceTransformer  # type: ignore[attr-defined]
            sys.modules["sentence_transformers"] = stub


_ensure_sentence_transformers_stub()

from app.db.base import get_db  # noqa: E402
from app.main import app  # noqa: E402


class FakeDocument:
    def __init__(
        self,
        doc_id: int = 1,
        title: str = "Test Doc",
        content: str = "Test content",
        metadata: Any = "category: test",
    ) -> None:
        self.id = doc_id
        self.title = title
        self.content = content
        self.metadata = metadata
        self.doc_metadata = metadata
        now = datetime.now(UTC)
        self.created_at = now
        self.updated_at = now


class FakeSession:
    pass


@pytest.fixture()
def fake_doc() -> FakeDocument:
    return FakeDocument()


@pytest.fixture()
def client() -> TestClient:
    async def _override_get_db() -> Any:
        yield FakeSession()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def mock_embeddings(monkeypatch: pytest.MonkeyPatch) -> Any:
    from app.services import document_service as ds_mod
    from app.services import embedding_service as es_mod

    async def _noop(*args: Any, **kwargs: Any) -> Any:
        return None

    monkeypatch.setattr(
        es_mod.embedding_service, "generate_embedding", lambda text: [0.1, 0.2, 0.3]
    )
    monkeypatch.setattr(
        es_mod.embedding_service,
        "generate_embeddings_batch",
        lambda texts: [[0.1] * 3 for _ in texts],
    )
    monkeypatch.setattr(
        ds_mod.document_service,
        "create_document",
        AsyncMock(return_value=FakeDocument()),
    )
    monkeypatch.setattr(
        ds_mod.document_service,
        "get_document",
        AsyncMock(return_value=FakeDocument()),
    )
    monkeypatch.setattr(
        ds_mod.document_service,
        "list_documents",
        AsyncMock(return_value=[FakeDocument(), FakeDocument(doc_id=2, title="Second")]),
    )
    monkeypatch.setattr(
        ds_mod.document_service,
        "search_similar_documents",
        AsyncMock(
            return_value=[
                {
                    "id": 1,
                    "title": "Test Doc",
                    "content": "Test content",
                    "metadata": "category: test",
                    "similarity": 0.95,
                }
            ]
        ),
    )
    monkeypatch.setattr(ds_mod.document_service, "delete_document", AsyncMock(return_value=True))
    return ds_mod.document_service


@pytest.fixture()
def mock_llm(monkeypatch: pytest.MonkeyPatch) -> Any:
    from app.services import llm_service as llm_mod

    monkeypatch.setattr(llm_mod.llm_service, "generate", AsyncMock(return_value="mocked response"))
    monkeypatch.setattr(
        llm_mod.llm_service,
        "check_health",
        AsyncMock(
            return_value={
                "status": "healthy",
                "host": "http://localhost:11434",
                "model": "llama3.2",
                "available_models": ["llama3.2"],
            }
        ),
    )
    return llm_mod.llm_service
