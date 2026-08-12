from functools import lru_cache
from pathlib import Path
from fastapi import Depends

from app.config import settings
from app.domain.ports import LLMProviderPort
from app.infra.repositories.excel_quote_repository import ExcelQuoteRepository
from app.infra.embeddings.local_embedder import LocalSentenceTransformerEmbedder
from app.infra.vector_store.in_memory_vector_store import InMemoryVectorStore
from app.infra.llm.mock_llm_provider import MockLLMProvider
from app.services.semantic_retriever import SemanticRetriever
from app.services.debate_service import DebateService


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
    Cached via lru_cache to avoid reloading SentenceTransformer model or re-indexing on every HTTP request.
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


@lru_cache()
def get_llm_provider() -> LLMProviderPort:
    """
    Dependency provider for LLMProviderPort instance.
    Currently returns MockLLMProvider for deterministic development and testing.
    """
    return MockLLMProvider(provider_name="mock-dev-llm")


@lru_cache()
def get_debate_service(
    retriever: SemanticRetriever = Depends(get_semantic_retriever),
    llm_provider: LLMProviderPort = Depends(get_llm_provider)
) -> DebateService:
    """
    Dependency provider for DebateService singleton instance.
    Injects cached retriever and llm_provider dependencies.
    """
    return DebateService(
        retriever=retriever,
        llm_provider=llm_provider,
        relevance_threshold=settings.DEBATE_RELEVANCE_THRESHOLD,
        max_evidence_quotes=settings.DEBATE_EVIDENCE_TOP_K
    )
