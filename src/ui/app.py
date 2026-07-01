import streamlit as st
import json
import os
import sys
from pathlib import Path

# Add the project root to sys.path so 'src' can be imported
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.rag_core.chain import RAGChain


# Load secrets into environment variables for underlying libraries (like Langchain) if deployed on Streamlit Cloud
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    if "EMBEDDING_MODEL_NAME" in st.secrets:
        os.environ["EMBEDDING_MODEL_NAME"] = st.secrets["EMBEDDING_MODEL_NAME"]
    if "CHROMA_DB_DIR" in st.secrets:
        os.environ["CHROMA_DB_DIR"] = st.secrets["CHROMA_DB_DIR"]
    if "CHROMA_COLLECTION_NAME" in st.secrets:
        os.environ["CHROMA_COLLECTION_NAME"] = st.secrets["CHROMA_COLLECTION_NAME"]
except FileNotFoundError:
    # Handle local execution if secrets.toml isn't used and python-dotenv is used instead
    pass

st.set_page_config(
    page_title="Aditya Birla Mutual Fund Assistant",
    page_icon="📈",
    layout="centered"
)

@st.cache_resource(show_spinner="Initializing RAG System...")
def get_rag_chain():
    return RAGChain()

try:
    rag_chain = get_rag_chain()
except Exception as e:
    st.error(f"Failed to initialize the RAG system: {e}")
    st.stop()

st.title("Aditya Birla Mutual Fund Assistant")
st.warning("⚠️ **Facts-only. No investment advice.** All answers are strictly based on factual data from official sources.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Example Queries
st.markdown("### Example Queries:")
col1, col2, col3 = st.columns(3)

def process_query(query):
    st.session_state.messages.append({"role": "user", "content": query})

with col1:
    if st.button("Exit load for Liquid Fund?"):
        process_query("What is the exit load for the liquid fund?")
with col2:
    if st.button("Who manages Digital India?"):
        process_query("Who manages the Digital India Fund?")
with col3:
    if st.button("Minimum SIP for Frontline?"):
        process_query("What is the minimum SIP amount for Frontline Equity?")

st.markdown("---")

# User Input
if prompt := st.chat_input("Ask a factual question about Aditya Birla Mutual Funds..."):
    process_query(prompt)

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# If the last message is from the user, generate a response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Searching mutual fund facts..."):
            query = st.session_state.messages[-1]["content"]
            try:
                result = rag_chain.process_query(query)
                answer = result.get("answer", "No answer received.")
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                error_msg = f"Error processing query: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
