from urllib.parse import urlsplit

import streamlit as st

from api.client import BackendAPIError, send_chat_message


def _render_sources(sources: object) -> None:
    if not isinstance(sources, list):
        sources = []

    valid_sources = [source for source in sources if isinstance(source, str) and source.strip()]
    if not valid_sources:
        st.caption("No relevant sources were used.")
        return

    for index, source in enumerate(valid_sources, start=1):
        try:
            parsed = urlsplit(source)
            is_web_url = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
        except ValueError:
            is_web_url = False

        if is_web_url:
            st.link_button(source, source, key=f"source-{index}-{source}")
        else:
            st.text(f"{index}. {source}")


def _render_message(message: dict[str, object]) -> None:
    role = str(message.get("role", "assistant"))
    with st.chat_message(role):
        if message.get("error"):
            st.error(str(message["content"]))
            return

        st.markdown(str(message.get("content", "")))
        if role == "assistant":
            with st.expander("Response Details"):
                query_type = message.get("query_type")
                retries_used = message.get("retries_used")
                st.write(f"**Query Type:** {query_type or 'Not provided'}")
                st.write(
                    f"**Retries Used:** "
                    f"{retries_used if retries_used is not None else 'Not provided'}"
                )
            st.markdown("**Sources**")
            _render_sources(message.get("sources"))


def render_chat() -> None:
    messages = st.session_state.setdefault("chat_messages", [])
    for message in messages:
        _render_message(message)

    question = st.chat_input("Ask a question about your documentation")
    if question is None:
        return

    question = question.strip()
    if not question:
        st.warning("Please enter a question.")
        return

    messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Searching technical documentation..."):
                response = send_chat_message(question)

        answer = response.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            raise BackendAPIError("The backend returned an empty answer.")
        messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": response.get("sources", []),
                "query_type": response.get("query_type"),
                "retries_used": response.get("retries_used"),
            }
        )
    except BackendAPIError as error:
        messages.append(
            {"role": "assistant", "content": str(error), "error": True}
        )
    st.rerun()