import numpy as np
from typing import List, Dict, Any
from app.domain.models import Quote, QuoteMatch
from app.domain.ports import VectorStorePort


class InMemoryVectorStore(VectorStorePort):
    """
    In-memory vector store implementation using NumPy for dense vector cosine similarity calculation.
    Implements VectorStorePort.
    """

    def __init__(self):
        self._quotes: List[Quote] = []
        self._vectors: Optional[np.ndarray] = None  # Shape (N, D)

    def index_quotes(self, quotes_with_vectors: List[Dict[str, Any]]) -> None:
        """
        Indexes quotes alongside their pre-computed dense embedding vectors.
        Payload format per item: {"quote": Quote, "vector": List[float]}
        """
        if not quotes_with_vectors:
            self._quotes = []
            self._vectors = None
            return

        quotes: List[Quote] = []
        vectors: List[List[float]] = []

        for item in quotes_with_vectors:
            if "quote" not in item or "vector" not in item:
                raise ValueError("Indexed item must contain 'quote' and 'vector' keys.")
            quotes.append(item["quote"])
            vectors.append(item["vector"])

        vec_array = np.array(vectors, dtype=np.float32)
        if vec_array.ndim != 2:
            raise ValueError("Indexed vectors must form a 2D array of shape (N, dimension).")

        self._quotes = quotes
        self._vectors = vec_array

    def search_similar(self, query_vector: List[float], top_k: int = 3) -> List[QuoteMatch]:
        """
        Searches indexed vectors using cosine similarity and returns top_k QuoteMatch results sorted descending.
        """
        if top_k <= 0:
            raise ValueError("top_k must be a positive integer > 0.")
        if not query_vector:
            raise ValueError("Query vector cannot be empty.")
        if self._vectors is None or len(self._quotes) == 0:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        if q_vec.ndim != 1 or q_vec.shape[0] != self._vectors.shape[1]:
            raise ValueError(
                f"Query vector dimension ({q_vec.shape[0] if q_vec.ndim == 1 else 'invalid'}) "
                f"does not match indexed vector dimension ({self._vectors.shape[1]})."
            )

        # Compute cosine similarity
        q_norm = np.linalg.norm(q_vec)
        v_norms = np.linalg.norm(self._vectors, axis=1)

        # Avoid division by zero
        denom = (v_norms * q_norm)
        denom[denom == 0] = 1e-10

        dots = np.dot(self._vectors, q_vec)
        similarities = dots / denom

        # Sort indices in descending order of similarity
        sorted_indices = np.argsort(-similarities)
        effective_top_k = min(top_k, len(self._quotes))
        top_indices = sorted_indices[:effective_top_k]

        matches: List[QuoteMatch] = []
        for idx in top_indices:
            score = float(similarities[idx])
            # Clamp cosine similarity score to valid [-1.0, 1.0] range due to floating point precision
            clamped_score = max(-1.0, min(1.0, score))
            matches.append(QuoteMatch(quote=self._quotes[idx], similarity_score=clamped_score))

        return matches
