import pytest
from app.infra.vector_store.in_memory_vector_store import InMemoryVectorStore
from app.domain.models import Quote


def test_vector_store_indexing_and_cosine_similarity_ordering():
    store = InMemoryVectorStore()

    q1 = Quote(id="q_1", text="Quote one", author="Author 1", tags=[])
    q2 = Quote(id="q_2", text="Quote two", author="Author 2", tags=[])
    q3 = Quote(id="q_3", text="Quote three", author="Author 3", tags=[])

    # Orthogonal / directional 3D vectors
    v1 = [1.0, 0.0, 0.0]  # Exact match for query [1.0, 0.0, 0.0]
    v2 = [0.7071, 0.7071, 0.0]  # Cosine similarity ~ 0.7071
    v3 = [0.0, 1.0, 0.0]  # Orthogonal, cosine similarity = 0.0

    payload = [
        {"quote": q1, "vector": v1},
        {"quote": q2, "vector": v2},
        {"quote": q3, "vector": v3},
    ]

    store.index_quotes(payload)

    # Search with query vector matching v1
    matches = store.search_similar(query_vector=[1.0, 0.0, 0.0], top_k=3)

    assert len(matches) == 3
    assert matches[0].quote.id == "q_1"
    assert pytest.approx(matches[0].similarity_score, 1e-3) == 1.0

    assert matches[1].quote.id == "q_2"
    assert pytest.approx(matches[1].similarity_score, 1e-3) == 0.7071

    assert matches[2].quote.id == "q_3"
    assert pytest.approx(matches[2].similarity_score, 1e-3) == 0.0

    # Verify descending ordering
    scores = [m.similarity_score for m in matches]
    assert scores == sorted(scores, reverse=True)


def test_vector_store_invalid_top_k_raises_error():
    store = InMemoryVectorStore()
    with pytest.raises(ValueError, match="top_k must be a positive integer"):
        store.search_similar(query_vector=[1.0, 0.0], top_k=0)

    with pytest.raises(ValueError, match="top_k must be a positive integer"):
        store.search_similar(query_vector=[1.0, 0.0], top_k=-5)


def test_vector_store_empty_query_vector_raises_error():
    store = InMemoryVectorStore()
    with pytest.raises(ValueError, match="Query vector cannot be empty"):
        store.search_similar(query_vector=[], top_k=3)
