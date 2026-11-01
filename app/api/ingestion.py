from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File

from app.models.schemas import URLIngestRequest, IngestResponse
from app.services.ingestion import (
    load_url,
    load_uploaded_file,
    ingest_documents,
    get_vector_store,
)

router = APIRouter(
    prefix="/ingest",
    tags=["Ingestion"]
)

SUPPORTED_EXTENSIONS = {".md", ".txt", ".html", ".htm"}


@router.post("/url", response_model=IngestResponse)
def ingest_url(request: URLIngestRequest):
    try:
        documents = load_url(str(request.url))
        result = ingest_documents(documents)

        return IngestResponse(
            message="URL ingested successfully",
            documents_processed=result["documents"],
            chunks_created=result["chunks"]
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest URL: {str(error)}"
        )


@router.post("/file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)):
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported formats: .md, .txt, .html"
        )

    try:
        content = await file.read()
        text = content.decode("utf-8")

        documents = load_uploaded_file(
            content=text,
            filename=filename
        )

        result = ingest_documents(documents)

        return IngestResponse(
            message=f"File '{filename}' ingested successfully",
            documents_processed=result["documents"],
            chunks_created=result["chunks"]
        )

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded."
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest file: {str(error)}"
        )


@router.get("/documents")
def list_documents():
    try:
        vector_store = get_vector_store()
        data = vector_store.get()
        metadatas = data.get("metadatas", [])
        sources = list({meta.get("source") for meta in metadatas if meta and "source" in meta})
        return {
            "total_chunks": len(data.get("ids", [])),
            "documents": sources
        }
    except Exception as e:
        return {"total_chunks": 0, "documents": []}
