import json
from google.genai import types
from app.config import client, GEMINI_MODEL
from app.graph.state import GraphState

def analyze_query(state: GraphState) -> dict:
    question = state["original_question"]
    prompt = f"""
        You are preparing a technical documentation search query.
        User question:
        {question}
        Your job:
        Rewrite the question to improve semantic retrieval.
        Preserve the original meaning.
        Make technical terms explicit if useful.
        Classify the query into exactly one of these categories:
        conceptual
        how-to
        troubleshooting
        api-reference
        Return ONLY valid JSON in this format:
        {{
        "query": "improved search query",
        "query_type": "one category"
        }}
        """
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    result = json.loads(response.text)

    return {
        "query": result["query"],
        "query_type": result["query_type"]
    }