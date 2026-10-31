from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.ingestion import get_vector_store

def main():
    vector_store = get_vector_store()
    query = "How do I handle a 404 error in FastAPI?"

    results = vector_store.similarity_search_with_score(query, k=3)

    print(f"\nQuery: {query}\n")
    print("="*60)

    for index, (document, score) in enumerate(results, start=1):
        print(f"\nResult {index}")
        print(f"Similarity score: {score}")
        print(f"Source: {document.metadata.get('source')}")
        print("-"*60)
        print(document.page_content[:500])

if __name__ == "__main__":
    main()