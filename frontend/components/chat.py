from urllib.parse import urlsplit

import streamlit as st

from api.client import BackendAPIError, send_chat_message, send_feedback


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


def _on_feedback_change(index: int) -> None:
    val = st.session_state.get(f"feedback_{index}")
    messages = st.session_state.get("chat_messages", [])
    if not (0 <= index < len(messages)):
        return

    msg = messages[index]
    if val is not None:
        rating = "thumbs_up" if val == 1 else "thumbs_down"
        msg["feedback"] = rating
        question = None
        if index > 0 and messages[index - 1].get("role") == "user":
            question = str(messages[index - 1].get("content", ""))
        answer = str(msg.get("content", ""))

        try:
            send_feedback(
                rating=rating,
                comment=msg.get("feedback_comment"),
                question=question,
                answer=answer,
            )
            msg["feedback_submitted"] = True
            st.toast("Thank you for your feedback!", icon="👍" if val == 1 else "👎")
        except BackendAPIError:
            msg["feedback_submitted"] = False
            st.toast("Feedback recorded locally (backend offline).", icon="ℹ️")
    else:
        msg["feedback"] = None
        msg["feedback_submitted"] = False


def _render_feedback(message: dict[str, object], index: int) -> None:
    fb_key = f"feedback_{index}"
    if fb_key not in st.session_state and message.get("feedback") is not None:
        st.session_state[fb_key] = 1 if message.get("feedback") == "thumbs_up" else 0

    st.markdown("**Feedback**")
    col_fb, col_status = st.columns([1, 4])
    with col_fb:
        st.feedback(
            "thumbs",
            key=fb_key,
            on_change=_on_feedback_change,
            args=(index,),
        )
    with col_status:
        current_fb = message.get("feedback")
        if current_fb == "thumbs_up":
            st.caption("Helpful 👍")
        elif current_fb == "thumbs_down":
            st.caption("Needs improvement 👎")

    if current_fb is not None:
        has_comment = bool(message.get("feedback_comment"))
        popover_label = "💬 Edit comment" if has_comment else "💬 Add comment (optional)"
        with st.popover(popover_label):
            comment_input = st.text_area(
                "Feedback details",
                value=str(message.get("feedback_comment") or ""),
                placeholder="Share more details about this response...",
                key=f"comment_input_{index}",
                height=80,
            )
            if st.button("Save Comment", key=f"save_comment_{index}"):
                cleaned_comment = comment_input.strip()
                message["feedback_comment"] = cleaned_comment or None
                messages = st.session_state.get("chat_messages", [])
                question = None
                if index > 0 and messages[index - 1].get("role") == "user":
                    question = str(messages[index - 1].get("content", ""))
                answer = str(message.get("content", ""))
                try:
                    send_feedback(
                        rating=current_fb,
                        comment=cleaned_comment,
                        question=question,
                        answer=answer,
                    )
                    st.toast("Feedback comment saved!", icon="✅")
                except BackendAPIError:
                    st.toast("Comment saved locally (backend offline).", icon="ℹ️")
                st.rerun()

        if has_comment:
            st.caption(f"*Comment: {message['feedback_comment']}*")


def _render_message(message: dict[str, object], index: int) -> None:
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
                search_source = message.get("search_source")
                st.write(f"**Query Type:** {query_type or 'Not provided'}")
                st.write(
                    f"**Retries Used:** "
                    f"{retries_used if retries_used is not None else 'Not provided'}"
                )
                if search_source:
                    source_label = (
                        "🌐 Web Search (Fallback)"
                        if search_source == "web_search"
                        else "📚 Vector Store"
                    )
                    st.write(f"**Information Source:** {source_label}")
            st.markdown("**Sources**")
            _render_sources(message.get("sources"))
            st.divider()
            _render_feedback(message, index)


def render_chat() -> None:
    messages = st.session_state.setdefault("chat_messages", [])
    for index, message in enumerate(messages):
        _render_message(message, index)

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
                "search_source": response.get("search_source"),
                "feedback": None,
                "feedback_comment": None,
                "feedback_submitted": False,
            }
        )
    except BackendAPIError as error:
        messages.append(
            {"role": "assistant", "content": str(error), "error": True}
        )
    st.rerun()
