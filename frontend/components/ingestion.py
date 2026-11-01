from typing import Any

import streamlit as st

from api.client import BackendAPIError, ingest_file, ingest_url


STATISTICS = (
    ("documents_processed", "Documents processed"),
    ("chunks_created", "Chunks created"),
    ("new_chunks_added", "New chunks added"),
    ("duplicate_chunks_skipped", "Duplicate chunks skipped"),
)


def _show_ingestion_result(result: dict[str, Any]) -> None:
    message = result.get("message")
    st.success(message if isinstance(message, str) and message else "Ingestion completed.")

    displayed_statistics = False
    for field, label in STATISTICS:
        value = result.get(field)
        if value is not None:
            st.write(f"**{label}:** {value}")
            displayed_statistics = True
    if not displayed_statistics:
        st.caption("The backend did not return ingestion statistics.")


def render_ingestion() -> None:
    st.subheader("Knowledge Management")
    st.markdown("**Upload Document**")

    with st.form("document_ingestion"):
        uploaded_file = st.file_uploader(
            "Upload a document (.md, .txt, .html)",
            type=["md", "txt", "html", "htm"],
            accept_multiple_files=False,
            help="Supported formats: Markdown (.md), Plain Text (.txt), HTML (.html, .htm)",
        )
        ingest_document = st.form_submit_button(
            "Ingest Document",
            use_container_width=True,
        )

    if ingest_document:
        if uploaded_file is None:
            st.warning("Choose a file (.md, .txt, or .html) before ingesting.")
        else:
            try:
                with st.spinner("Ingesting document..."):
                    result = ingest_file(uploaded_file)
                _show_ingestion_result(result)
            except BackendAPIError as error:
                st.error(f"Document ingestion failed: {error}")
            except OSError as error:
                st.error(f"Could not read the selected document: {error}")

    st.divider()
    st.markdown("**Ingest Documentation URL**")
    with st.form("url_ingestion"):
        url = st.text_input(
            "Documentation URL",
            placeholder="https://example.com/documentation",
            label_visibility="collapsed",
        )
        ingest_documentation_url = st.form_submit_button(
            "Ingest URL",
            use_container_width=True,
        )

    if ingest_documentation_url:
        if not url.strip():
            st.warning("Enter a documentation URL before ingesting.")
        else:
            try:
                with st.spinner("Ingesting documentation URL..."):
                    result = ingest_url(url.strip())
                _show_ingestion_result(result)
            except BackendAPIError as error:
                st.error(f"URL ingestion failed: {error}")
