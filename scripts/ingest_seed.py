from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.ingestion import load_file, ingest_documents

DATA_FOLDER = Path("data/seed_documents")
SUPPORTED_EXTENSIONS = {".md", ".txt", ".html", ".htm"}


def main():
    files = [
        p for p in DATA_FOLDER.glob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not files:
        print("No supported documents (.md, .txt, .html) found.")
        return
    all_documents = []

    for file_path in files:
        print(f"Loading: {file_path}")
        documents = load_file(str(file_path))
        all_documents.extend(documents)

    result = ingest_documents(all_documents)

    print("\nIngestion complete")
    print(f"Documents processed: {result['documents']}")
    print(f"Chunks created: {result['chunks']}")


if __name__ == "__main__":
    main()
