from typing import List, Optional
from sentence_transformers import SentenceTransformer
from app.domain.ports import EmbedderPort
from app.config import settings


class LocalSentenceTransformerEmbedder(EmbedderPort):
    """
    Concrete implementation of EmbedderPort using local SentenceTransformers.
    Loads models locally without external API dependencies.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self._model = SentenceTransformer(self.model_name)

    def embed_text(self, text: str) -> List[float]:
        """Generates a dense vector embedding for a single text string."""
        if not text or not text.strip():
            raise ValueError("Input text for embedding cannot be empty or whitespace.")

        embedding = self._model.encode(text.strip(), convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates dense vector embeddings for a list of text inputs."""
        if not texts:
            return []

        cleaned_texts = [t.strip() for t in texts]
        if any(not t for t in cleaned_texts):
            raise ValueError("All texts in batch embedding input must be non-empty strings.")

        embeddings = self._model.encode(cleaned_texts, convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.tolist()
