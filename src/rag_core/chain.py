"""
RAG Chain — Orchestrates Intent Classification, Retrieval, and LLM Generation.
"""
import os
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Add project root to sys.path so we can import 'src' when running this script directly
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.rag_core.intent import classify_intent
from src.rag_core.retriever import MutualFundRetriever
from src.rag_core.prompts import RAG_PROMPT_TEMPLATE

load_dotenv()
logger = logging.getLogger(__name__)

class RAGChain:
    """
    Main RAG orchestrator for Mutual Fund FAQ Assistant.
    """
    def __init__(self):
        # Initialize the Retriever
        self.retriever = MutualFundRetriever(top_k=3)
        
        # Initialize Groq LLM
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            logger.warning("GROQ_API_KEY is missing or invalid in .env")
            
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile", # Fast and capable open source model on Groq
            temperature=0.0, # Keep it factual
            max_tokens=256,  # 3 sentences don't need much
        )
        
        # Setup Prompt Template
        self.prompt = PromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        
        logger.info("RAG Chain initialized successfully.")

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query through the RAG pipeline.
        
        Returns a dict containing:
        - answer: The final string to show the user
        - intent: 'factual' or 'advisory'
        - sources: List of source URLs used
        """
        logger.info(f"Processing query: '{query}'")
        
        # 1. Intent Classification (Refusal Engine)
        intent, refusal_msg = classify_intent(query)
        if intent == "advisory":
            logger.info("Query blocked by refusal engine (Advisory).")
            return {
                "answer": refusal_msg,
                "intent": "advisory",
                "sources": []
            }
            
        # 2. Retrieval
        retrieved_docs = self.retriever.retrieve(query)
        
        if not retrieved_docs:
            return {
                "answer": "I don't have information about that in my current data.",
                "intent": "factual",
                "sources": []
            }
            
        # 3. Prompt Construction
        # Combine the context texts
        context_parts = []
        source_urls = set()
        latest_date = "Unknown"
        
        for doc in retrieved_docs:
            context_parts.append(doc["content"])
            source_urls.add(doc["metadata"].get("source_url", "Unknown source"))
            # Just take the first valid date found, they should all be the same (ingestion date)
            if doc["metadata"].get("last_updated"):
                latest_date = doc["metadata"]["last_updated"]
                
        context_text = "\n\n".join(context_parts)
        sources_text = "\n".join(list(source_urls))
        
        formatted_prompt = self.prompt.format(
            context=context_text,
            sources=sources_text,
            last_updated=latest_date,
            question=query
        )
        
        # 4. LLM Generation
        logger.info("Generating answer with Groq...")
        try:
            response = self.llm.invoke(formatted_prompt)
            answer_text = response.content.strip()
            
            return {
                "answer": answer_text,
                "intent": "factual",
                "sources": list(source_urls)
            }
        except Exception as e:
            logger.error(f"Error during LLM generation: {e}")
            return {
                "answer": "I encountered an error while processing your request. Please try again.",
                "intent": "error",
                "sources": []
            }


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    logging.basicConfig(level=logging.INFO)
    
    chain = RAGChain()
    
    test_queries = [
        "What is the exit load for the liquid fund?",
        "Should I invest in the small cap fund?",
        "Who manages the Digital India Fund and what is their experience?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Q: {query}")
        result = chain.process_query(query)
        print(f"A: {result['answer']}")
