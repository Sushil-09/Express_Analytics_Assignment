# Technical Documentation Assistant (Self-Corrective RAG)

A production-grade Retrieval-Augmented Generation (RAG) assistant designed for technical documentation. Built using **LangGraph**, **FastAPI**, **Google Gemini**, **HuggingFace Embeddings**, and **ChromaDB**, with an interactive **Streamlit** user interface.

The system incorporates **self-corrective retrieval** inspired by Corrective RAG (CRAG) and Self-RAG, including query analysis, LLM-based document grading, automatic query rewriting with retry limits, web search fallback, multi-format ingestion (`.md`, `.txt`, `.html`, URLs), and human feedback collection.

---

## Architecture Overview

The system models the question-answering lifecycle as a state machine using a LangGraph `StateGraph`.

### Workflow Diagram

```mermaid
flowchart TD
    Start([User Query]) --> QA[Node 1: Query Analysis & Classification]
    QA --> Retrieve[Node 2: Vector Search Retrieval]
    Retrieve --> Grade[Node 3: Document Relevance Grading]

    Grade -->|Relevant Docs Found| Gen[Node 4: Grounded Answer Generation]
    Grade -->|All Irrelevant & Retries < Max| Rewrite[Node: Query Rewriter]
    Rewrite -->|Rewritten Query| Retrieve

    Grade -->|All Irrelevant & Retries Exhausted| WebSearch[Bonus Node: Web Search Fallback]
    WebSearch -->|Web Content Found| Gen
    WebSearch -->|No Content Found / Network Error| Fallback[Node: Fallback Response]

    Gen --> Feedback[User Feedback: Thumbs Up / Down + Comment]
    Gen --> EndNode([Final Answer with Citations])
    Fallback --> EndNode
```

### Graph Nodes & Self-Corrective Logic

1. **Node 1: Query Analysis (`query_analysis`)**:
   - Analyzes raw user questions, rewrites ambiguities, and classifies queries by type (`conceptual`, `how-to`, `troubleshooting`, `api_reference`).
2. **Node 2: Retrieval (`retrieve`)**:
   - Queries ChromaDB using dense semantic similarity with `sentence-transformers/all-MiniLM-L6-v2` embeddings, retrieving the top-$k$ document chunks with source metadata.
3. **Node 3: Document Grading (`grade_documents`)**:
   - Evaluates each retrieved chunk using an LLM-as-a-judge to filter out noise. Only chunks deemed relevant are retained for generation.
4. **Conditional Routing (`route_after_grading`)**:
   - **Generation Path**: If at least one relevant document is found, immediately proceeds to generation.
   - **Rewrite Path**: If no documents are relevant and retry budget remains (`retry_count < max_retries`), the query is rewritten with focused search keywords and re-retrieved.
   - **Web Search Fallback**: If retries are exhausted without finding relevant corpus chunks, execution transitions to web search.
5. **Bonus Node: Web Search Fallback (`web_search`)**:
   - Queries real-time search APIs (Tavily, Serper, or DuckDuckGo) for external documentation. If results are found, routes to generation with web citations; otherwise, transitions to graceful fallback.
6. **Node 4: Generation (`generate`)**:
   - Generates an accurate, grounded answer strictly constrained to the validated context, complete with source links and citations.
7. **Node 5: Fallback Response (`fallback`)**:
   - Returns a safe, deterministic message indicating insufficient information when context cannot be located.

---

## State Schema (`GraphState`)

The pipeline tracks data across graph nodes via a typed state dictionary:

| Field | Type | Description |
|---|---|---|
| `original_question` | `str` | Raw question submitted by the user |
| `query` | `str` | Current active query (rewritten or expanded) |
| `query_type` | `Optional[str]` | Classification (`how-to`, `conceptual`, etc.) |
| `retrieved_documents`| `List[Document]` | Raw chunks returned by similarity search |
| `relevant_documents` | `List[Document]` | Chunks validated by the grading node |
| `retry_count` | `int` | Number of rewrite/re-retrieval attempts made |
| `max_retries` | `int` | Maximum allowed query rewrite cycles (default: 2) |
| `answer` | `Optional[str]` | Generated response text |
| `sources` | `List[str]` | Unique source document paths or web URLs cited |
| `search_source` | `Optional[str]` | Origin of data: `"vector_store"` or `"web_search"` |

---

## Setup Instructions

### 1. Prerequisites

- Python 3.10+ (tested with Python 3.12 & 3.14)
- Git

### 2. Clone Repository & Setup Virtual Environment

```bash
git clone <repository-url>
cd Assignment

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Required: Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Web Search Fallback Providers (Tavily or Serper)
# If neither is set, DuckDuckGo is used as zero-config fallback
TAVILY_API_KEY=your_tavily_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

---

## Ingesting Technical Documentation

The ingestion pipeline supports **Markdown (`.md`)**, **Plain Text (`.txt`)**, **HTML (`.html`, `.htm`)**, and **Live URLs**.

### Ingesting Seed Documents

Run the seed script to index local markdown and documentation files in `data/seed_documents/`:

```bash
python scripts/ingest_seed.py
```

### Ingesting Live Web Documentation

Run the URL scraper script to fetch, clean, chunk, and index live documentation (e.g., FastAPI tutorials):

```bash
python scripts/ingest_urls.py
```

---

## Running the Application

### 1. Start the FastAPI Backend

```bash
uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger Docs: `http://127.0.0.1:8000/docs`
- ReDoc Docs: `http://127.0.0.1:8000/redoc`

### 2. Start the Streamlit Frontend

In a separate terminal (with `.venv` activated):

```bash
streamlit run frontend/app.py
```

- Web UI opens at: `http://localhost:8501`
- Includes live backend health status, knowledge upload manager, chat interface, expandable response reasoning details, and interactive **thumbs up / thumbs down** feedback with comments.

### 3. Running Unit & Integration Tests

```bash
pytest
```

---

## API Reference & Examples

### 1. `POST /chat` (or `POST /query`)
Submit a natural language question.

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I raise a 404 HTTP exception in FastAPI?"}'
```

**Response (HTTP 200):**
```json
{
  "answer": "To raise a 404 HTTP exception in FastAPI, import `HTTPException` from `fastapi` and raise it with `status_code=404` and a `detail` message.",
  "sources": [
    "data/seed_documents/fastapi_error_handling.md"
  ],
  "query_type": "how-to",
  "retries_used": 0,
  "search_source": "vector_store"
}
```

---

### 2. `POST /ingest/file`
Upload and index a Markdown, text, or HTML document.

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/ingest/file \
  -F "file=@data/seed_documents/fastapi_basics.md"
```

**Response (HTTP 200):**
```json
{
  "message": "File 'fastapi_basics.md' ingested successfully",
  "documents_processed": 1,
  "chunks_created": 3
}
```

---

### 3. `POST /ingest/url`
Ingest and index a web documentation page.

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/ingest/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://fastapi.tiangolo.com/tutorial/path-params/"}'
```

**Response (HTTP 200):**
```json
{
  "message": "URL ingested successfully",
  "documents_processed": 1,
  "chunks_created": 5
}
```

---

### 4. `GET /documents`
List indexed documents and total chunk count in the corpus.

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/documents
```

**Response (HTTP 200):**
```json
{
  "total_chunks": 18,
  "documents": [
    "data/seed_documents/fastapi_basics.md",
    "data/seed_documents/fastapi_error_handling.md",
    "https://fastapi.tiangolo.com/tutorial/path-params/"
  ]
}
```

---

### 5. `POST /feedback`
Submit user rating (thumbs up / thumbs down) with optional qualitative comments.

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "rating": "thumbs_up",
    "comment": "Accurate answer and cited the exact file.",
    "question": "How do I raise a 404 HTTP exception in FastAPI?",
    "answer": "To raise a 404 HTTP exception in FastAPI..."
  }'
```

**Response (HTTP 200):**
```json
{
  "message": "Feedback submitted successfully",
  "status": "success"
}
```

---

### 6. `GET /feedback`
Retrieve feedback records for quality evaluation.

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/feedback
```

---

## Design Decisions & Tradeoffs

### 1. LangGraph Self-Corrective Loop vs. Naive RAG
- **Decision**: Implemented an active graph with query rewriting, document grading, and fallback routing instead of a linear Retrieve $\rightarrow$ Generate pipeline.
- **Tradeoff**: Increased latency per request on difficult or ambiguous queries (due to LLM document grading and potential retry turns).
- **Benefit**: Vastly reduces hallucination by ensuring answers are generated exclusively from verified, relevant content.

### 2. Chunking Strategy (`RecursiveCharacterTextSplitter`)
- **Decision**: Chunk size of 1000 characters with 200 character overlap, splitting on paragraphs (`\n\n`), code boundaries (`\n`), and sentences.
- **Tradeoff**: 1000 characters balances contextual completeness for technical explanations with code snippets. Larger chunks dilute embedding precision; smaller chunks fragment code blocks and API signatures.
- **HTML & Document Cleaning**: HTML input is parsed with BeautifulSoup to decompose non-content tags (`<nav>`, `<script>`, `<style>`, `<footer>`) prior to chunking, preventing noisy headers and navigation scripts from polluting the embeddings.

### 3. Local Sentence-Transformers vs. Cloud Embeddings
- **Decision**: Used `sentence-transformers/all-MiniLM-L6-v2` executed locally via HuggingFace rather than proprietary cloud embedding APIs.
- **Tradeoff**: Requires local CPU/GPU compute during ingestion.
- **Benefit**: Zero cost, no external rate limits, fast embedding generation, and 100% reproducibility across environments.

### 4. Document Grading with Structured JSON Output
- **Decision**: Enforced JSON response mode on the Gemini document grading node with strict schema `{"relevant": true|false}`.
- **Tradeoff**: Strict format requirements; addressed by configuring `response_mime_type="application/json"`.
- **Benefit**: Eliminates parsing ambiguity and prevents regex fragility when extracting relevance judgments.

### 5. Multi-Layer Web Search Fallback
- **Decision**: Supported Tavily, Serper, and DuckDuckGo with automatic graceful degradation.
- **Tradeoff**: External web results can be noisier than curated internal documentation.
- **Benefit**: Prevents the assistant from hitting dead ends when encountering out-of-corpus queries, returning grounded answers with live web links.

### 6. Persistent Feedback Loop
- **Decision**: Exposed `POST /feedback` on the backend and integrated `st.feedback("thumbs")` with popover comment submission into the Streamlit chat UI.
- **Tradeoff**: Added state tracking per message turn in frontend session state.
- **Benefit**: Captures human-in-the-loop evaluation data persistently in `data/feedback.json` for continuous RAG evaluation.

---

## What Would Be Improved With More Time

1. **Reranking**: Add a Cross-Encoder (e.g. `bge-reranker-large` or Cohere Rerank) between retrieval and grading to re-score documents before LLM grading.
2. **Conversational Memory**: Add thread-based memory (`langgraph.checkpoint.memory.MemorySaver`) to allow multi-turn follow-up questions referencing previous answers.
3. **Automated RAG Triad Evaluation**: Integrate TruLens or Ragas to continuously compute Context Relevance, Groundedness, and Answer Relevance on collected feedback data.
4. **Streaming Answers**: Implement Server-Sent Events (SSE) / WebSocket streaming from FastAPI to Streamlit for real-time token rendering.

