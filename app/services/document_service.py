from typing import List, Optional, Dict, Any
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.services.embedding_service import embedding_service
from app.core.logging_config import logger


class DocumentService:
    """Service for managing documents with vector search."""

    async def create_document(
        self,
        db: AsyncSession,
        title: str,
        content: str,
        metadata: Optional[str] = None
    ) -> Document:
        """Create a new document with embeddings."""
        try:
            # Generate embedding
            embedding = embedding_service.generate_embedding(content)

            # Create document
            document = Document(
                title=title,
                content=content,
                embedding=embedding,
                metadata=metadata
            )

            db.add(document)
            await db.commit()
            await db.refresh(document)

            logger.info(f"Created document: {document.id}")
            return document

        except Exception as e:
            logger.error(f"Error creating document: {e}")
            await db.rollback()
            raise

    async def get_document(self, db: AsyncSession, document_id: int) -> Optional[Document]:
        """Get a document by ID."""
        try:
            result = await db.execute(
                select(Document).where(Document.id == document_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            raise

    async def list_documents(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """List all documents with pagination."""
        try:
            result = await db.execute(
                select(Document)
                .offset(skip)
                .limit(limit)
                .order_by(Document.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise

    async def search_similar_documents(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity."""
        try:
            # Generate embedding for query
            query_embedding = embedding_service.generate_embedding(query)

            # Perform vector similarity search
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
                {
                    "query_embedding": str(query_embedding),
                    "limit": limit
                }
            )

            documents = []
            for row in result:
                documents.append({
                    "id": row.id,
                    "title": row.title,
                    "content": row.content,
                    "metadata": row.metadata,
                    "similarity": float(row.similarity)
                })

            return documents

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    async def delete_document(self, db: AsyncSession, document_id: int) -> bool:
        """Delete a document."""
        try:
            document = await self.get_document(db, document_id)
            if document:
                await db.delete(document)
                await db.commit()
                logger.info(f"Deleted document: {document_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            await db.rollback()
            raise


# Singleton instance
document_service = DocumentService()
