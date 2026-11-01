from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.web_search import (
    perform_web_search,
    _search_tavily,
    _search_serper,
    _search_duckduckgo,
)
from app.graph.nodes.web_search import web_search_node


def test_tavily_search_success():
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "results": [
            {
                "title": "FastAPI Docs",
                "url": "https://fastapi.tiangolo.com",
                "content": "FastAPI is a modern web framework.",
            }
        ]
    }

    with patch("requests.post", return_value=mock_response):
        docs = _search_tavily("FastAPI", api_key="dummy_key")
        assert len(docs) == 1
        assert docs[0].page_content == "FastAPI is a modern web framework."
        assert docs[0].metadata["source"] == "https://fastapi.tiangolo.com"
        assert docs[0].metadata["source_type"] == "web_search"


def test_serper_search_success():
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "organic": [
            {
                "title": "PyTorch Tutorial",
                "link": "https://pytorch.org/tutorials",
                "snippet": "Learn PyTorch basics and neural networks.",
            }
        ]
    }

    with patch("requests.post", return_value=mock_response):
        docs = _search_serper("PyTorch", api_key="dummy_key")
        assert len(docs) == 1
        assert "Learn PyTorch basics" in docs[0].page_content
        assert docs[0].metadata["source"] == "https://pytorch.org/tutorials"


def test_web_search_fallback_graceful_on_network_error():
    with patch("requests.post", side_effect=Exception("Connection refused")):
        docs = perform_web_search("Any query")
        assert isinstance(docs, list)
        assert len(docs) == 0


def test_web_search_node_updates_state():
    mock_doc = MagicMock(page_content="Answer from web", metadata={"source": "https://example.com"})
    with patch("app.graph.nodes.web_search.perform_web_search", return_value=[mock_doc]):
        state = {
            "original_question": "What is LangGraph?",
            "query": "What is LangGraph?",
            "relevant_documents": [],
        }
        update = web_search_node(state)
        assert len(update["relevant_documents"]) == 1
        assert update["search_source"] == "web_search"


def test_web_search_node_empty():
    with patch("app.graph.nodes.web_search.perform_web_search", return_value=[]):
        state = {
            "original_question": "Obscure question",
            "query": "Obscure question",
            "relevant_documents": [],
        }
        update = web_search_node(state)
        assert len(update["relevant_documents"]) == 0
        assert update["search_source"] == "none"

