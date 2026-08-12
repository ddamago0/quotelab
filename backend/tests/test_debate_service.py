import pytest
from pathlib import Path

from app.domain.models import Quote, QuoteMatch, DebateResponse, DebateArgument
from app.infra.repositories.excel_quote_repository import ExcelQuoteRepository
from app.infra.embeddings.local_embedder import LocalSentenceTransformerEmbedder
from app.infra.vector_store.in_memory_vector_store import InMemoryVectorStore
from app.infra.llm.mock_llm_provider import MockLLMProvider
from app.services.semantic_retriever import SemanticRetriever
from app.services.debate_service import DebateService


def get_real_retriever() -> SemanticRetriever:
    project_root = Path(__file__).resolve().parent.parent.parent
    dataset_path = project_root / "data" / "citas.xlsx"
    repo = ExcelQuoteRepository(dataset_path)
    embedder = LocalSentenceTransformerEmbedder()
    store = InMemoryVectorStore()
    retriever = SemanticRetriever(quote_repository=repo, embedder=embedder, vector_store=store)
    retriever.initialize_index()
    return retriever


def test_debate_service_empty_topic_raises_error():
    retriever = get_real_retriever()
    provider = MockLLMProvider()
    service = DebateService(retriever=retriever, llm_provider=provider)

    with pytest.raises(ValueError, match="cannot be empty or whitespace"):
        service.generate_debate("")

    with pytest.raises(ValueError, match="cannot be empty or whitespace"):
        service.generate_debate("   ")


def test_debate_service_valid_topic_with_sufficient_evidence():
    """Verify DebateService generates a valid DebateResponse for a relevant topic."""
    retriever = get_real_retriever()
    provider = MockLLMProvider()
    # Use a low threshold to ensure real quotes match
    service = DebateService(retriever=retriever, llm_provider=provider, relevance_threshold=0.1)

    topic = "El paso del tiempo y el destino del ser humano"
    response = service.generate_debate(topic)

    assert isinstance(response, DebateResponse)
    assert response.topic == topic
    assert response.sufficient_evidence is True
    assert response.refusal_message is None
    assert len(response.evidence_quotes) > 0
    assert len(response.arguments) > 0

    # Verify structured argument attributes
    for arg in response.arguments:
        assert isinstance(arg, DebateArgument)
        assert bool(arg.position)
        assert bool(arg.argument_text)
        assert len(arg.evidence_quote_ids) > 0


def test_debate_service_insufficient_evidence_refusal():
    """Verify DebateService returns a controlled refusal when evidence similarity is below threshold."""
    retriever = get_real_retriever()
    provider = MockLLMProvider()
    # Set an impossibly high threshold (0.999) to force refusal
    service = DebateService(retriever=retriever, llm_provider=provider, relevance_threshold=0.999)

    topic = "Quantum electrodynamics in supercomputers"
    response = service.generate_debate(topic)

    assert isinstance(response, DebateResponse)
    assert response.topic == topic
    assert response.sufficient_evidence is False
    assert len(response.arguments) == 0
    assert len(response.evidence_quotes) == 0
    assert response.refusal_message is not None
    assert "Insufficient relevant evidence" in response.refusal_message


def test_mock_llm_provider_deterministic_behavior():
    """Verify MockLLMProvider runs deterministically and cites evidence quote IDs accurately."""
    provider = MockLLMProvider(provider_name="test-mock")
    q1 = Quote(id="q_100", text="La verdad nos hará libres.", author="Desconocido", tags=[])
    q2 = Quote(id="q_101", text="Pienso, luego existo.", author="René Descartes", tags=[])

    topic = "La búsqueda de la verdad"
    args = provider.generate_debate_arguments(topic=topic, evidence_quotes=[q1, q2])

    assert len(args) == 2
    assert args[0].evidence_quote_ids == ["q_100"]
    assert args[1].evidence_quote_ids == ["q_101"]
    assert "Desconocido" in args[0].argument_text
    assert "René Descartes" in args[1].argument_text


def test_debate_service_prevention_of_fabricated_evidence():
    """Verify DebateService only cites quote IDs that exist in the retrieved evidence_quotes."""
    retriever = get_real_retriever()
    provider = MockLLMProvider()
    service = DebateService(retriever=retriever, llm_provider=provider, relevance_threshold=0.1)

    topic = "La importancia de la imaginación"
    response = service.generate_debate(topic)

    valid_quote_ids = {q.id for q in response.evidence_quotes}

    for arg in response.arguments:
        for cited_id in arg.evidence_quote_ids:
            assert cited_id in valid_quote_ids, f"Fabricated quote ID cited: {cited_id}"
