from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from app.graph.nodes.retrieval import retrieve_documents
from app.graph.nodes.document_grading import grade_documents
from app.graph.nodes.generation import generate_answer


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
    state["retrieved_documents"] = retrieval_result[
        "retrieved_documents"
    ]

    grading_result = grade_documents(state)
    state["relevant_documents"] = grading_result[
        "relevant_documents"
    ]

    if state["relevant_documents"]:
        generation_result = generate_answer(state)

        print("\nANSWER")
        print("=" * 60)
        print(generation_result["answer"])

        print("\nSOURCES")
        print("=" * 60)

        for source in generation_result["sources"]:
            print(source)

    else:
        print("No relevant documents found.")


if __name__ == "__main__":
    main()