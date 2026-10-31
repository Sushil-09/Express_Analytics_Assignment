from app.graph.state import GraphState


def fallback_answer(state: GraphState) -> dict:
    return {
        "answer": (
            "I don't have enough relevant information in the "
            "provided documentation to answer this question."
        ),
        "sources": []
    }