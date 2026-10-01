from collections.abc import Sequence
from typing import Any

from sqlalchemy import Row, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging_config import logger
from app.models.document import Document
from app.services.embedding_service import embedding_service


class DocumentService:
    """Service for managing documents with vector search."""

    async def create_document(
        self,
        db: AsyncSession,
        title: str,
        content: str,
        metadata: str | None = None,
    ) -> Document:
        """Create a new document with embeddings."""
        settings = get_settings()
        if len(content) > settings.MAX_CONTENT_CHARS:
            raise ValueError(
                f"Content too long: {len(content)} chars > {settings.MAX_CONTENT_CHARS} max."
            )
        try:
            embedding = embedding_service.generate_embedding(content)

            document = Document(
                title=title,
                content=content,
                embedding=embedding,
                metadata=metadata,
            )

            db.add(document)
            await db.commit()
            await db.refresh(document)

            logger.info("Created document: %s", document.id)
            return document

        except Exception as e:
            logger.error("Error creating document: %s", e)
            await db.rollback()
            raise

    async def get_document(self, db: AsyncSession, document_id: int) -> Document | None:
        """Get a document by ID."""
        try:
            result = await db.execute(select(Document).where(Document.id == document_id))
            value: Document | None = result.scalar_one_or_none()
            return value
        except Exception as e:
            logger.error("Error getting document: %s", e)
            raise

    async def list_documents(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[Document]:
        """List all documents with pagination."""
        try:
            result = await db.execute(
                select(Document).offset(skip).limit(limit).order_by(Document.created_at.desc())
            )
            values: Sequence[Document] = result.scalars().all()
            return values
        except Exception as e:
            logger.error("Error listing documents: %s", e)
            raise

    async def search_similar_documents(
        self, db: AsyncSession, query: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Search for similar documents using vector similarity."""
        try:
            query_embedding = embedding_service.generate_embedding(query)
            vector_literal = "[" + ",".join(str(float(x)) for x in query_embedding) + "]"

            sql = text("""
                SELECT
                    id,
                    title,
                    content,
                    metadata,
                    1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
                FROM documents
                ORDER BY embedding <=> CAST(:query_embedding AS vector)
                LIMIT :limit
            """)

            result = await db.execute(
                sql,
                {"query_embedding": vector_literal, "limit": limit},
            )

            documents: list[dict[str, Any]] = []
            row: Row[Any]
            for row in result:
                documents.append(
                    {
                        "id": row.id,
                        "title": row.title,
                        "content": row.content,
                        "metadata": row.metadata,
                        "similarity": float(row.similarity),
                    }
                )

            return documents

        except Exception as e:
            logger.error("Error searching documents: %s", e)
            raise

    async def delete_document(self, db: AsyncSession, document_id: int) -> bool:
        """Delete a document."""
        try:
            document = await self.get_document(db, document_id)
            if document:
                await db.delete(document)
                await db.commit()
                logger.info("Deleted document: %s", document_id)
                return True
            return False
        except Exception as e:
            logger.error("Error deleting document: %s", e)
            await db.rollback()
            raise


# Singleton instance
document_service = DocumentService()
