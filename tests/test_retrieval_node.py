from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from app.graph.nodes.retrieval import retrieve_documents


def main():
    state = {
        "original_question": "How do I return a 404 when an item does not exist?",
        "query": "How to raise an HTTP 404 Not Found exception in FastAPI?",
        "query_type": "how-to",
        "retrieved_documents": [],
        "relevant_documents": [],
        "retry_count": 0,
        "max_retries": 2,
        "answer": None,
        "sources": []
    }

    result = retrieve_documents(state)

    documents = result["retrieved_documents"]

    print(f"\nRetrieved {len(documents)} documents\n")
    print("=" * 60)

    for index, document in enumerate(documents, start=1):
        print(f"\nResult {index}")
        print(f"Source: {document.metadata.get('source')}")
        print("-" * 60)
        print(document.page_content[:400])


if __name__ == "__main__":
    main()