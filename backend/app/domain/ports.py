from typing import Protocol, List, Dict, Any, Optional, runtime_checkable
from app.domain.models import Quote, QuoteMatch, DebateArgument


@runtime_checkable
class QuoteRepositoryPort(Protocol):
    """Abstract port for accessing quote dataset records."""

    def get_all_quotes(self) -> List[Quote]:
        """Retrieves all available quotes in the repository."""
        ...

    def get_quote_by_id(self, quote_id: str) -> Optional[Quote]:
        """Retrieves a single quote by its unique identifier."""
        ...


@runtime_checkable
class VectorStorePort(Protocol):
    """Abstract port for dense vector index storage and retrieval."""

    def index_quotes(self, quotes_with_vectors: List[Dict[str, Any]]) -> None:
        """Indexes quote records along with their pre-computed dense embedding vectors."""
        ...

    def search_similar(self, query_vector: List[float], top_k: int = 3) -> List[QuoteMatch]:
        """Searches index for top_k quotes matching the query vector via dense cosine similarity."""
        ...


@runtime_checkable
class EmbedderPort(Protocol):
    """Abstract port for generating text dense embeddings."""

    def embed_text(self, text: str) -> List[float]:
        """Generates a dense vector embedding representation for input text."""
        ...

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates dense vector embeddings for a list of text inputs."""
        ...


@runtime_checkable
class LLMProviderPort(Protocol):
    """
    Abstract provider-agnostic port for LLM generation.
    Decoupled from cloud APIs (OpenAI, Anthropic, Gemini) and specific vendor SDKs.
    Allows local inference engines (such as Ollama) or mock providers to be plugged in seamlessly.
    """

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generates text completion based on prompt and optional system instructions."""
        ...

    def generate_debate_arguments(
        self,
        topic: str,
        evidence_quotes: List[Quote]
    ) -> List[DebateArgument]:
        """Generates structured debate arguments grounded strictly in the provided evidence quotes."""
        ...


@runtime_checkable
class TokenizerPort(Protocol):
    """Abstract port for measuring text unit / token counts."""

    def count_units(self, text: str) -> int:
        """Calculates token or text-unit count for a given text string."""
        ...

