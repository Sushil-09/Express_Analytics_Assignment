from fastapi import FastAPI

from app.api.chat import router as chat_router, chat as chat_endpoint
from app.api.ingestion import router as ingestion_router, list_documents
from app.api.feedback import router as feedback_router
from app.models.schemas import ChatResponse

app = FastAPI(
    title="Self-Corrective RAG API",
    description="A technical documentation assistant using Gemini and LangGraph",
    version="1.0.0"
)

app.include_router(chat_router)
app.include_router(ingestion_router)
app.include_router(feedback_router)

# Provide /query as an alias for /chat as specified in the assignment API requirements
app.add_api_route(
    "/query",
    chat_endpoint,
    methods=["POST"],
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Submit a question (alias for /chat)",
)

# Provide /documents as specified in the assignment API requirements
app.add_api_route(
    "/documents",
    list_documents,
    methods=["GET"],
    tags=["Ingestion"],
    summary="List indexed documents",
)


@app.get("/")
def root():
    return {
        "message": "Self-Corrective RAG API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
