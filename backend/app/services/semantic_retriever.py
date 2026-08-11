from typing import List, Optional
from app.domain.models import QuoteMatch
from app.domain.ports import QuoteRepositoryPort, EmbedderPort, VectorStorePort
from app.config import settings


class SemanticRetriever:
    """
    Service responsible for purely semantic quote retrieval using dense vector embeddings.
    Strictly isolated from keyword, lexical, or hybrid search.
    Depends only on abstract Ports (QuoteRepositoryPort, EmbedderPort, VectorStorePort).
    """

    def __init__(
        self,
        quote_repository: QuoteRepositoryPort,
        embedder: EmbedderPort,
        vector_store: VectorStorePort,
    ):
        self.quote_repository = quote_repository
        self.embedder = embedder
        self.vector_store = vector_store
        self._is_indexed = False

    def initialize_index(self) -> None:
        """Loads all quotes from repository, computes embeddings, and populates the vector store."""

        quotes = self.quote_repository.get_all_quotes()
        if not quotes:
            self.vector_store.index_quotes([])
            self._is_indexed = True
            return

        texts = [q.text for q in quotes]
        vectors = self.embedder.embed_batch(texts)

        payload = [
            {"quote": quote, "vector": vector}
            for quote, vector in zip(quotes, vectors)
        ]
        self.vector_store.index_quotes(payload)
        self._is_indexed = True

    def search(self, query: str, top_k: Optional[int] = None) -> List[QuoteMatch]:
        """
        Executes pure semantic search for a natural-language query against indexed quote embeddings.
        Returns top_k QuoteMatch objects sorted by similarity score descending.
        """
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty or whitespace.")

        k = top_k if top_k is not None else settings.DEFAULT_TOP_K
        if k <= 0:
            raise ValueError("top_k must be a positive integer > 0.")

        if not self._is_indexed:
            self.initialize_index()

        query_vector = self.embedder.embed_text(query.strip())
        return self.vector_store.search_similar(query_vector, top_k=k)
