# FastAPI + Local LLM + pgvector

A FastAPI service combining a local LLM (via Ollama) with PostgreSQL/pgvector for semantic document search — a small RAG (retrieval-augmented generation) building block.

## What's inside

- **LLM generation**: `POST /api/v1/llm/generate` — text generation via a local Ollama model, with health checks for both the API and the Ollama service
- **Document store with embeddings**: create/list/get/delete documents; embeddings are generated with `sentence-transformers` and stored in pgvector
- **Semantic search**: `POST /api/v1/documents/search` — natural-language query over stored documents using vector similarity
- Async SQLAlchemy models and DB session management
- Interactive OpenAPI docs (Swagger UI + ReDoc)
- Separate Docker Compose overrides for development and production, with optional GPU passthrough for Ollama

## Tech stack

- FastAPI, async SQLAlchemy
- PostgreSQL + pgvector
- Ollama (local LLM runtime)
- sentence-transformers for embeddings
- pytest, black, flake8
- Docker / Docker Compose, Make

## Quickstart

### Docker (recommended)

```bash
git clone git@github.com:mortogo321/python-fastapi-ml.git
cd python-fastapi-ml
cp .env.example .env.development
make dev

# in another terminal, once services are up:
make setup-ollama   # pulls the Ollama model
make init-db        # creates tables + pgvector extension
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/api/v1/health

### Local development (venv)

```bash
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # point POSTGRES_* and OLLAMA_HOST at your local services

python -m app.db.init_db
uvicorn app.main:app --reload --port 8000
```

Requires a locally running PostgreSQL with pgvector and Ollama (see Makefile targets `venv`, `install`, `run-local` for shortcuts).

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/llm/generate` | Generate text with the local LLM |
| POST | `/api/v1/documents` | Create a document (generates embeddings) |
| GET | `/api/v1/documents` | List documents |
| GET | `/api/v1/documents/{id}` | Get a document |
| POST | `/api/v1/documents/search` | Semantic search |
| DELETE | `/api/v1/documents/{id}` | Delete a document |
| GET | `/api/v1/health`, `/api/v1/health/ollama` | Health checks |

## Structure

```
app/
├── api/v1/           # Routes and Pydantic schemas
├── core/              # Config and logging
├── db/                # Session management, init
├── models/            # SQLAlchemy models (Document)
└── services/          # LLM, embedding, document services
docker/
├── docker-compose.yml       # Base config
├── docker-compose.dev.yml   # Development overrides
└── docker-compose.prod.yml  # Production overrides
scripts/               # Ollama setup, DB init, sample data seeding
```

## Common commands

```bash
make dev / make prod        # start an environment
make logs / make ps         # observability
make test / make lint       # pytest / flake8
make clean-all              # remove Docker + venv + build artifacts
```
