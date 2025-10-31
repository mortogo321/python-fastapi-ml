from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from pgvector.sqlalchemy import Vector
from app.db.base import Base
from app.core.config import settings


class Document(Base):
    """Document model with vector embeddings."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"
