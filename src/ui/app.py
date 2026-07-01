import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Aditya Birla Mutual Fund Assistant",
    page_icon="📈",
    layout="centered"
)

API_URL = "http://localhost:8000/chat"

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
                response = requests.post(API_URL, json={"query": query}, timeout=30)
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer received.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error from backend: HTTP {response.status_code}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except requests.exceptions.RequestException:
                error_msg = "Could not connect to the API. Is the FastAPI backend running?"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
