from functools import lru_cache
from pathlib import Path

from app.config import settings
from app.infra.repositories.excel_quote_repository import ExcelQuoteRepository
from app.infra.embeddings.local_embedder import LocalSentenceTransformerEmbedder
from app.infra.vector_store.in_memory_vector_store import InMemoryVectorStore
from app.services.semantic_retriever import SemanticRetriever


def resolve_dataset_path() -> Path:
    """Resolves dataset file path, supporting both relative and absolute execution paths."""
    path = Path(settings.DATASET_PATH)
    if path.exists():
        return path
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    fallback_path = project_root / settings.DATASET_PATH
    if fallback_path.exists():
        return fallback_path
    return path


@lru_cache()
def get_semantic_retriever() -> SemanticRetriever:
    """
    Dependency provider for SemanticRetriever singleton instance.
    Waiver: Cached via lru_cache to avoid reloading SentenceTransformer model or re-indexing on every HTTP request.
    """
    dataset_path = resolve_dataset_path()
    quote_repository = ExcelQuoteRepository(dataset_path)
    embedder = LocalSentenceTransformerEmbedder(model_name=settings.EMBEDDING_MODEL_NAME)
    vector_store = InMemoryVectorStore()

    retriever = SemanticRetriever(
        quote_repository=quote_repository,
        embedder=embedder,
        vector_store=vector_store
    )
    retriever.initialize_index()
    return retriever
