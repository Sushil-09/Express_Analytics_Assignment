import logging
from app.graph.state import GraphState
from app.services.web_search import perform_web_search

logger = logging.getLogger(__name__)


def web_search_node(state: GraphState) -> dict:
    query = state.get("query") or state.get("original_question", "")
    logger.info(f"Executing web search fallback for query: '{query}'")

    documents = perform_web_search(query)

    return {
        "relevant_documents": documents,
        "search_source": "web_search" if documents else "none",
    }

