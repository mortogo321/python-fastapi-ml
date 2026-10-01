from typing import Any

import numpy as np

from app.core.config import get_settings
from app.core.logging_config import logger


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers.

    The heavy model is loaded lazily on first use so importing this
    module (e.g. in CI without torch weights cached) never has side effects.
    """

    def __init__(self, model_name: str | None = None) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.model: Any = None

    def _ensure_model(self) -> Any:
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}")
                raise
        return self.model

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        try:
            model = self._ensure_model()
            embedding = model.encode(text, convert_to_numpy=True)
            result: list[float] = embedding.tolist()
            return result
        except Exception as e:
            logger.error("Error generating embedding: %s", e)
            raise

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        try:
            model = self._ensure_model()
            embeddings = model.encode(texts, convert_to_numpy=True)
            result: list[list[float]] = embeddings.tolist()
            return result
        except Exception as e:
            logger.error("Error generating batch embeddings: %s", e)
            raise

    def calculate_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            dot_product = float(np.dot(vec1, vec2))
            norm1 = float(np.linalg.norm(vec1))
            norm2 = float(np.linalg.norm(vec2))
            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.error("Error calculating similarity: %s", e)
            raise


# Singleton instance — cheap to construct (no model loaded until first use).
embedding_service = EmbeddingService()
