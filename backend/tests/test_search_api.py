import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_search_api_valid_query():
    """Verify POST /api/search with valid query returns 200 OK and 3 ranked matches."""
    payload = {
        "query": "I feel that time is passing too quickly and I am not achieving my goals"
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "query" in data
    assert data["query"] == payload["query"]
    assert "matches" in data
    assert "total_found" in data

    matches = data["matches"]
    assert len(matches) == 3
    assert data["total_found"] == 3

    quote_ids = set()
    prev_score = 1.0

    for match in matches:
        # Verify required keys in response structure
        assert "quote" in match
        assert "similarity_score" in match

        quote = match["quote"]
        assert "id" in quote
        assert "text" in quote
        assert "author" in quote
        assert bool(quote["text"])
        assert bool(quote["author"])

        score = match["similarity_score"]
        assert isinstance(score, float)
        assert -1.0 <= score <= 1.0

        # Verify descending order of similarity scores
        assert score <= prev_score + 1e-6
        prev_score = score

        # Verify uniqueness of returned quote IDs
        assert quote["id"] not in quote_ids
        quote_ids.add(quote["id"])


def test_search_api_empty_query_returns_400():
    """Verify POST /api/search with empty string returns HTTP 400."""
    response = client.post("/api/search", json={"query": ""})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "cannot be empty" in data["detail"]


def test_search_api_whitespace_query_returns_400():
    """Verify POST /api/search with whitespace string returns HTTP 400."""
    response = client.post("/api/search", json={"query": "     "})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "cannot be empty" in data["detail"]


def test_search_api_missing_query_field_returns_422():
    """Verify POST /api/search with missing body field returns HTTP 422 Unprocessable Entity."""
    response = client.post("/api/search", json={})
    assert response.status_code == 422


def test_search_api_spanish_query_real_dataset():
    """Verify semantic search with Spanish query against real 100-quote dataset."""
    payload = {
        "query": "Búsqueda de la sabiduría y el sentido de la vida"
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data["matches"]) == 3
    scores = [m["similarity_score"] for m in data["matches"]]
    assert scores == sorted(scores, reverse=True)
