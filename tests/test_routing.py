from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from app.graph.routing import route_after_grading


def test_relevant_documents():
    state = {
        "relevant_documents": ["some document"],
        "retry_count": 0,
        "max_retries": 2
    }

    print("Relevant docs:", route_after_grading(state))


def test_retry():
    state = {
        "relevant_documents": [],
        "retry_count": 0,
        "max_retries": 2
    }

    print("Retry available:", route_after_grading(state))


def test_fallback():
    state = {
        "relevant_documents": [],
        "retry_count": 2,
        "max_retries": 2
    }

    print("Retry exhausted:", route_after_grading(state))


if __name__ == "__main__":
    test_relevant_documents()
    test_retry()
    test_fallback()