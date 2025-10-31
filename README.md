# Python FastAPI ML Demo

A production-ready FastAPI application with local LLM integration (Ollama), PostgreSQL with pgvector for semantic search, and Docker multi-environment setup.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Local LLM Integration**: Uses Ollama for running LLMs locally (llama2)
- **Vector Database**: PostgreSQL with pgvector extension for semantic search
- **Embedding Generation**: Sentence-transformers for creating document embeddings
- **Multi-Environment Setup**: Separate Docker configurations for development and production
- **Virtual Environment Support**: Full support for local development with venv
- **Health Checks**: Built-in health endpoints for all services
- **OpenAPI/Swagger Documentation**: Interactive API documentation with Swagger UI and ReDoc
- **Auto-generated Docs**: API documentation stays in sync with code
- **Testing Ready**: Pytest setup with coverage reporting

## Project Structure

```
.
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints.py      # API endpoints
│   │       └── schemas.py        # Pydantic models
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   └── logging_config.py   # Logging setup
│   ├── db/
│   │   ├── base.py              # Database session management
│   │   └── init_db.py           # Database initialization
│   ├── models/
│   │   └── document.py          # SQLAlchemy models
│   ├── services/
│   │   ├── llm_service.py       # LLM integration
│   │   ├── embedding_service.py # Embedding generation
│   │   └── document_service.py  # Document CRUD operations
│   └── main.py                  # FastAPI application
├── docker/
│   ├── Dockerfile               # Multi-stage Docker build
│   ├── docker-compose.yml       # Base compose configuration
│   ├── docker-compose.dev.yml   # Development overrides
│   └── docker-compose.prod.yml  # Production overrides
├── scripts/
│   ├── setup_ollama.sh          # Ollama model setup
│   ├── init_db.sh               # Database initialization
│   └── seed_data.py             # Sample data seeding
├── .env.example                 # Example environment variables
├── .env.development             # Development environment
├── .env.production              # Production environment
├── requirements.txt             # Python dependencies
└── Makefile                     # Convenient commands
```

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Python 3.11+ (for local development with venv)
- (Optional) NVIDIA GPU for better LLM performance
- (Optional) PostgreSQL 16+ with pgvector extension (for local development without Docker)

## Quick Start

Choose your preferred setup method:

### Option A: Docker (Recommended for Quick Start)

#### 1. Setup Environment Files

```bash
# Copy example environment file
cp .env.example .env.development
cp .env.example .env.production

# Edit environment files as needed
```

#### 2. Start Development Environment

```bash
# Using Make (recommended)
make dev

# Or using Docker Compose directly
cd docker
docker-compose --profile development up --build
```

#### 3. Initialize Ollama and Database

```bash
# Wait for services to start, then in another terminal:

# Pull Ollama models
make setup-ollama

# Initialize database
make init-db

# (Optional) Seed sample data
docker-compose -f docker/docker-compose.yml exec api-dev python scripts/seed_data.py
```

#### 4. Access the Application

- **Swagger UI (Interactive)**: http://localhost:8000/docs
- **ReDoc (Alternative)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/api/v1/health
- **Root Endpoint**: http://localhost:8000/

---

### Option B: Local Development with venv

For local development without Docker, using Python virtual environment:

#### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
# Install all dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
pip list
```

#### 3. Setup External Services

You need PostgreSQL with pgvector and Ollama running locally:

**Install PostgreSQL with pgvector:**

```bash
# macOS (using Homebrew)
brew install postgresql@16
brew install pgvector

# Ubuntu/Debian
sudo apt-get install postgresql-16 postgresql-16-pgvector

# Or use Docker for just the database:
docker run -d \
  --name postgres-pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=fastapi_ml_db \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

**Install and Run Ollama:**

```bash
# macOS
brew install ollama
ollama serve

# Linux
curl -fsSL https://ollama.com/install.sh | sh
ollama serve

# Or use Docker:
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  ollama/ollama:latest
```

**Pull Ollama Models:**

```bash
ollama pull llama2
# Or for a smaller model:
ollama pull tinyllama
```

#### 4. Configure Environment

```bash
# Copy and edit environment file
cp .env.example .env

# Edit .env and set:
# POSTGRES_SERVER=localhost
# POSTGRES_PORT=5432
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=postgres
# POSTGRES_DB=fastapi_ml_db
# OLLAMA_HOST=http://localhost:11434
# OLLAMA_MODEL=llama2
```

#### 5. Initialize Database

```bash
# Create database (if using local PostgreSQL)
createdb fastapi_ml_db

# Initialize tables and pgvector extension
python -m app.db.init_db
```

#### 6. Seed Sample Data (Optional)

```bash
python scripts/seed_data.py
```

#### 7. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or using Python directly
python -m app.main
```

#### 8. Access the Application

- **Swagger UI (Interactive)**: http://localhost:8000/docs
- **ReDoc (Alternative)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/api/v1/health
- **Root Endpoint**: http://localhost:8000/

#### 9. Deactivate Virtual Environment

When you're done working:

```bash
deactivate
```

## Available Make Commands

Run `make help` to see all available commands. Key commands:

### Virtual Environment Commands
```bash
make venv           # Create and setup virtual environment
make venv-activate  # Show activation command
make install        # Install dependencies in active venv
make install-dev    # Install dev dependencies in active venv
```

### Docker Commands
```bash
make dev            # Start development environment with Docker
make prod           # Start production environment with Docker
make down           # Stop all Docker containers
make clean          # Stop containers and remove volumes
make logs           # Show logs from all containers
make logs-api       # Show API logs only
make logs-db        # Show database logs only
make logs-ollama    # Show Ollama logs only
make ps             # Show running containers
make restart        # Restart all services
```

### Docker Service Management
```bash
make setup-ollama   # Pull Ollama model (Docker)
make init-db        # Initialize database (Docker)
make seed           # Seed database with sample data (Docker)
make shell-api      # Open shell in API container
make shell-db       # Open PostgreSQL shell
```

### Local Development Commands (venv)
```bash
make run-local      # Run app locally (requires active venv)
make init-db-local  # Initialize local database
make seed-local     # Seed local database
```

### Testing and Code Quality
```bash
make test           # Run tests
make test-cov       # Run tests with coverage
make format         # Format code with black
make format-check   # Check code formatting
make lint           # Lint code with flake8
make quality        # Run all quality checks
```

### Cleanup Commands
```bash
make clean-pyc      # Remove Python file artifacts
make clean-venv     # Remove virtual environment
make clean-all      # Clean everything (Docker + venv + pyc)
```

## API Documentation (OpenAPI/Swagger)

This project includes comprehensive **OpenAPI/Swagger** documentation built into FastAPI:

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API testing interface
  - Try endpoints directly in your browser
  - View request/response schemas
  - See example payloads
  - Download OpenAPI specification

- **ReDoc**: http://localhost:8000/redoc
  - Alternative documentation interface
  - Clean, responsive design
  - Better for reading documentation
  - Search functionality

- **OpenAPI JSON**: http://localhost:8000/openapi.json
  - Raw OpenAPI 3.0 specification
  - Import into Postman, Insomnia, etc.
  - Generate client libraries
  - CI/CD integration

### Features

✅ **Rich Documentation** - Detailed descriptions for every endpoint
✅ **Interactive Testing** - Test API endpoints directly from the browser
✅ **Request Examples** - See example requests and responses
✅ **Schema Validation** - Automatic validation with clear error messages
✅ **Organized by Tags** - Endpoints grouped by functionality (Health, LLM, Documents)
✅ **Multiple Status Codes** - Document success and error responses

## API Endpoints

### Health Checks

- `GET /api/v1/health` - API health status
- `GET /api/v1/health/ollama` - Ollama service health

### LLM Operations

- `POST /api/v1/llm/generate` - Generate text using local LLM

Example request:
```json
{
  "prompt": "Explain machine learning in simple terms",
  "system_prompt": "You are a helpful AI assistant",
  "temperature": 0.7,
  "max_tokens": 500
}
```

### Document Management

- `POST /api/v1/documents` - Create document with embeddings
- `GET /api/v1/documents` - List all documents
- `GET /api/v1/documents/{id}` - Get specific document
- `POST /api/v1/documents/search` - Semantic search
- `DELETE /api/v1/documents/{id}` - Delete document

Example document creation:
```json
{
  "title": "Introduction to AI",
  "content": "Artificial Intelligence is...",
  "metadata": "category: AI, level: beginner"
}
```

Example semantic search:
```json
{
  "query": "What is machine learning?",
  "limit": 5
}
```

### Using the API Documentation

1. **Start the application** (Docker or venv)
2. **Open Swagger UI**: http://localhost:8000/docs
3. **Explore endpoints** - Click to expand and see details
4. **Try it out** - Click "Try it out" button on any endpoint
5. **Execute** - Fill in parameters and click "Execute"
6. **View response** - See the actual API response

### Exporting OpenAPI Specification

```bash
# Download OpenAPI spec
curl http://localhost:8000/openapi.json -o openapi.json

# Import into Postman
# File → Import → Select openapi.json

# Generate client code
npm install -g @openapitools/openapi-generator-cli
openapi-generator-cli generate -i openapi.json -g python -o ./client
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | development |
| `DEBUG` | Enable debug mode | True |
| `POSTGRES_SERVER` | PostgreSQL host | localhost |
| `POSTGRES_PORT` | PostgreSQL port | 5432 |
| `POSTGRES_USER` | Database user | postgres |
| `POSTGRES_PASSWORD` | Database password | postgres |
| `POSTGRES_DB` | Database name | fastapi_ml_db |
| `OLLAMA_HOST` | Ollama service URL | http://localhost:11434 |
| `OLLAMA_MODEL` | LLM model to use | llama2 |
| `EMBEDDING_MODEL` | Embedding model | all-MiniLM-L6-v2 |

## Development

### Virtual Environment Management

**Creating a fresh virtual environment:**

```bash
# Remove old venv if exists
rm -rf venv

# Create new venv
python3.11 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Managing dependencies:**

```bash
# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# List installed packages
pip list

# Show package info
pip show package-name
```

**Virtual environment with different Python versions:**

```bash
# Using specific Python version
python3.10 -m venv venv310
python3.11 -m venv venv311
python3.12 -m venv venv312

# Activate specific version
source venv311/bin/activate
```

### Running Tests

```bash
# Activate venv first
source venv/bin/activate

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_specific.py -v
```

### Code Formatting

```bash
# Activate venv first
source venv/bin/activate

# Format all code
black app/ tests/

# Check without formatting
black app/ tests/ --check

# Format specific file
black app/main.py
```

### Linting

```bash
# Activate venv first
source venv/bin/activate

# Lint code
flake8 app/ tests/

# With specific config
flake8 app/ tests/ --max-line-length=100
```

### Development Workflow (with venv)

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Start external services (if not using Docker)
# Terminal 1: Start PostgreSQL (if local)
postgres -D /usr/local/var/postgres

# Terminal 2: Start Ollama
ollama serve

# 3. Run the application with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. In another terminal (with venv activated), run tests
pytest tests/ -v

# 5. Format and lint before committing
black app/ tests/
flake8 app/ tests/

# 6. When done
deactivate
```

## Production Deployment

```bash
# Start production environment
make prod

# Check logs
make logs

# Monitor containers
make ps
```

## Docker Configuration

### Development Mode
- Hot-reload enabled
- Debug logging
- Volume mounts for code changes
- Development dependencies included

### Production Mode
- Optimized build
- Multiple workers
- Resource limits
- Security hardening
- Non-root user

## GPU Support

If you have an NVIDIA GPU, uncomment the GPU configuration in `docker/docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

## Quick Testing

Once the application is running, test the endpoints:

### Health Check
```bash
curl http://localhost:8000/api/v1/health
# Response: {"status":"healthy","environment":"development","version":"1.0.0"}
```

### Create Document
```bash
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Programming",
    "content": "Python is a high-level programming language known for its simplicity.",
    "metadata": "category: Programming"
  }'
```

### Semantic Search
```bash
curl -X POST "http://localhost:8000/api/v1/documents/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "programming languages",
    "limit": 5
  }'
```

### Generate Text with LLM
```bash
curl -X POST "http://localhost:8000/api/v1/llm/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain FastAPI in one sentence",
    "temperature": 0.7
  }'
```

## Troubleshooting

### Port Already in Use
If port 8000, 5432, or 11434 is already in use:

Edit `docker/docker-compose.yml` and change the port:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Ollama service not starting
```bash
# Check Ollama logs
make logs-ollama

# Restart Ollama
docker-compose -f docker/docker-compose.yml restart ollama

# Try a smaller model if needed
docker exec -it fastapi-ollama ollama pull tinyllama
# Update .env files: OLLAMA_MODEL=tinyllama
```

### Database connection issues
```bash
# Check PostgreSQL logs
make logs-db

# Verify database is healthy
docker-compose -f docker/docker-compose.yml ps postgres

# Connect to database directly
make shell-db
# In psql: \dt (list tables), \dx (list extensions)
```

### No GPU Available
Comment out the GPU section in `docker/docker-compose.yml`:
```yaml
# Comment these lines in ollama service:
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: all
#           capabilities: [gpu]
```

### Models not downloading
```bash
# Check Ollama is running
docker ps | grep ollama

# Pull models manually
make setup-ollama

# Or directly
docker exec -it fastapi-ollama ollama pull llama2

# List available models
docker exec -it fastapi-ollama ollama list
```

### Virtual Environment Issues
```bash
# Remove and recreate
make clean-venv
make venv

# Or manually
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Technology Stack

- **FastAPI** - Modern web framework with automatic OpenAPI documentation
- **Ollama** - Local LLM runtime (llama2)
- **PostgreSQL 16** - Primary database
- **pgvector** - Vector similarity search extension
- **SQLAlchemy 2.0** - Async ORM
- **Pydantic** - Data validation and serialization
- **sentence-transformers** - Embedding generation (all-MiniLM-L6-v2)
- **Docker** - Containerization with multi-stage builds
- **uvicorn** - High-performance ASGI server
- **pytest** - Testing framework
- **black** - Code formatting
- **flake8** - Code linting

## Common Use Cases

### 1. Semantic Document Search System
- Store documents with automatic embeddings
- Search using natural language queries
- Get similarity scores for relevance ranking

### 2. Local LLM Integration
- Generate text without external API dependencies
- Run privately on your own infrastructure
- No API costs or rate limits

### 3. RAG (Retrieval Augmented Generation)
Combine vector search with LLM:
1. Search documents: `POST /documents/search`
2. Use results as context for LLM: `POST /llm/generate`

### 4. API Development Learning
- Study FastAPI best practices
- Learn async Python patterns
- Understand OpenAPI documentation
- Practice Docker containerization

## Development Tips

### Hot Reload (Development Mode)
Changes to code automatically reload the server:
- **Docker**: Volume mounted, auto-reloads
- **venv**: Run with `--reload` flag

### Debugging
```bash
# View API logs in real-time
make logs-api

# Check specific service
docker-compose -f docker/docker-compose.yml logs -f api-dev

# Access container for debugging
make shell-api
# Inside container:
python -c "from app.db.base import engine; print(engine)"
```

### Adding New Endpoints
1. Define schemas in `app/api/v1/schemas.py`
2. Add endpoint in `app/api/v1/endpoints.py`
3. Test in Swagger UI: http://localhost:8000/docs

### Database Migrations
For schema changes, use Alembic:
```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Performance Considerations

### Vector Search Performance
- **pgvector indexes** - Add HNSW or IVFFlat indexes for large datasets
- **Batch embeddings** - Use `generate_embeddings_batch()` for multiple documents
- **Limit results** - Keep search `limit` reasonable (5-50)

### LLM Performance
- **GPU acceleration** - Use NVIDIA GPU with Ollama for faster inference
- **Model size** - Smaller models (tinyllama) = faster, larger (llama2) = better quality
- **Temperature** - Lower values (0.1-0.3) = faster, more deterministic

### Production Optimization
- Use multiple uvicorn workers (configured in production Dockerfile)
- Enable PostgreSQL connection pooling
- Add Redis for caching frequent queries
- Use CDN for static assets

## Security Notes

### Production Checklist
- [ ] Change default passwords in `.env.production`
- [ ] Enable authentication/authorization
- [ ] Use HTTPS with proper certificates
- [ ] Configure CORS appropriately
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Regular security updates
- [ ] Backup database regularly

### Environment Variables
Never commit `.env` files with sensitive data:
```bash
# These are ignored by default
.env
.env.local
.env.*.local
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run `make format` and `make lint`
6. Submit a Pull Request

## Support

For issues, questions, or suggestions:
- **Issues**: Create a GitHub issue
- **Discussions**: Start a GitHub discussion
- **Documentation**: Check README and Swagger UI docs

## Changelog

### Version 1.0.0
- Initial release
- FastAPI with async support
- Ollama LLM integration
- PostgreSQL + pgvector
- Docker multi-environment setup
- Virtual environment support
- OpenAPI/Swagger documentation
- Sample data and scripts
