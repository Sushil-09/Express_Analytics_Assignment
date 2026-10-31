from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.ingestion import load_url

def main():
    url = "https://fastapi.tiangolo.com/tutorial/path-params"

    print(f"Fetching: {url}")

    documents = load_url(url)

    document = documents[0]

    print("\nSuccessfully loaded URL")
    print(f"Source: {document.metadata['source']}")
    print(f"Characters extracted: {len(document.page_content)}")

    print("\nFirst 1000 characters:\n")
    print(document.page_content[:1000])

if __name__ == "__main__":
    main()