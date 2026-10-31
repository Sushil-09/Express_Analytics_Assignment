from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.ingestion import router as ingestion_router

app = FastAPI(
    title="Self-Corrective RAG API",
    description="A technical documentation assistant using Gemini and LangGraph",
    version="1.0.0"
)


app.include_router(chat_router)
app.include_router(ingestion_router)

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