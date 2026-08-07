import sys
from pathlib import Path

from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from main import app


client = TestClient(app)


def test_polygon_context_endpoint():
    payload = {
        "polygon": [
            [78.36, 17.43],
            [78.38, 17.43],
            [78.38, 17.44],
            [78.36, 17.44],
        ]
    }

    response = client.post("/api/v1/ai-context/polygon", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert "context" in body
    assert "centroid" in body
    assert "detected_locality" in body
    ctx = body["context"]
    for key in ("core", "builder", "investor", "buyer", "scores"):
        assert key in ctx
    assert "property_summary" in ctx
    assert "buyer_recommendation" in ctx
