from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup

import hashlib

from functools import lru_cache
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_DB_PATH = "data/chroma_db"
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

@lru_cache
def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)

@lru_cache
def get_vector_store():
    return Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=get_embeddings(), collection_name="technical_docs",)

def load_markdown_file(file_path: str) -> List[Document]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"file not found: {file_path}")

    content = path.read_text(encoding="utf-8")

    document = Document(
        page_content=content,
        metadata={
            "source": str(path),
            "file_name": path.name,
            "source_type": "file",
        },
    )

    return [document]

def load_url(url: str) -> List[Document]:
    response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})

    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    document = Document(page_content=text, metadata={"source": url, "source_type": "url",},)
    return [document]

def split_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return splitter.split_documents(documents)

def ingest_documents(documents: List[Document]):
    chunks = split_documents(documents)
    vector_store = get_vector_store()

    ids = [create_chunk_id(chunk) for chunk in chunks]

    vector_store.add_documents(documents=chunks, ids=ids)

    return {
        "documents": len(documents),
        "chunks": len(chunks),
    }

def load_uploaded_file(content: str, filename: str) -> List[Document]:
    
    document = Document(
        page_content=content,
        metadata={
            "source": filename,
            "file_name": filename,
            "source_type": "upload",
        },
    )

    return [document]

def create_chunk_id(document: Document) -> str:
    source = document.metadata.get("source", "")
    content = document.page_content
    raw_value = f"{source}:{content}"

    return hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()