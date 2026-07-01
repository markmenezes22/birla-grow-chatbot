import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.rag_core.chain import RAGChain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to hold the RAG chain instance
rag_chain = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize RAGChain on startup
    global rag_chain
    try:
        logger.info("Initializing RAG Chain...")
        rag_chain = RAGChain()
        logger.info("RAG Chain initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize RAG Chain: {e}")
    yield
    # Clean up on shutdown if needed
    logger.info("Shutting down RAG API...")

app = FastAPI(
    title="Mutual Fund Assistant API",
    description="RAG backend API for factual mutual fund information.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

@app.get("/health")
async def health_check():
    """Simple readiness check."""
    status = "healthy" if rag_chain is not None else "degraded - RAG chain not initialized"
    return {"status": status}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a user query through the RAG chain."""
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG Chain is not initialized. Check server logs.")
    
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    try:
        logger.info(f"Received query: '{query}'")
        result = rag_chain.process_query(query)
        return ChatResponse(answer=result['answer'])
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
