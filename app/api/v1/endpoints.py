from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.v1.schemas import (
    HealthCheck,
    LLMRequest,
    LLMResponse,
    DocumentCreate,
    DocumentResponse,
    DocumentSearchRequest,
    DocumentSearchResponse,
    DocumentSearchResult
)
from app.core.config import settings
from app.db.base import get_db
from app.services.llm_service import llm_service
from app.services.document_service import document_service
from app.core.logging_config import logger

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheck,
    tags=["Health"],
    summary="Check API Health",
    description="Returns the health status of the API service",
    responses={
        200: {
            "description": "API is healthy and running",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "environment": "development",
                        "version": "1.0.0"
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    Check API health status.

    Returns basic information about the API including:
    - Status: Current health status
    - Environment: Current environment (development/production)
    - Version: API version number
    """
    return HealthCheck(
        status="healthy",
        environment=settings.ENVIRONMENT,
        version=settings.APP_VERSION
    )


@router.get(
    "/health/ollama",
    tags=["Health"],
    summary="Check Ollama LLM Service Health",
    description="Verify that the Ollama LLM service is running and accessible",
    responses={
        200: {
            "description": "Ollama service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "host": "http://ollama:11434",
                        "model": "llama2",
                        "available_models": ["llama2", "tinyllama"]
                    }
                }
            }
        },
        503: {
            "description": "Ollama service is unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "status": "unhealthy",
                            "error": "Connection refused",
                            "host": "http://ollama:11434"
                        }
                    }
                }
            }
        }
    }
)
async def ollama_health_check():
    """
    Check Ollama service health.

    Verifies that:
    - Ollama service is running
    - The service is accessible
    - Models are available

    Returns connection information and available models.
    """
    health_status = await llm_service.check_health()
    if health_status["status"] != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
    return health_status


@router.post(
    "/llm/generate",
    response_model=LLMResponse,
    tags=["LLM"],
    summary="Generate Text with Local LLM",
    description="Generate text using the local Ollama LLM (llama2)",
    responses={
        200: {
            "description": "Text generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "response": "FastAPI is a modern, fast web framework for building APIs with Python.",
                        "model": "llama2"
                    }
                }
            }
        },
        500: {"description": "LLM generation failed"}
    }
)
async def generate_text(request: LLMRequest):
    """
    Generate text using the local LLM.

    **Parameters:**
    - **prompt**: The main prompt to send to the LLM (required)
    - **system_prompt**: Optional system prompt for context/instructions
    - **temperature**: Controls randomness (0.0 = deterministic, 2.0 = very random)
    - **max_tokens**: Maximum number of tokens to generate

    **Example Request:**
    ```json
    {
        "prompt": "Explain machine learning in simple terms",
        "system_prompt": "You are a helpful AI assistant",
        "temperature": 0.7,
        "max_tokens": 500
    }
    ```
    """
    try:
        response = await llm_service.generate(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return LLMResponse(
            response=response,
            model=settings.OLLAMA_MODEL
        )

    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating text: {str(e)}"
        )


@router.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Documents"],
    summary="Create Document with Embeddings",
    description="Create a new document and automatically generate vector embeddings for semantic search",
    responses={
        201: {
            "description": "Document created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "FastAPI Guide",
                        "content": "FastAPI is a modern web framework...",
                        "metadata": "category: Web Development",
                        "created_at": "2025-10-31T12:00:00",
                        "updated_at": "2025-10-31T12:00:00"
                    }
                }
            }
        },
        500: {"description": "Document creation failed"}
    }
)
async def create_document(
    document: DocumentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new document with automatic vector embeddings.

    The system will:
    1. Store the document in the database
    2. Automatically generate vector embeddings using sentence-transformers
    3. Store embeddings for later semantic search

    **Parameters:**
    - **title**: Document title (required, max 255 characters)
    - **content**: Document content (required)
    - **metadata**: Optional metadata as a string (e.g., "category: AI, level: beginner")
    """
    try:
        new_document = await document_service.create_document(
            db=db,
            title=document.title,
            content=document.content,
            metadata=document.metadata
        )
        return new_document

    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating document: {str(e)}"
        )


@router.get("/documents", response_model=List[DocumentResponse], tags=["Documents"])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all documents with pagination."""
    try:
        documents = await document_service.list_documents(db=db, skip=skip, limit=limit)
        return documents

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing documents: {str(e)}"
        )


@router.get("/documents/{document_id}", response_model=DocumentResponse, tags=["Documents"])
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a document by ID."""
    try:
        document = await document_service.get_document(db=db, document_id=document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found"
            )
        return document

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting document: {str(e)}"
        )


@router.post(
    "/documents/search",
    response_model=DocumentSearchResponse,
    tags=["Documents"],
    summary="Semantic Document Search",
    description="Search documents using semantic similarity based on vector embeddings",
    responses={
        200: {
            "description": "Search completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "query": "machine learning frameworks",
                        "results": [
                            {
                                "id": 1,
                                "title": "FastAPI Overview",
                                "content": "FastAPI is a framework...",
                                "metadata": "category: Web",
                                "similarity": 0.85
                            }
                        ],
                        "count": 1
                    }
                }
            }
        }
    }
)
async def search_documents(
    search_request: DocumentSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Search for similar documents using vector similarity.

    Uses pgvector's cosine similarity to find documents semantically similar to your query.

    **How it works:**
    1. Convert your query text to a vector embedding
    2. Calculate similarity with all document embeddings
    3. Return top N most similar documents with similarity scores

    **Parameters:**
    - **query**: Search query text (required)
    - **limit**: Number of results to return (1-50, default: 5)

    **Similarity Score:**
    - 1.0 = Identical
    - 0.8-1.0 = Very similar
    - 0.6-0.8 = Somewhat similar
    - < 0.6 = Less similar
    """
    try:
        results = await document_service.search_similar_documents(
            db=db,
            query=search_request.query,
            limit=search_request.limit
        )

        return DocumentSearchResponse(
            query=search_request.query,
            results=[DocumentSearchResult(**doc) for doc in results],
            count=len(results)
        )

    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}"
        )


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Documents"])
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a document."""
    try:
        deleted = await document_service.delete_document(db=db, document_id=document_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )
