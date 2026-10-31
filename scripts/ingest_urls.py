from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.ingestion import load_url, ingest_documents

URLS = [
    "https://fastapi.tiangolo.com/tutorial/path-params/",
    "https://fastapi.tiangolo.com/tutorial/body/",
    "https://fastapi.tiangolo.com/tutorial/handling-errors/",
]

def main():
    all_documents = []

    for url in URLS:
        print(f"Fetching: {url}")

        try:
            documents = load_url(url)
            all_documents.extend(documents)

            print("Successfully loaded!")
        except Exception as error:
            print(f"Failed to load {url}")
            print(f"Error: {error}")

    if not all_documents:
        print("\nNo documents were loaded.")
        return

    result = ingest_documents(all_documents)
    print("\nIngestion complete!")
    print(f"Documents processed: {result['documents']}")
    print(f"Chunks created: {result['chunks']}")

if __name__ == "__main__":
    main()