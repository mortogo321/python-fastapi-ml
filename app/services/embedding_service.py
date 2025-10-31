from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.core.config import settings
from app.core.logging_config import logger


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers."""

    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the embedding model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            raise


# Singleton instance
embedding_service = EmbeddingService()
