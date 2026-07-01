import os
import sys
import logging
from dotenv import load_dotenv
import chromadb

# Add project root to sys.path so we can import 'src'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Import our pipeline modules
from src.data_pipeline.scraper import scrape_all_urls
from src.data_pipeline.chunker import chunk_all_funds
from src.data_pipeline.embedder import get_embedding_function

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Data Ingestion Pipeline...")
    
    # 1. Scrape raw data (Task 2.1)
    logger.info("--- Step 1: Scraping Data ---")
    raw_data = scrape_all_urls()
    if not raw_data:
        logger.error("No data scraped. Exiting.")
        return
        
    # 2. Chunk data (Task 2.2 & 2.3)
    logger.info("--- Step 2: Chunking Data & Tagging Metadata ---")
    documents = chunk_all_funds(raw_data)
    if not documents:
        logger.error("No chunks created. Exiting.")
        return
        
    # 3. Setup Embedding Function (Task 2.4)
    logger.info("--- Step 3: Loading Embedding Model ---")
    embedding_func = get_embedding_function()
    
    # 4. Store in Vector DB (Task 2.5)
    logger.info("--- Step 4: Storing in ChromaDB ---")
    
    # Get DB configuration from .env
    db_dir = os.getenv("CHROMA_DB_DIR", "./data/chroma_db")
    collection_name = os.getenv("CHROMA_COLLECTION_NAME", "mutual_fund_facts")
    
    # Initialize Chroma persistent client
    # Resolve absolute path for db_dir relative to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    db_path = os.path.join(project_root, db_dir.replace('./', ''))
    
    logger.info(f"Initializing persistent ChromaDB at: {db_path}")
    client = chromadb.PersistentClient(path=db_path)
    
    # Create or get the collection
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"} # Use cosine similarity
    )
    
    # Prepare data for ChromaDB
    texts = []
    metadatas = []
    ids = []
    
    for i, doc in enumerate(documents):
        texts.append(doc.page_content)
        metadatas.append(doc.metadata)
        # Create a unique ID for each chunk based on fund name and chunk index
        safe_fund_name = doc.metadata["fund_name"].replace(" ", "_").replace("&", "and").lower()
        chunk_id = f"{safe_fund_name}_chunk_{doc.metadata['chunk_index']}"
        ids.append(chunk_id)
        
    # Upsert data into ChromaDB in batches (though 77 chunks is small enough for one batch)
    logger.info(f"Adding {len(texts)} chunks to collection '{collection_name}'...")
    collection.upsert(
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )
    
    # Verification
    count = collection.count()
    logger.info(f"Success! Collection '{collection_name}' now contains {count} total documents.")
    logger.info("Data Ingestion Pipeline completed successfully.")

if __name__ == "__main__":
    main()
