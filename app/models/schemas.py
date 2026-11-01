from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    query_type: Optional[str] = None
    retries_used: int = 0
    search_source: Optional[str] = None

class URLIngestRequest(BaseModel):
    url: HttpUrl

class IngestResponse(BaseModel):
    message: str
    documents_processed: int
    chunks_created: int

class FeedbackRequest(BaseModel):
    rating: str
    comment: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None

class FeedbackResponse(BaseModel):
    message: str
    status: str = "success"
