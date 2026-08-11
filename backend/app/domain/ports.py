from typing import Protocol, List, Dict, Any, Optional
from app.domain.models import Quote, QuoteMatch


class QuoteRepositoryPort(Protocol):
    """Abstract port for accessing quote dataset records."""

    def get_all_quotes(self) -> List[Quote]:
        """Retrieves all available quotes in the repository."""
        ...

    def get_quote_by_id(self, quote_id: str) -> Optional[Quote]:
        """Retrieves a single quote by its unique identifier."""
        ...


class VectorStorePort(Protocol):
    """Abstract port for dense vector index storage and retrieval."""

    def index_quotes(self, quotes_with_vectors: List[Dict[str, Any]]) -> None:
        """Indexes quote records along with their pre-computed dense embedding vectors."""
        ...

    def search_similar(self, query_vector: List[float], top_k: int = 3) -> List[QuoteMatch]:
        """Searches index for top_k quotes matching the query vector via dense cosine similarity."""
        ...


class EmbedderPort(Protocol):
    """Abstract port for generating text dense embeddings."""

    def embed_text(self, text: str) -> List[float]:
        """Generates a dense vector embedding representation for input text."""
        ...

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates dense vector embeddings for a list of text inputs."""
        ...


class LLMProviderPort(Protocol):
    """Abstract port for decoupled LLM text generation."""

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generates text completion based on prompt and optional system instructions."""
        ...


class TokenizerPort(Protocol):
    """Abstract port for measuring text unit / token counts."""

    def count_units(self, text: str) -> int:
        """Calculates token or text-unit count for a given text string."""
        ...
