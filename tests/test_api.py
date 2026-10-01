"""API endpoint tests (all external services mocked)."""

from unittest.mock import AsyncMock

import pytest


def test_root(client) -> None:
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["health"] == "/api/v1/health"


def test_health_v1(client) -> None:
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_health_alias(client) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_ollama_health_ok(client, mock_llm) -> None:
    r = client.get("/api/v1/health/ollama")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_ollama_health_down(client, mock_llm) -> None:
    mock_llm.check_health = AsyncMock(
        return_value={"status": "unhealthy", "error": "refused", "host": "http://x"}
    )
    r = client.get("/api/v1/health/ollama")
    assert r.status_code == 503


def test_llm_generate_ok(client, mock_llm) -> None:
    r = client.post("/api/v1/llm/generate", json={"prompt": "hello"})
    assert r.status_code == 200
    assert r.json()["response"] == "mocked response"


def test_llm_generate_validation(client, mock_llm) -> None:
    r = client.post("/api/v1/llm/generate", json={"prompt": ""})
    assert r.status_code == 422
    r = client.post("/api/v1/llm/generate", json={"prompt": "x", "temperature": 5})
    assert r.status_code == 422


def test_llm_generate_error_hidden(client, mock_llm) -> None:
    mock_llm.generate = AsyncMock(side_effect=RuntimeError("ollama exploded"))
    r = client.post("/api/v1/llm/generate", json={"prompt": "hi"})
    assert r.status_code == 500
    assert "ollama exploded" not in r.text


def test_create_document(client, mock_embeddings) -> None:
    r = client.post(
        "/api/v1/documents",
        json={"title": "T", "content": "C"},
    )
    assert r.status_code == 201
    assert r.json()["title"] == "Test Doc"


def test_create_document_validation(client, mock_embeddings) -> None:
    r = client.post("/api/v1/documents", json={"title": "", "content": "C"})
    assert r.status_code == 422
    r = client.post("/api/v1/documents", json={"title": "T", "content": ""})
    assert r.status_code == 422


def test_list_documents(client, mock_embeddings) -> None:
    r = client.get("/api/v1/documents")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_documents_pagination_validation(client, mock_embeddings) -> None:
    assert client.get("/api/v1/documents?limit=1000").status_code == 422
    assert client.get("/api/v1/documents?skip=-1").status_code == 422


def test_get_document(client, mock_embeddings) -> None:
    r = client.get("/api/v1/documents/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_get_document_404(client, mock_embeddings) -> None:
    mock_embeddings.get_document = AsyncMock(return_value=None)
    assert client.get("/api/v1/documents/999").status_code == 404


def test_search_documents(client, mock_embeddings) -> None:
    r = client.post("/api/v1/documents/search", json={"query": "hello"})
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 1
    assert body["results"][0]["similarity"] == pytest.approx(0.95)


def test_delete_document(client, mock_embeddings) -> None:
    r = client.delete("/api/v1/documents/1")
    assert r.status_code == 204


def test_delete_document_404(client, mock_embeddings) -> None:
    mock_embeddings.delete_document = AsyncMock(return_value=False)
    assert client.delete("/api/v1/documents/999").status_code == 404
