"""
ChromaDB Retriever — Retrieves relevant chunks for factual queries.

Uses BGE query prefix and optional fund-name metadata filtering
to prevent cross-fund contamination.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import chromadb

from src.data_pipeline.embedder import get_embedding_function

load_dotenv()
logger = logging.getLogger(__name__)

# Known fund name fragments for metadata filtering
FUND_NAME_KEYWORDS = {
    "liquid": "Aditya Birla Sun Life Liquid Fund Direct Growth",
    "cash plus": "Aditya Birla Sun Life Liquid Fund Direct Growth",
    "digital india": "Aditya Birla Sun Life Digital India Fund Direct Growth",
    "new millennium": "Aditya Birla Sun Life Digital India Fund Direct Growth",
    "large cap": "Aditya Birla Sun Life Large Cap Direct Fund Growth",
    "midcap 150": "Aditya Birla Sun Life Nifty Midcap 150 Index Fund Direct Growth",
    "nifty midcap": "Aditya Birla Sun Life Nifty Midcap 150 Index Fund Direct Growth",
    "midcap index": "Aditya Birla Sun Life Nifty Midcap 150 Index Fund Direct Growth",
    "small cap": "Aditya Birla Sun Life Small Cap Fund Direct Growth",
    "small mid": "Aditya Birla Sun Life Small Cap Fund Direct Growth",
}


def _detect_fund_name(query: str) -> Optional[str]:
    """
    Checks if the query mentions a recognizable fund name.
    Returns the full canonical fund name or None.
    """
    query_lower = query.lower()
    for keyword, full_name in FUND_NAME_KEYWORDS.items():
        if keyword in query_lower:
            return full_name
    return None


class MutualFundRetriever:
    """
    Retrieves relevant chunks from ChromaDB for a given query.
    """
    def __init__(self, top_k: int = 3):
        self.top_k = top_k
        
        # Load config from .env
        db_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")
        collection_name = os.getenv("CHROMA_COLLECTION_NAME", "mutual_fund_facts")
        
        # Resolve absolute path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        db_path = os.path.join(project_root, db_dir.replace('./', ''))
        
        # Initialize ChromaDB
        self.embedding_func = get_embedding_function()
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(
            name=collection_name,
            embedding_function=self.embedding_func,
        )
        logger.info(f"Retriever initialized with {self.collection.count()} documents.")
    
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieves the top-K most relevant chunks for a query.
        
        Uses the BGE query prefix for optimal retrieval, and applies
        an optional metadata filter if a specific fund is mentioned.
        
        Returns a list of dicts with 'content', 'metadata', and 'distance'.
        """
        # Detect if the query mentions a specific fund
        fund_name = _detect_fund_name(query)
        
        # Build query embedding with the BGE prefix
        query_embedding = self.embedding_func.embed_query(query)
        
        # Build the query params
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": self.top_k,
        }
        
        # Apply fund-name filter if detected
        if fund_name:
            query_params["where"] = {"fund_name": fund_name}
            logger.info(f"Applying fund filter: {fund_name}")
        
        # Execute the query
        results = self.collection.query(**query_params)
        
        # Format results
        retrieved_docs = []
        if results and results["documents"]:
            for i, doc_text in enumerate(results["documents"][0]):
                retrieved_docs.append({
                    "content": doc_text,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                })
        
        logger.info(f"Retrieved {len(retrieved_docs)} chunks for query: '{query[:50]}...'")
        return retrieved_docs


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    logging.basicConfig(level=logging.INFO)
    
    retriever = MutualFundRetriever(top_k=3)
    
    test_queries = [
        "What is the exit load for the liquid fund?",
        "Who manages the small cap fund?",
        "What is the NAV of Aditya Birla Large Cap?",
        "Top holdings of Digital India fund",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        results = retriever.retrieve(query)
        for j, r in enumerate(results):
            print(f"  [{j+1}] Section: {r['metadata'].get('section','?')} | "
                  f"Fund: {r['metadata'].get('fund_name','?')[:40]} | "
                  f"Distance: {r['distance']:.4f}")
            print(f"      {r['content'][:120]}...")
