import json

from google.genai import types

from app.config import client, GEMINI_MODEL
from app.graph.state import GraphState


def grade_documents(state: GraphState) -> dict:
    question = state["original_question"]
    documents = state["retrieved_documents"]

    relevant_documents = []

    for index, document in enumerate(documents, start=1):

        prompt = f"""
            You are grading a retrieved technical documentation chunk.

            Determine whether the document chunk is relevant for answering
            the user's question.

            User question:
            {question}

            Document chunk:
            {document.page_content}

            Return ONLY valid JSON:

            {{
                "relevant": true
            }}

            Use true if the chunk contains information that can help answer
            the question.

            Use false if the chunk is unrelated or not useful.
            """

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        result = json.loads(response.text)

        is_relevant = result.get("relevant", False)

        print(
            f"Document {index}: "
            f"{'RELEVANT' if is_relevant else 'IRRELEVANT'}"
        )

        if is_relevant:
            relevant_documents.append(document)

    return {
        "relevant_documents": relevant_documents
    }