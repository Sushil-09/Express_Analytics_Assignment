import io
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app
from app.services.ingestion import load_uploaded_file, load_file


def test_load_uploaded_file_txt():
    content = "FastAPI supports dependency injection and async/await."
    docs = load_uploaded_file(content=content, filename="guide.txt")
    assert len(docs) == 1
    assert docs[0].page_content == content
    assert docs[0].metadata["source"] == "guide.txt"


def test_load_uploaded_file_html():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>FastAPI Docs</title></head>
    <body>
        <nav><a href="/home">Home</a></nav>
        <h1>FastAPI Guide</h1>
        <p>FastAPI is very fast and easy to learn.</p>
        <script>console.log("ignore me");</script>
        <footer>Footer text</footer>
    </body>
    </html>
    """
    docs = load_uploaded_file(content=html_content, filename="guide.html")
    assert len(docs) == 1
    assert "FastAPI Guide" in docs[0].page_content
    assert "FastAPI is very fast and easy to learn." in docs[0].page_content
    # Scripts and nav should be stripped
    assert "console.log" not in docs[0].page_content
    assert "Home" not in docs[0].page_content
    assert "Footer text" not in docs[0].page_content


def test_api_ingest_txt_file():
    client = TestClient(app)
    file_bytes = b"This is a plain text guide on Python typing."
    response = client.post(
        "/ingest/file",
        files={"file": ("guide.txt", io.BytesIO(file_bytes), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["documents_processed"] == 1
    assert data["chunks_created"] >= 1


def test_api_ingest_html_file():
    client = TestClient(app)
    html_bytes = b"<html><body><h1>Title</h1><p>HTML document body content for testing.</p></body></html>"
    response = client.post(
        "/ingest/file",
        files={"file": ("page.html", io.BytesIO(html_bytes), "text/html")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["documents_processed"] == 1
    assert data["chunks_created"] >= 1


def test_api_ingest_unsupported_file():
    client = TestClient(app)
    pdf_bytes = b"%PDF-1.4 mock content"
    response = client.post(
        "/ingest/file",
        files={"file": ("document.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_api_ingest_empty_file():
    client = TestClient(app)
    empty_bytes = b"   "
    response = client.post(
        "/ingest/file",
        files={"file": ("empty.txt", io.BytesIO(empty_bytes), "text/plain")},
    )
    assert response.status_code == 400
    assert "no readable text content" in response.json()["detail"]

