from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import router as api_router
from app.api.v1.schemas import HealthCheck
from app.core.config import get_settings
from app.core.logging_config import logger
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown events."""
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Environment: %s", settings.ENVIRONMENT)

    # Database is initialized via `make init-db` / `python -m app.db.init_db`.
    # Never fail startup when the DB is not reachable (orchestrators retry).
    yield

    logger.info("Shutting down application")


# Create FastAPI application with enhanced OpenAPI documentation
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## FastAPI ML Demo with Local LLM and Vector Database

    This API provides:

    * **Local LLM Integration**: Generate text using Ollama
    * **Vector Search**: Store and search documents using semantic similarity
    * **PostgreSQL + pgvector**: Efficient vector storage and retrieval
    * **Automatic Embeddings**: Generate embeddings for documents automatically

    ### Features

    - Local LLM text generation
    - Semantic document search
    - Document management with CRUD operations
    - Vector embeddings storage
    - Health check endpoints
    """,
    summary="FastAPI ML Demo API",
    contact={
        "name": "API Support",
        "url": "https://github.com/mortogo321/python-fastapi-ml",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Health",
            "description": "Health check endpoints for monitoring service status",
        },
        {
            "name": "LLM",
            "description": "Local LLM operations using Ollama for text generation",
        },
        {
            "name": "Documents",
            "description": "Document management with vector embeddings and semantic search",
        },
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# NOTE: wildcard origins cannot be combined with credentials — keep
# allow_credentials=False while allowing all origins for local demo use.
# Set explicit origins via reverse proxy in production.
_cors_origins = settings.CORS_ORIGINS
_cors_credentials = True
if "*" in _cors_origins:
    _cors_credentials = False
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_cors_credentials,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
# Rate limit is enforced from settings at request time via app.state;
# default 60/min keeps the middleware stateless at import time.
app.add_middleware(RateLimiterMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/api/health", response_model=HealthCheck, tags=["Health"])
async def api_health() -> HealthCheck:
    """Top-level health alias (without version prefix, for Docker/CI probes)."""
    return HealthCheck(
        status="healthy",
        environment=settings.ENVIRONMENT,
        version=settings.APP_VERSION,
    )


@app.get("/", tags=["Root"])
async def root() -> dict[str, object]:
    """Root endpoint with API information and documentation links."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "health": "/api/v1/health",
        "api_version": "v1",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
