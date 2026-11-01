from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from app.graph.routing import route_after_grading, route_after_web_search


def test_relevant_documents():
    state = {
        "relevant_documents": ["some document"],
        "retry_count": 0,
        "max_retries": 2
    }

    result = route_after_grading(state)
    print("Relevant docs:", result)
    assert result == "generate"


def test_retry():
    state = {
        "relevant_documents": [],
        "retry_count": 0,
        "max_retries": 2
    }

    result = route_after_grading(state)
    print("Retry available:", result)
    assert result == "rewrite"


def test_web_search_fallback():
    state = {
        "relevant_documents": [],
        "retry_count": 2,
        "max_retries": 2
    }

    result = route_after_grading(state)
    print("Retry exhausted (routes to web_search):", result)
    assert result == "web_search"


def test_route_after_web_search():
    state_with_docs = {"relevant_documents": ["web doc 1"]}
    assert route_after_web_search(state_with_docs) == "generate"

    state_empty = {"relevant_documents": []}
    assert route_after_web_search(state_empty) == "fallback"


if __name__ == "__main__":
    test_relevant_documents()
    test_retry()
    test_web_search_fallback()
    test_route_after_web_search()
