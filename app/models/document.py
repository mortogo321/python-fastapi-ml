from datetime import UTC, datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.db.base import Base

settings = get_settings()


class Document(Base):
    """Document model with vector embeddings.

    ``metadata`` is reserved on SQLAlchemy Declarative, so the mapped
    attribute is ``doc_metadata`` while the DB column stays ``metadata``.
    A ``metadata`` property alias is attached after class creation
    (assigning it inside the class body would trip SQLAlchemy's
    reserved-name check during mapper configuration).
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Any | None] = mapped_column(Vector(settings.VECTOR_DIMENSION), nullable=True)
    doc_metadata: Mapped[str | None] = mapped_column("metadata", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __init__(self, **kwargs: Any) -> None:
        # Accept ``metadata=`` for backwards compatibility.
        if "metadata" in kwargs:
            kwargs["doc_metadata"] = kwargs.pop("metadata")
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title='{self.title}')>"


def _get_metadata(self: Document) -> str | None:
    return self.doc_metadata


def _set_metadata(self: Document, value: str | None) -> None:
    self.doc_metadata = value


# Backwards-compatible alias (attached post-creation to avoid the
# Declarative reserved-name scan).
Document.metadata = property(_get_metadata, _set_metadata)  # type: ignore[assignment]
