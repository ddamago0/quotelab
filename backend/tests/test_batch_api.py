import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_post_batch_default_processes_all_dataset_quotes():
    """Verify POST /api/batch with default payload processes all 100 quotes from dataset."""
    response = client.post("/api/batch", json={})
    assert response.status_code == 200

    data = response.json()
    assert "total_items_processed" in data
    assert data["total_items_processed"] == 100
    assert "total_units_consumed" in data
    assert data["total_units_consumed"] > 0
    assert "total_batches_created" in data
    assert data["total_batches_created"] > 0
    assert "max_units_per_request" in data
    assert data["max_units_per_request"] == 500
    assert "batches" in data
    assert isinstance(data["batches"], list)
    assert len(data["batches"]) == data["total_batches_created"]
    assert "failed_items" in data


def test_post_batch_specific_quote_ids():
    """Verify POST /api/batch with specific quote_ids packs requested quotes."""
    payload = {
        "quote_ids": ["q_1", "q_2", "q_3"]
    }
    response = client.post("/api/batch", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["total_items_processed"] == 3
    assert data["total_batches_created"] > 0


def test_post_batch_custom_max_units():
    """Verify POST /api/batch with custom max_units_per_batch override."""
    payload = {
        "quote_ids": ["q_1", "q_2"],
        "max_units_per_batch": 10
    }
    response = client.post("/api/batch", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["max_units_per_request"] == 10


def test_post_batch_invalid_max_units_returns_422():
    """Verify POST /api/batch with negative max_units_per_batch returns HTTP 422."""
    payload = {
        "max_units_per_batch": -10
    }
    response = client.post("/api/batch", json=payload)
    assert response.status_code == 422


def test_post_batch_non_existent_quote_id_returns_400():
    """Verify POST /api/batch with invalid quote ID returns HTTP 400."""
    payload = {
        "quote_ids": ["fake_quote_id_999"]
    }
    response = client.post("/api/batch", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not found in repository" in data["detail"]
