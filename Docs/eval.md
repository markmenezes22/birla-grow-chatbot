# Evaluation Plan (eval.md)

This document defines the evaluation criteria, testing methodologies, and success metrics for each phase outlined in the `Implementation-plan.md`. It ensures that each component of the Mutual Fund FAQ Assistant meets the strict project constraints.

---

## Phase 1: Project Setup & Environment

**Evaluation Criteria:**
- **Dependency Integrity:** All required packages (`fastapi`, `langchain`, `sentence-transformers`, `streamlit`, etc.) install successfully without version conflicts.
- **Environment Security:** The `.env` file containing the `GEMINI_API_KEY` is completely excluded from version control (verified via `.gitignore`).
- **Module Structure:** The codebase is correctly partitioned into `/data_pipeline`, `/rag_core`, `/api`, and `/ui`.

**Verification Method:** 
- Manual code review and running a generic script (`python -c "import langchain, fastapi, sentence_transformers"`) to verify imports.

---

## Phase 2: Data Ingestion Pipeline (Offline)

**Evaluation Criteria:**
- **Scraping Completeness:** The scraper must successfully extract textual data from exactly all 5 provided Groww URLs. No URLs should fail silently.
- **Chunk Quality:** Text must be split into logical chunks without breaking sentences in the middle unnecessarily. 
- **Metadata Accuracy:** Every single chunk stored in ChromaDB MUST contain a valid `source_url` (one of the 5 Groww URLs) and a `last_updated` timestamp.
- **Embedding Success:** The BGE model successfully converts the text chunks into dense vectors and stores them in ChromaDB.

**Verification Method:**
- Query the local ChromaDB collection directly and assert the total chunk count > 0.
- Sample 5 random chunks from the DB and assert that `metadata['source_url']` and `metadata['last_updated']` exist.

---

## Phase 3: Query Processing & RAG Core

**Evaluation Criteria:**
- **Retrieval Precision (Top-K):** For a known factual query (e.g., "What is the exit load of Birla Sun Life Cash Plus?"), the correct chunk containing the answer must appear in the top 3 results returned by ChromaDB.
- **Intent Classification (Refusal Engine):** 
  - **Factual Queries:** Must pass through to the RAG pipeline.
  - **Advisory Queries:** Must trigger the refusal response + AMFI link (e.g., "Should I invest in this?").
- **Generation Constraints (Gemini LLM):**
  - Output must **never** exceed 3 sentences.
  - Output must contain **exactly one** valid citation link from the metadata.
  - Output must append the exact footer: *"Last updated from sources: <date>"*
  - **Zero Hallucination:** If the DB lacks the answer, the LLM must explicitly state it does not know.

**Verification Method:**
- Create a unit test suite of 10 Factual Queries and 5 Advisory Queries. 
- Measure Retrieval Hit Rate (target: > 90%).
- Measure Refusal Accuracy (target: 100%).
- Programmatically check the LLM output length (count periods/newlines) and regex match for the citation and footer.

---

## Phase 4: API & Minimal UI Integration

**Evaluation Criteria:**
- **API Reliability:** The FastAPI `/chat` endpoint accepts a JSON payload and returns a valid response in under 5 seconds on average.
- **UI Constraints:**
  - The Streamlit app loads successfully.
  - The disclaimer (**"Facts-only. No investment advice."**) is prominently displayed and persistent.
  - The 3 example question buttons are functional and populate the chat interface.
- **Privacy Compliance:** The UI does not contain any input fields for PII (emails, phone numbers, account numbers) and does not persist chat logs to disk.

**Verification Method:**
- API load testing using tools like `Postman` or `curl`.
- Manual visual inspection of the Streamlit UI to ensure the disclaimer and example buttons meet requirements.

---

## Phase 5: End-to-End Testing & Validation

**Evaluation Criteria:**
- **System-wide Compliance:** The full user flow—from entering a query in the UI to receiving the Gemini-generated response—works seamlessly.
- **Edge Case Resilience:** The system gracefully handles the scenarios outlined in `edge-case.md` (e.g., ambiguous queries, massive text inputs).

**Verification Method:**
- Perform exploratory testing as an end-user.
- Execute the full test suite (Factual vs. Advisory) end-to-end through the FastAPI backend instead of just testing the LangChain core in isolation.
