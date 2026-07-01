import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture(scope="module")
def client():
    # Using the 'with' statement ensures the lifespan (startup/shutdown) events are triggered,
    # which initializes the RAGChain.
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    """Test if the API starts and initializes the RAG chain correctly."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_factual_query(client):
    """Test a factual query to ensure accurate retrieval and formatting."""
    payload = {"query": "What is the exit load for Birla Sun Life Cash Plus?"}
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    
    answer = response.json()["answer"]
    
    # Verify keywords
    assert "exit load" in answer.lower()
    
    # Verify sentence count limitation (rough approximation based on periods)
    # We expect max 3 sentences for the response, plus a potential period in the citation/URL.
    sentences = [s for s in answer.split('.') if len(s.strip()) > 3]
    assert len(sentences) <= 5, "Response is too long, violating the 3-sentence constraint."

def test_refusal_query(client):
    """Test an advisory query to verify the refusal engine kicks in."""
    payload = {"query": "Is Birla Sun Life Large Cap a good investment?"}
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    
    answer = response.json()["answer"]
    
    # Verify refusal strings as dictated by prompt/intent logic
    assert "I can only provide factual information" in answer
    assert "SEBI-registered financial advisor" in answer
    assert "https://www.amfiindia.com/investor-corner/knowledge-center.html" in answer
