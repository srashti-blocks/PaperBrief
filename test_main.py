from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Dummy valid response structure that passes Pydantic schema validation
MOCK_SUMMARY_RESPONSE = (
    '{"title_guess": "Attention Is All You Need", '
    '"summary": "presents the Transformer architecture.", '
    '"key_findings": ["Outperforms RNNs", "Faster training"], '
    '"methods": "Self-attention mechanisms", '
    '"limitations": "High GPU memory usage", '
    '"keywords": ["transformer", "attention", "nlp"]}'
)

VALID_TEXT = "A" * 250  # Meets the 200 character minimum requirement


def test_index_route():
    """Verify that the home page returns 200 OK and serves HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_create_summary_validation_too_short():
    """Verify that text under 200 characters triggers a validation error (422)."""
    response = client.post("/api/summaries", json={"text": "Too short"})
    assert response.status_code == 422


@patch("main.call_llm", return_value=MOCK_SUMMARY_RESPONSE)
def test_create_summary_success(mock_llm):
    """Verify successful summary generation and database persistence."""
    response = client.post("/api/summaries", json={"text": VALID_TEXT})
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["title_guess"] == "Attention Is All You Need"
    assert data["attempts"] == 1
    assert mock_llm.called


@patch("main.call_llm", return_value="Invalid JSON response")
def test_create_summary_retry_and_fail(mock_llm):
    """Verify that malformed LLM responses trigger retries up to MAX_ATTEMPTS and fail with 502."""
    response = client.post("/api/summaries", json={"text": VALID_TEXT})
    assert response.status_code == 502
    assert mock_llm.call_count == 3  # Tried 3 times before returning 502


def test_get_stats():
    """Verify the /api/stats endpoint returns expected keys."""
    response = client.get("/api/stats")
    assert response.status_code == 200

    data = response.json()
    assert "total" in data
    assert "ok" in data
    assert "failed" in data