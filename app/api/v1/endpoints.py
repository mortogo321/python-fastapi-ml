from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    DocumentCreate,
    DocumentResponse,
    DocumentSearchRequest,
    DocumentSearchResponse,
    DocumentSearchResult,
    HealthCheck,
    LLMRequest,
    LLMResponse,
)
from app.core.config import get_settings
from app.core.logging_config import logger
from app.db.base import get_db
from app.services.document_service import document_service
from app.services.llm_service import llm_service

router = APIRouter()
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthCheck,
    tags=["Health"],
    summary="Check API Health",
    description="Returns the health status of the API service",
)
async def health_check() -> HealthCheck:
    """Check API health status."""
    return HealthCheck(
        status="healthy",
        environment=settings.ENVIRONMENT,
        version=settings.APP_VERSION,
    )


@router.get(
    "/health/ollama",
    tags=["Health"],
    summary="Check Ollama LLM Service Health",
    description="Verify that the Ollama LLM service is running and accessible",
)
async def ollama_health_check() -> dict[str, object]:
    """Check Ollama service health."""
    health_status = await llm_service.check_health()
    if health_status.get("status") != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status,
        )
    return health_status


@router.post(
    "/llm/generate",
    response_model=LLMResponse,
    tags=["LLM"],
    summary="Generate Text with Local LLM",
    description="Generate text using the local Ollama LLM",
)
async def generate_text(request: LLMRequest) -> LLMResponse:
    """Generate text using the local LLM.

    Prompt / token limits are enforced by the schema and service layer.
    Internal error details are logged but never leaked to the caller.
    """
    try:
        response = await llm_service.generate(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return LLMResponse(response=response, model=settings.OLLAMA_MODEL)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error("Error generating text: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating text",
        ) from e


@router.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Documents"],
    summary="Create Document with Embeddings",
    description="Create a new document and automatically generate vector embeddings",
)
async def create_document(
    document: DocumentCreate, db: Annotated[AsyncSession, Depends(get_db)]
) -> DocumentResponse:
    """Create a new document with automatic vector embeddings."""
    try:
        new_document = await document_service.create_document(
            db=db,
            title=document.title,
            content=document.content,
            metadata=document.metadata,
        )
        return DocumentResponse.model_validate(new_document)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error("Error creating document: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating document",
        ) from e


@router.get("/documents", response_model=list[DocumentResponse], tags=["Documents"])
async def list_documents(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0, le=10000)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[DocumentResponse]:
    """List all documents with pagination."""
    try:
        documents = await document_service.list_documents(db=db, skip=skip, limit=limit)
        return [DocumentResponse.model_validate(d) for d in documents]

    except Exception as e:
        logger.error("Error listing documents: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing documents",
        ) from e


@router.get("/documents/{document_id}", response_model=DocumentResponse, tags=["Documents"])
async def get_document(
    document_id: int, db: Annotated[AsyncSession, Depends(get_db)]
) -> DocumentResponse:
    """Get a document by ID."""
    try:
        document = await document_service.get_document(db=db, document_id=document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )
        return DocumentResponse.model_validate(document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting document: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting document",
        ) from e


@router.post(
    "/documents/search",
    response_model=DocumentSearchResponse,
    tags=["Documents"],
    summary="Semantic Document Search",
    description="Search documents using semantic similarity based on vector embeddings",
)
async def search_documents(
    search_request: DocumentSearchRequest, db: Annotated[AsyncSession, Depends(get_db)]
) -> DocumentSearchResponse:
    """Search for similar documents using vector similarity."""
    try:
        results = await document_service.search_similar_documents(
            db=db,
            query=search_request.query,
            limit=search_request.limit,
        )

        return DocumentSearchResponse(
            query=search_request.query,
            results=[DocumentSearchResult(**doc) for doc in results],
            count=len(results),
        )

    except Exception as e:
        logger.error("Error searching documents: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching documents",
        ) from e


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Documents"],
)
async def delete_document(document_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    """Delete a document."""
    try:
        deleted = await document_service.delete_document(db=db, document_id=document_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting document: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document",
        ) from e
