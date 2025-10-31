from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import logger
from app.api.v1.endpoints import router as api_router
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application with enhanced OpenAPI documentation
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## FastAPI ML Demo with Local LLM and Vector Database

    This API provides:

    * **Local LLM Integration**: Generate text using Ollama (llama2)
    * **Vector Search**: Store and search documents using semantic similarity
    * **PostgreSQL + pgvector**: Efficient vector storage and retrieval
    * **Automatic Embeddings**: Generate embeddings for documents automatically

    ### Features

    - 🤖 Local LLM text generation
    - 🔍 Semantic document search
    - 📝 Document management with CRUD operations
    - 💾 Vector embeddings storage
    - 🏥 Health check endpoints

    ### Quick Start

    1. Check health: `GET /api/v1/health`
    2. Create a document: `POST /api/v1/documents`
    3. Search documents: `POST /api/v1/documents/search`
    4. Generate text: `POST /api/v1/llm/generate`
    """,
    summary="FastAPI ML Demo API",
    version=settings.APP_VERSION,
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "https://example.com/support",
        "email": "support@example.com",
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
            "description": "Document management with automatic vector embeddings and semantic search",
        },
    ],
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",  # OpenAPI schema
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """
    ## Root Endpoint

    Returns basic API information and links to documentation.

    **Available Documentation:**
    - Swagger UI: `/docs`
    - ReDoc: `/redoc`
    - OpenAPI JSON: `/openapi.json`
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "health": "/api/v1/health",
        "api_version": "v1"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
