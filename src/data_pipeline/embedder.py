import os
import logging
from typing import List
from dotenv import load_dotenv
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from sentence_transformers import SentenceTransformer

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger(__name__)

class BGEEmbeddingFunction(EmbeddingFunction):
    """
    ChromaDB compatible embedding function using BAAI/bge-small-en-v1.5 
    via sentence-transformers.
    """
    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
            
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
    def __call__(self, input: Documents) -> Embeddings:
        """
        Embeds a list of text documents.
        This is called internally by ChromaDB during add() or query().
        """
        # sentence-transformers encode returns a numpy array, we convert to list
        embeddings = self.model.encode(input, normalize_embeddings=True)
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """
        Special method for querying. BGE models require a specific prefix 
        for queries to achieve optimal retrieval performance.
        """
        prefixed_query = f"Represent this sentence: {query}"
        embedding = self.model.encode(prefixed_query, normalize_embeddings=True)
        return embedding.tolist()

def get_embedding_function() -> EmbeddingFunction:
    """
    Factory function to instantiate and return the embedding function.
    """
    return BGEEmbeddingFunction()

if __name__ == "__main__":
    # Configure basic logging for test
    logging.basicConfig(level=logging.INFO)
    
    logger.info("Testing BGEEmbeddingFunction...")
    embedder = get_embedding_function()
    
    # Test document embedding
    sample_docs = ["This is a test document.", "Here is another fact about mutual funds."]
    doc_embeddings = embedder(sample_docs)
    logger.info(f"Generated {len(doc_embeddings)} document embeddings.")
    logger.info(f"Embedding dimension: {len(doc_embeddings[0])}")
    
    # Test query embedding
    sample_query = "What is the exit load?"
    query_embedding = embedder.embed_query(sample_query)
    logger.info(f"Generated query embedding with dimension: {len(query_embedding)}")
