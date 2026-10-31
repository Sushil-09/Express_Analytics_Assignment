from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import client, GEMINI_MODEL

def main():
    response = client.models.generate_content(model=GEMINI_MODEL, contents="Explain what a REST API is in one sentence.")

    print(response)

if __name__ == "__main__":
    main()