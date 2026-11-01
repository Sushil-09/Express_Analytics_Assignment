from typing import TypedDict, List, Optional
from langchain_core.documents import Document

class GraphState(TypedDict):

    original_question: str # user initial query
    query: str # current query that is running
    query_type: Optional[str]
    retrieved_documents: List[Document] # docs returned by vector search
    relevant_documents: List[Document] # docs that passed relevance check
    retry_count: int
    max_retries: int
    answer: Optional[str] # final answer
    sources: List[dict] # sources for the answer
    search_source: Optional[str] # "vector_store" | "web_search" | None
