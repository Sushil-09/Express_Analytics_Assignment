from app.graph.state import GraphState
from app.services.ingestion import get_vector_store

TOP_K = 5

def retrieve_documents(state: GraphState) -> dict:
    query = state["query"]

    vector_store = get_vector_store()

    documents = vector_store.similarity_search(
        query=query,
        k=TOP_K
    )

    return {
        "retrieved_documents": documents
    }