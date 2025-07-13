"""
Main FastAPI application for the SafeGuard Insurance chatbot system.
Provides API endpoints for chat interactions with RAG capabilities using Ollama.
"""

import logging
from datetime import datetime
from typing import List, Optional

from chains import ChatChain
from config import Config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ollama_utils import OllamaManager
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SafeGuard Insurance AI Assistant",
    description="AI-powered customer service for SafeGuard Insurance with RAG capabilities",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize configuration
config = Config()

# Initialize Ollama manager
ollama_manager = OllamaManager(config.OLLAMA_BASE_URL, config.OLLAMA_MODEL)

# Initialize chat chain
chat_chain = ChatChain(config)


# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    use_rag: bool = True


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: datetime
    sources: Optional[List[str]] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    ollama_status: Optional[dict] = None


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint including Ollama status."""
    # Check Ollama health
    ollama_health = ollama_manager.health_check()

    # Determine overall status
    status = (
        "healthy"
        if ollama_health.get("ollama_running", False) and ollama_health.get("model_functional", False)
        else "degraded"
    )

    return HealthResponse(status=status, timestamp=datetime.now(), version="1.0.0", ollama_status=ollama_health)


@app.get("/health/ollama")
async def ollama_health():
    """Detailed Ollama health check endpoint."""
    return ollama_manager.health_check()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process an insurance-related chat message and return a response.

    Args:
        request: ChatRequest containing the user message and configuration

    Returns:
        ChatResponse with the bot's response and metadata
    """
    try:
        logger.info(f"Processing chat request: {request.message[:100]}...")

        # Process the message through the chat chain
        result = await chat_chain.process_message(
            message=request.message, conversation_id=request.conversation_id, use_rag=request.use_rag
        )

        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            timestamp=datetime.now(),
            sources=result.get("sources", []),
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Retrieve conversation history."""
    try:
        history = await chat_chain.get_conversation_history(conversation_id)
        return {"conversation_id": conversation_id, "history": history}
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        raise HTTPException(status_code=404, detail="Conversation not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
