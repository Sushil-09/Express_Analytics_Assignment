from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from app.graph.nodes.retrieval import retrieve_documents
from app.graph.nodes.document_grading import grade_documents


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

    retrieval_result = retrieve_documents(state)

    state["retrieved_documents"] = (
        retrieval_result["retrieved_documents"]
    )

    print(f"\nRetrieved: {len(state['retrieved_documents'])} documents\n")

    grading_result = grade_documents(state)

    relevant_documents = (
        grading_result["relevant_documents"]
    )

    print("\n" + "=" * 60)
    print(f"\nRelevant documents: {len(relevant_documents)}")

    for index, document in enumerate(
        relevant_documents,
        start=1
    ):
        print(f"\nResult {index}")
        print(
            f"Source: "
            f"{document.metadata.get('source')}"
        )
        print("-" * 50)
        print(document.page_content[:300])


if __name__ == "__main__":
    main()