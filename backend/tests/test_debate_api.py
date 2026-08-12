import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_debate_api_valid_topic_returns_200():
    """Verify POST /api/debate with valid topic returns HTTP 200 and structured response."""
    payload = {
        "topic": "El tiempo y el destino del ser humano",
        "min_evidence_score": 0.1
    }
    response = client.post("/api/debate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "topic" in data
    assert data["topic"] == payload["topic"]
    assert "sufficient_evidence" in data
    assert data["sufficient_evidence"] is True
    assert "arguments" in data
    assert "evidence_quotes" in data
    assert "refusal_message" in data
    assert data["refusal_message"] is None

    arguments = data["arguments"]
    evidence_quotes = data["evidence_quotes"]

    assert len(arguments) > 0
    assert len(evidence_quotes) > 0

    valid_quote_ids = {q["id"] for q in evidence_quotes}

    # Verify traceability: every cited quote ID in arguments must exist in evidence_quotes
    for arg in arguments:
        assert "position" in arg
        assert "argument_text" in arg
        assert "evidence_quote_ids" in arg
        assert bool(arg["position"])
        assert bool(arg["argument_text"])
        assert len(arg["evidence_quote_ids"]) > 0

        for cited_id in arg["evidence_quote_ids"]:
            assert cited_id in valid_quote_ids, f"Fabricated quote ID cited: {cited_id}"


def test_debate_api_empty_topic_returns_400():
    """Verify POST /api/debate with empty string returns HTTP 400."""
    response = client.post("/api/debate", json={"topic": ""})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "cannot be empty" in data["detail"]


def test_debate_api_whitespace_topic_returns_400():
    """Verify POST /api/debate with whitespace string returns HTTP 400."""
    response = client.post("/api/debate", json={"topic": "     "})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "cannot be empty" in data["detail"]


def test_debate_api_missing_topic_field_returns_422():
    """Verify POST /api/debate with missing required field returns HTTP 422 Unprocessable Entity."""
    response = client.post("/api/debate", json={})
    assert response.status_code == 422


def test_debate_api_invalid_min_score_returns_422():
    """Verify POST /api/debate with invalid min_evidence_score out of bounds returns HTTP 422."""
    response = client.post("/api/debate", json={"topic": "Test topic", "min_evidence_score": 5.0})
    assert response.status_code == 422


def test_debate_api_insufficient_evidence_controlled_response():
    """Verify POST /api/debate with high threshold returns HTTP 200 with controlled refusal response."""
    payload = {
        "topic": "Quantum computing in biological cells",
        "min_evidence_score": 0.999
    }
    response = client.post("/api/debate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["topic"] == payload["topic"]
    assert data["sufficient_evidence"] is False
    assert len(data["arguments"]) == 0
    assert len(data["evidence_quotes"]) == 0
    assert data["refusal_message"] is not None
    assert "Insufficient relevant evidence" in data["refusal_message"]
