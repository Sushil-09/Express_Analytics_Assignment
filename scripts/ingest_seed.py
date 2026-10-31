from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.ingestion import load_markdown_file, ingest_documents

DATA_FOLDER = Path("data/seed_documents")

def main():
    files = list(DATA_FOLDER.glob("*.md"))

    if not files:
        print("No markdown files found.")
        return
    all_documents = []

    for file_path in files:
        print(f"Loading: {file_path}")
        documents = load_markdown_file(str(file_path))
        all_documents.extend(documents)

    result = ingest_documents(all_documents)

    print("\nIngestion complete")
    print(f"Documents processed: {result['documents']}")
    print(f"Chunks created: {result['chunks']}")

if __name__ == "__main__":
    main()