from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from app.graph.workflow import rag_graph


def main():

    initial_state = {
        "original_question": (
            "How do I train a neural network using PyTorch?"
        ),
        "query": "",
        "query_type": None,
        "retrieved_documents": [],
        "relevant_documents": [],
        "retry_count": 0,
        "max_retries": 2,
        "answer": None,
        "sources": []
    }

    result = rag_graph.invoke(initial_state)

    print("\n" + "=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)

    print(result["answer"])

    print("\n" + "=" * 70)
    print("SOURCES")
    print("=" * 70)

    for source in result["sources"]:
        print(source)

    print("\n" + "=" * 70)
    print("WORKFLOW INFO")
    print("=" * 70)

    print(f"Query type: {result['query_type']}")
    print(f"Final query: {result['query']}")
    print(f"Retries used: {result['retry_count']}")


if __name__ == "__main__":
    main()