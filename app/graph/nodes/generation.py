from app.config import client, GEMINI_MODEL
from app.graph.state import GraphState


def generate_answer(state: GraphState) -> dict:
    question = state["original_question"]
    documents = state["relevant_documents"]

    context_parts = []

    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "Unknown source")

        context_parts.append(
            f"""
            [Document {index}]
            Source: {source}

            Content:
            {document.page_content}
            """
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
        You are a technical documentation assistant.
        Answer the user's question using ONLY the provided documentation.
        User question:
        {question}
        Documentation:
        {context}
        Rules:
        - Answer only using the provided documentation.
        - Do not invent information.
        - If the documentation does not contain enough information,
        clearly say so.
        - Be concise but technically accurate.
        """

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    answer = response.text.strip()

    sources = []

    for document in documents:
        source = document.metadata.get("source")

        if source and source not in sources:
            sources.append(source)

    return {
        "answer": answer,
        "sources": sources
    }