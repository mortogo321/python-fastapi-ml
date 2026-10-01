# FastAPI + Local LLM + pgvector

[![CI](https://github.com/mortogo321/python-fastapi-ml/actions/workflows/ci.yml/badge.svg)](https://github.com/mortogo321/python-fastapi-ml/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.142-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A FastAPI service combining a local LLM (via Ollama) with PostgreSQL/pgvector for semantic document search — a small RAG (retrieval-augmented generation) building block.

## What's inside

- **LLM generation**: `POST /api/v1/llm/generate` — text generation via a local Ollama model, with health checks for both the API and the Ollama service
- **Document store with embeddings**: create/list/get/delete documents; embeddings are generated with `sentence-transformers` and stored in pgvector
- **Semantic search**: `POST /api/v1/documents/search` — natural-language query over stored documents using vector similarity
- Async SQLAlchemy 2.1 models and DB session management
- Hardened middleware: global error handler (no internal leaks), per-IP rate limiting (health-exempt), structured request logging
- Input caps (prompt / content / upload limits) and paginated listing with validated bounds
- Interactive OpenAPI docs (Swagger UI + ReDoc)
- Separate Docker Compose overrides for development and production, with optional GPU passthrough for Ollama

## Tech stack

- FastAPI 0.142, uvicorn 0.54, pydantic 2.13
- PostgreSQL 17 + pgvector 0.8.6, SQLAlchemy 2.1 (asyncpg)
- Ollama 0.35 (llama3.2) local LLM runtime
- sentence-transformers 6.1 for embeddings, numpy 2.5
- pytest 9.1, ruff 0.16, mypy 2.3 (strict)
- Docker / Docker Compose, Make, GitHub Actions CI + Dependabot

## Quickstart

### Docker (recommended)

```bash
git clone git@github.com:mortogo321/python-fastapi-ml.git
cd python-fastapi-ml
cp .env.example .env.development
make up

# in another terminal, once services are up:
make setup-ollama   # pulls the Ollama model
make init-db        # creates tables + pgvector extension
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health checks: http://localhost:8000/api/health and http://localhost:8000/api/v1/health

### Local development (venv)

```bash
python3.13 -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env   # point POSTGRES_* and OLLAMA_HOST at your local services

python -m app.db.init_db
uvicorn app.main:app --reload --port 8000
```

Requires a locally running PostgreSQL with pgvector and Ollama.

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/llm/generate` | Generate text with the local LLM |
| POST | `/api/v1/documents` | Create a document (generates embeddings) |
| GET | `/api/v1/documents` | List documents (paginated, `skip`/`limit`) |
| GET | `/api/v1/documents/{id}` | Get a document |
| POST | `/api/v1/documents/search` | Semantic search |
| DELETE | `/api/v1/documents/{id}` | Delete a document |
| GET | `/api/health`, `/api/v1/health`, `/api/v1/health/ollama` | Health checks |

## Structure

```
app/
├── api/v1/           # Routes and Pydantic schemas
├── core/              # Config and logging
├── db/                # Session management, init
├── middleware/        # Error handler, rate limiter, request logger
├── models/            # SQLAlchemy models (Document)
└── services/          # LLM, embedding, document services
docker/
├── docker-compose.yml       # Base config
├── docker-compose.dev.yml   # Development overrides
└── docker-compose.prod.yml  # Production overrides
scripts/               # Ollama setup, DB init, sample data seeding
tests/                 # Mocked pytest suite (no infra required)
```

## Common commands

```bash
make check      # ruff + mypy strict + pytest
make test       # pytest only
make lint       # ruff lint + format check
make typecheck  # mypy strict
make build      # docker build
make up         # dev compose up
make prod       # prod compose up
make down       # compose down
```

## Notes

- Embeddings default to `all-MiniLM-L6-v2` (384 dims, `VECTOR_DIMENSION=384`). If you swap the model, update `VECTOR_DIMENSION` and recreate the table.
- Ollama defaults to `llama3.2` — override with `OLLAMA_MODEL` and pull via `make setup-ollama`.
- `CORS_ORIGINS="*"` is local-demo only and automatically disables credentials.
- Removed unused `langchain` dependencies from earlier revisions (no code imports them); the RAG loop here is Ollama + pgvector directly.
