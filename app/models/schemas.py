from typing import List
from pydantic import BaseModel, HttpUrl

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    query_type: str | None
    retries_used: int

class URLIngestRequest(BaseModel):
    url: HttpUrl

class IngestResponse(BaseModel):
    message: str
    documents_processed: int
    chunks_created: int