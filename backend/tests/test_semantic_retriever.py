import pytest
from pathlib import Path

from app.domain.models import Quote, QuoteMatch
from app.infra.repositories.excel_quote_repository import ExcelQuoteRepository
from app.infra.embeddings.local_embedder import LocalSentenceTransformerEmbedder
from app.infra.vector_store.in_memory_vector_store import InMemoryVectorStore
from app.services.semantic_retriever import SemanticRetriever


def test_semantic_retriever_empty_query_raises_error():
    project_root = Path(__file__).resolve().parent.parent.parent
    dataset_path = project_root / "data" / "citas.xlsx"

    repo = ExcelQuoteRepository(dataset_path)
    embedder = LocalSentenceTransformerEmbedder()
    store = InMemoryVectorStore()
    retriever = SemanticRetriever(quote_repository=repo, embedder=embedder, vector_store=store)

    with pytest.raises(ValueError, match="cannot be empty or whitespace"):
        retriever.search("")

    with pytest.raises(ValueError, match="cannot be empty or whitespace"):
        retriever.search("   ")


def test_semantic_retriever_invalid_top_k_raises_error():
    project_root = Path(__file__).resolve().parent.parent.parent
    dataset_path = project_root / "data" / "citas.xlsx"

    repo = ExcelQuoteRepository(dataset_path)
    embedder = LocalSentenceTransformerEmbedder()
    store = InMemoryVectorStore()
    retriever = SemanticRetriever(quote_repository=repo, embedder=embedder, vector_store=store)

    with pytest.raises(ValueError, match="top_k must be a positive integer"):
        retriever.search("Siento que el tiempo vuela", top_k=0)


def test_semantic_retriever_real_dataset_invariants():
    """
    Semantic test using the real 100-quote dataset and multilingual SentenceTransformer model.
    Validates structural invariants without relying on hardcoded quote rankings.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    dataset_path = project_root / "data" / "citas.xlsx"

    repo = ExcelQuoteRepository(dataset_path)
    embedder = LocalSentenceTransformerEmbedder(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    store = InMemoryVectorStore()

    retriever = SemanticRetriever(quote_repository=repo, embedder=embedder, vector_store=store)
    retriever.initialize_index()

    query = "Siento que el tiempo pasa muy rápido y no logro mis metas"
    top_k = 3

    results = retriever.search(query, top_k=top_k)

    # 1. Exactly top_k results
    assert len(results) == top_k

    quote_ids = set()
    prev_score = 1.0

    for match in results:
        assert isinstance(match, QuoteMatch)
        assert isinstance(match.quote, Quote)

        # 2. Check complete result contract (quote ID, text, author, score)
        assert bool(match.quote.id)
        assert bool(match.quote.text)
        assert bool(match.quote.author)
        assert isinstance(match.similarity_score, float)

        # 3. Check similarity range [-1.0, 1.0]
        assert -1.0 <= match.similarity_score <= 1.0

        # 4. Check descending similarity order
        assert match.similarity_score <= prev_score + 1e-6
        prev_score = match.similarity_score

        # 5. Check no duplicate quote IDs
        assert match.quote.id not in quote_ids
        quote_ids.add(match.quote.id)
