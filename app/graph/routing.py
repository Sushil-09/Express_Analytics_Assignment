from app.graph.state import GraphState


def route_after_grading(state: GraphState) -> str:
    relevant_documents = state["relevant_documents"]

    if relevant_documents:
        return "generate"

    if state["retry_count"] < state["max_retries"]:
        return "rewrite"

    return "web_search"


def route_after_web_search(state: GraphState) -> str:
    relevant_documents = state.get("relevant_documents", [])

    if relevant_documents:
        return "generate"

    return "fallback"
