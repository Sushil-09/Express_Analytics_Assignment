from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app


def test_submit_feedback_thumbs_up():
    client = TestClient(app)
    response = client.post(
        "/feedback",
        json={
            "rating": "thumbs_up",
            "comment": "Accurate answer with good citations.",
            "question": "What is FastAPI?",
            "answer": "FastAPI is a modern web framework for Python.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Feedback submitted successfully"


def test_submit_feedback_thumbs_down():
    client = TestClient(app)
    response = client.post(
        "/feedback",
        json={
            "rating": "thumbs_down",
            "comment": "Sources were irrelevant.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_get_feedback_list():
    client = TestClient(app)
    response = client.get("/feedback")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

