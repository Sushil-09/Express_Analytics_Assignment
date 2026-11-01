from langgraph.graph import StateGraph, START, END

from app.graph.state import GraphState
from app.graph.routing import route_after_grading, route_after_web_search

from app.graph.nodes.query_analysis import analyze_query
from app.graph.nodes.retrieval import retrieve_documents
from app.graph.nodes.document_grading import grade_documents
from app.graph.nodes.query_rewrite import rewrite_query
from app.graph.nodes.web_search import web_search_node
from app.graph.nodes.generation import generate_answer
from app.graph.nodes.fallback import fallback_answer


def build_graph():

    workflow = StateGraph(GraphState)

    workflow.add_node("query_analysis", analyze_query)
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("grade_documents", grade_documents)
    workflow.add_node("rewrite_query", rewrite_query)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate", generate_answer)
    workflow.add_node("fallback", fallback_answer)

    # Start workflow
    workflow.add_edge(
        START,
        "query_analysis"
    )

    # Query analysis -> Retrieval
    workflow.add_edge(
        "query_analysis",
        "retrieve"
    )

    # Retrieval -> Document grading
    workflow.add_edge(
        "retrieve",
        "grade_documents"
    )

    # Conditional routing after grading:
    # 1. Relevant docs found -> generate
    # 2. Retries remaining -> rewrite_query
    # 3. Retries exhausted -> web_search fallback
    workflow.add_conditional_edges(
        "grade_documents",
        route_after_grading,
        {
            "generate": "generate",
            "rewrite": "rewrite_query",
            "web_search": "web_search",
        }
    )

    # Retry loop
    workflow.add_edge(
        "rewrite_query",
        "retrieve"
    )

    # Web search fallback routing:
    # If web search returned content -> generate, else -> fallback
    workflow.add_conditional_edges(
        "web_search",
        route_after_web_search,
        {
            "generate": "generate",
            "fallback": "fallback",
        }
    )

    # Final routes
    workflow.add_edge(
        "generate",
        END
    )

    workflow.add_edge(
        "fallback",
        END
    )

    return workflow.compile()


rag_graph = build_graph()
