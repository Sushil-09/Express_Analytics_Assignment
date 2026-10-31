from fastapi import APIRouter, HTTPException, UploadFile, File

from app.models.schemas import URLIngestRequest, IngestResponse
from app.services.ingestion import (load_url, load_uploaded_file, ingest_documents)

router = APIRouter(
    prefix="/ingest",
    tags=["Ingestion"]
)

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
    if not file.filename.endswith(".md"):
        raise HTTPException(
            status_code=400,
            detail="Only Markdown (.md) files are currently supported."
        )

    try:
        content = await file.read()

        text = content.decode("utf-8")

        documents = load_uploaded_file(
            content=text,
            filename=file.filename
        )

        result = ingest_documents(documents)

        return IngestResponse(
            message=f"File '{file.filename}' ingested successfully",
            documents_processed=result["documents"],
            chunks_created=result["chunks"]
        )

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded."
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest file: {str(error)}"
        )