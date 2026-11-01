from fastapi import APIRouter

from app.graph.workflow import rag_graph
from app.models.schemas import ChatRequest, ChatResponse


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):

    initial_state = {
        "original_question": request.question,
        "query": "",
        "query_type": None,
        "retrieved_documents": [],
        "relevant_documents": [],
        "retry_count": 0,
        "max_retries": 2,
        "answer": None,
        "sources": [],
        "search_source": None,
    }

    result = rag_graph.invoke(initial_state)

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        query_type=result["query_type"],
        retries_used=result["retry_count"],
        search_source=result.get("search_source"),
    )
