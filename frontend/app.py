import streamlit as st

from api.client import BackendAPIError, check_health
from components.chat import render_chat
from components.ingestion import render_ingestion


st.set_page_config(
    page_title="Self-Corrective RAG Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=30, show_spinner=False)
def _backend_status() -> tuple[bool, str]:
    try:
        check_health()
        return True, "Connected"
    except BackendAPIError as error:
        return False, str(error)


with st.sidebar:
    connected, status_message = _backend_status()
    st.subheader("Backend Status")
    if connected:
        st.success("🟢 Backend Connected")
    else:
        st.error("🔴 Backend Unavailable")
        st.caption(status_message)

    st.divider()
    render_ingestion()

st.title("Self-Corrective RAG Assistant")
st.caption("Ask questions about your ingested technical documentation.")
st.divider()
render_chat()