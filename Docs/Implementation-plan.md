# Implementation Plan: Mutual Fund FAQ Assistant

This document outlines the step-by-step implementation plan for building the RAG-based FAQ Assistant based on the `architecture.md` document.

## 1. Selected Technology Stack
To ensure a lightweight and robust system, the following stack will be used:
- **Backend API:** FastAPI (Python)
- **RAG Orchestration:** LangChain
- **LLM & Embeddings:** Groq (for generation) and BGE models (for embeddings). *Requires a Groq API Key.*
- **Vector Database:** ChromaDB (Local, lightweight, file-based)
- **Web Scraping:** BeautifulSoup4 (for extracting text from the Groww URLs)
- **Frontend UI:** Streamlit (Provides a very fast, clean, and minimal chat interface in pure Python)

---

## Phase 1: Project Setup & Environment
**Objective:** Set up the repository and install dependencies.
1. Initialize a Python virtual environment (`venv`).
2. Create `requirements.txt` with dependencies:
   - `fastapi`, `uvicorn`, `langchain`, `langchain-groq`, `sentence-transformers`, `chromadb`, `beautifulsoup4`, `requests`, `streamlit`, `python-dotenv`.
3. Set up a `.env` file for storing the `GROQ_API_KEY`.
4. Create the initial folder structure:
   ```text
   /src
     /data_pipeline    # Scraping and ingestion scripts
     /rag_core         # Embeddings, retrieval, and LLM chains
     /api              # FastAPI endpoints
     /ui               # Streamlit frontend app
   ```

## Phase 2: Data Ingestion Pipeline (Offline)
**Objective:** Scrape the 5 specified Groww URLs, process the content, and populate the Vector Database.

### Task 2.1: Web Scraper
**File:** `src/data_pipeline/scraper.py`
**Objective:** Fetch and clean HTML content from the 5 Groww URLs, stripping site-wide boilerplate.
- Use `requests` with appropriate headers (User-Agent) to fetch the HTML from each URL.
- Use `BeautifulSoup` to parse the HTML and strip non-content elements (`script`, `style`, `nav`, `header`, `footer`, `button`, `svg`, `iframe`, `noscript`).
- Extract clean text using `get_text()` with whitespace normalization.
- **Strip Groww boilerplate:** Remove the site-wide navigation menu (~first 1,900 chars) and footer links (everything after Fund House info section). These are identical across all 5 pages and contain no fund-specific data.
- Return a list of dictionaries containing `url` and `content` for each page.
- Save raw data to `data/raw_scraped_data.json` for inspection and reuse.
- Include error handling and logging for failed requests.

### Task 2.2: Document Chunking (Section-Aware)
**File:** `src/data_pipeline/chunker.py`
**Objective:** Extract logical sections from each fund page and produce focused, high-quality chunks.

**Why not naive chunking?** Analysis of the scraped data shows that blind 1000-char splitting would:
- Mix data across sections (exit load + tax in one chunk)
- Lose fund identity (no way to know which fund a chunk belongs to)
- Create noise chunks from the 40–166 holdings per fund

**Section-aware approach:**
- Parse each fund's cleaned content into logical sections:
  - **Fund Overview** — NAV, AUM, Expense Ratio, Rating, Min SIP
  - **Returns** — SIP returns (1Y, 3Y, 5Y, 10Y) + category rankings
  - **Top Holdings** — Only the top 10 holdings (ignore the rest)
  - **Exit Load & Tax** — Exit load rules + tax implications + stamp duty
  - **Fund Manager** — Manager name, education, experience
  - **About & Objective** — Fund description + investment objective
  - **Fund House Info** — Address, custodian, registrar
- **Prepend fund name** to every chunk for retrieval context (e.g., `"Aditya Birla Sun Life Liquid Fund — Exit Load: ..."`).
- Use `RecursiveCharacterTextSplitter` as a **fallback only** for sections exceeding 500 characters, with:
  - `chunk_size=500` characters.
  - `chunk_overlap=100` characters.
- Target output: **~7 focused chunks per fund × 5 funds = ~35 high-quality chunks**.
- Output a list of LangChain `Document` objects, each containing the chunk text and associated metadata.

### Task 2.3: Metadata Tagging
**File:** Integrated within `src/data_pipeline/chunker.py`
**Objective:** Attach provenance metadata to every chunk for citation and freshness tracking.
- For each chunk, attach the following metadata fields:
  - `source_url`: The original Groww URL the chunk was scraped from.
  - `last_updated`: The date of ingestion (e.g., `YYYY-MM-DD` format using the current date).
  - `chunk_index`: The sequential index of the chunk within its source document.
- Ensure metadata is preserved through the embedding and storage steps.

### Task 2.4: Embedding
**File:** `src/data_pipeline/embedder.py`
**Objective:** Convert text chunks into dense vector representations.

**Model choice: `BAAI/bge-small-en-v1.5`** (not large). Rationale:
- Corpus is only **77 chunks** (~200–500 chars each) — retrieval accuracy difference between small (MTEB: 62.17) and large (MTEB: 64.23) is negligible on small, well-structured corpora.
- Chunks are already **fund-name-prefixed and section-labeled**, making semantic matching easier.
- Queries are **simple factual lookups** (e.g., "What is the exit load?"), not complex reasoning.
- Small model is **~130MB vs ~1.3GB**, embedding is **~4x faster**, and local RAM is preserved for ChromaDB + FastAPI + Streamlit.

**Implementation details:**
- Load the model name from `.env` (`EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5`).
- Use `sentence-transformers` to load the model and provide an embedding function.
- Wrap the embedding function in a ChromaDB-compatible `EmbeddingFunction` class so it can be passed directly to the Chroma collection.
- The model outputs **384-dimensional vectors** optimized for cosine similarity search.
- **BGE query prefix:** At query time, prepend `"Represent this sentence: "` to the user's query for optimal retrieval (BGE models are trained with this instruction prefix). This prefix is NOT applied to document embeddings during ingestion.

### Task 2.5: Vector Database Storage
**File:** `src/data_pipeline/ingest.py`
**Objective:** Store the embedded chunks in ChromaDB for retrieval.
- Initialize a persistent ChromaDB client using the path from `.env` (`CHROMA_DB_DIR`).
- Create (or get) a collection named as per `.env` (`CHROMA_COLLECTION_NAME` = `mutual_fund_facts`).
- Use the BGE embedding function from Task 2.4 as the collection's embedding function.
- Insert all chunked documents with their text, metadata, and embeddings into the collection.
- Log the total number of documents stored for verification.
- This script serves as the **main entry point** for the entire ingestion pipeline, orchestrating Tasks 2.1 → 2.2/2.3 → 2.4 → 2.5 in sequence.

## Phase 3: Query Processing & RAG Core
**Objective:** Build the intent classifier, retrieval logic, prompt template, and RAG chain.

### Task 3.1: Intent Classification (Refusal Engine)
**File:** `src/rag_core/intent.py`
**Objective:** Block advisory/non-factual queries before retrieval.

**Strategy — Keyword heuristic (no LLM call needed):**
The corpus is narrow (5 mutual funds) and the advisory boundary is clear. A lightweight keyword-matching approach is sufficient and avoids an extra LLM round-trip.

- Maintain a list of **advisory trigger patterns**: `"should I invest"`, `"which is better"`, `"recommend"`, `"good investment"`, `"buy or sell"`, `"worth investing"`, `"safe to invest"`, `"best fund"`, `"compare"`, etc.
- If the query matches any trigger pattern (case-insensitive), return a **refusal response**:
  - Message: `"I can only provide factual information about mutual funds. For investment advice, please consult a SEBI-registered financial advisor."`
  - Link: `https://www.amfiindia.com/investor-corner/knowledge-center.html`
- Otherwise, classify as `factual` and proceed to retrieval.

### Task 3.2: Retrieval Strategy
**File:** `src/rag_core/retriever.py`
**Objective:** Retrieve the most relevant chunks from ChromaDB for a factual query.

**Strategy — informed by chunk analysis:**
- **77 total chunks** across 5 funds, 8 sections each.
- Average chunk is **340 chars** (range 70–500). The BGE-small model handles these comfortably.
- Fund names are **prepended to every chunk**, so semantic search naturally scores fund-specific queries higher.

**Implementation details:**
- Load the ChromaDB persistent client + collection (same config from `.env`).
- Use the `BGEEmbeddingFunction` from `embedder.py` as the collection's embedding function.
- **Top-K = 3**: With only 77 well-separated chunks, 3 results provide sufficient context without overwhelming the LLM's 3-sentence limit.
- **Query preprocessing**: Apply the BGE query prefix (`"Represent this sentence: "`) via the `embed_query()` method.
- **Optional metadata filter**: If the user query contains a recognizable fund name, apply a ChromaDB `where` filter on `fund_name` to restrict results to that fund. This prevents cross-fund contamination (e.g., returning Liquid Fund data for a Small Cap query).
- Return the retrieved `Document` objects with both `page_content` and `metadata` (for citation building).

### Task 3.3: Prompt Engineering
**File:** `src/rag_core/prompts.py`
**Objective:** Create the strict prompt template for the LLM.

The prompt must enforce all formatting constraints from the architecture:
```
You are a mutual fund FAQ assistant. Answer ONLY using the provided context.

Rules:
1. Maximum 3 sentences.
2. Include exactly 1 citation link from the source URLs provided.
3. End with: "Last updated from sources: <date>"
4. If the context does not contain the answer, say "I don't have information about that in my current data."
5. Never provide investment advice, recommendations, or opinions.
6. Stick to facts only.

Context:
{context}

Source URLs:
{sources}

Last updated: {last_updated}

Question: {question}
```

### Task 3.4: RAG Chain
**File:** `src/rag_core/chain.py`
**Objective:** Wire together intent classification → retrieval → prompt → LLM generation.

- Use `langchain-groq` with the `llama-3.3-70b-versatile` model (fast, capable, and fits our needs).
- Load `GROQ_API_KEY` from `.env`.
- The chain flow:
  1. **Intent check** → if advisory, return refusal immediately.
  2. **Retrieve** top-3 chunks from ChromaDB.
  3. **Build prompt** with retrieved context, source URLs, and date.
  4. **Generate** via Groq and return the formatted answer.

## Phase 4: FastAPI Backend Integration
**Objective:** Expose the RAG Core logic via a robust, RESTful API.
- **File:** `src/api/main.py`
- **Framework:** FastAPI
- **Details:**
  - Initialize a FastAPI application with CORS middleware enabled to allow frontend connections.
  - Instantiate the `RAGChain` (from `src.rag_core.chain`) on startup to ensure models and vector DB connections are held in memory.
  - Define a Pydantic request model (e.g., `ChatRequest`) that strictly accepts a string `query`.
  - Define a Pydantic response model (e.g., `ChatResponse`) containing the `answer` string.
  - Create a single `POST /chat` endpoint that:
    - Receives the `query`.
    - Passes it to `RAGChain.ask(query)`.
    - Handles exceptions gracefully, returning 500 errors if Groq or ChromaDB fails.
    - Returns the formatted answer.
  - Provide a `/health` endpoint for simple readiness checks.
  - Run the server using `uvicorn` (e.g., `uvicorn src.api.main:app --reload --port 8000`).

## Phase 5: Streamlit Frontend UI
**Objective:** Build a minimal, user-friendly chat interface for interacting with the backend API.
- **File:** `src/ui/app.py`
- **Framework:** Streamlit
- **Details:**
  - **Layout & Disclaimer:** 
    - Use `st.set_page_config` to title the app "Aditya Birla Mutual Fund Assistant".
    - Display a prominent, permanent banner at the top using `st.warning()`: **"Facts-only. No investment advice."**
  - **Chat Interface:**
    - Utilize Streamlit's native `st.chat_message` and `st.chat_input` widgets to simulate a conversational flow.
    - Maintain conversation history in `st.session_state.messages` to render previous turns.
  - **Example Prompts:**
    - Provide 3 pre-defined buttons (e.g., in a sidebar or above the chat) for quick querying:
      1. "What is the exit load for Liquid Fund?"
      2. "Who manages the Digital India Fund?"
      3. "What is the minimum SIP amount for Frontline Equity?"
    - Clicking a button should instantly populate the chat and trigger an API call.
  - **API Integration:**
    - Use the `requests` library to POST user queries to the FastAPI backend (`http://localhost:8000/chat`).
    - Display a loading spinner (`st.spinner`) while waiting for the Groq API generation.
    - Ensure robust error handling if the FastAPI backend is unreachable, displaying a user-friendly error message in the chat.

## Phase 6: Testing & Validation
**Objective:** Ensure strict compliance with the project constraints.
1. **Factual Testing:** Test factual queries (e.g., "What is the exit load for Birla Sun Life Cash Plus?") to ensure accurate retrieval and 3-sentence limits.
2. **Refusal Testing:** Test advisory queries (e.g., "Is Birla Sun Life Large Cap a good investment?") to verify the refusal engine kicks in.
3. **UI Verification:** Ensure the disclaimer is visible and no PII is requested.

## Phase 7: Data Ingestion Scheduler
**Objective:** Automate the execution of the data ingestion pipeline so the vector database remains up-to-date with the latest information from the sources on a daily basis.
- **Technology:** GitHub Actions
- **File:** `.github/workflows/ingest_data.yml`
- **Details:**
  - **Cron Schedule:** Create a GitHub Actions workflow that runs on a daily schedule (e.g., `cron: '0 0 * * *'` for midnight UTC).
  - **Environment Setup:** The workflow will check out the repository, set up Python, and install all necessary dependencies.
  - **Trigger Ingestion:** Execute `python src/data_pipeline/ingest.py` to run the scraping, chunking, embedding, and vector database update pipeline.
  - **State Persistence:** Automatically commit any updates or additions in the `chroma_db` directory and push them back to the repository (or remote storage) so the latest vectors are used by the deployment.
