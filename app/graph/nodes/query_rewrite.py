from app.config import client, GEMINI_MODEL
from app.graph.state import GraphState


def rewrite_query(state: GraphState) -> dict:
    original_question = state["original_question"]
    current_query = state["query"]

    prompt = f"""
        You are improving a search query for a technical documentation system.

        The previous search did not find relevant documentation.

        Original user question:
        {original_question}

        Previous search query:
        {current_query}

        Rewrite the search query using different wording or more specific
        technical terminology.

        Rules:
        - Preserve the user's original intent.
        - Do not answer the question.
        - Return only the improved search query.
        """

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    rewritten_query = response.text.strip()

    return {
        "query": rewritten_query,
        "retry_count": state["retry_count"] + 1
    }