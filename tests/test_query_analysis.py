from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from app.graph.nodes.query_analysis import analyze_query


def main():
    state = {
        "original_question": "How do I return a 404 when an item does not exist?",
        "query": "",
        "query_type": None,
        "retrieved_documents": [],
        "relevant_documents": [],
        "retry_count": 0,
        "max_retries": 2,
        "answer": None,
        "sources": []
    }

    result = analyze_query(state)

    print("\nQuery Analysis Result:")
    print(result)


if __name__ == "__main__":
    main()