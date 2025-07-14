"""
Simple Insurance Chatbot API
A basic LLMOps application using FastAPI, LangChain, and Ollama
"""

import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title=os.getenv("API_TITLE", "Simple Insurance Chatbot"),
    version=os.getenv("API_VERSION", "1.0.0"),
    description="A simple insurance chatbot using Ollama and LangChain",
)

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:12b")
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/vector_store")

# Initialize LLM and embeddings
llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

embeddings = OllamaEmbeddings(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

# Initialize vector store
try:
    vector_store = Chroma(persist_directory=CHROMA_PERSIST_DIRECTORY, embedding_function=embeddings)
except Exception as e:
    print(f"Warning: Could not initialize vector store: {e}")
    vector_store = None


# Pydantic models
class ChatRequest(BaseModel):
    message: str
    use_context: bool = True


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None


class HealthResponse(BaseModel):
    status: str
    ollama_status: str
    vector_store_status: str


# Add CORS middleware
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {"message": "Simple Insurance Chatbot API", "docs": "/docs", "health": "/health"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""

    # Check Ollama
    try:
        test_response = llm.invoke("Hello")
        ollama_status = "healthy" if test_response else "unhealthy"
    except Exception as e:
        ollama_status = f"unhealthy: {str(e)}"

    # Check vector store
    if vector_store:
        try:
            # Try to get collection info
            vector_store._collection.count()
            vector_store_status = "healthy"
        except Exception as e:
            vector_store_status = f"unhealthy: {str(e)}"
    else:
        vector_store_status = "not initialized"

    overall_status = "healthy" if ollama_status == "healthy" else "degraded"

    return HealthResponse(status=overall_status, ollama_status=ollama_status, vector_store_status=vector_store_status)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint"""

    try:
        sources = []
        context = ""

        # Get context from vector store if available and requested
        if request.use_context and vector_store:
            try:
                # Search for relevant documents
                docs = vector_store.similarity_search(request.message, k=3)
                if docs:
                    context = "\n".join([doc.page_content for doc in docs])
                    sources = [doc.metadata.get("source", "unknown") for doc in docs]
            except Exception as e:
                print(f"Vector search error: {e}")

        # Prepare prompt
        if context:
            prompt = f"""You are a helpful insurance assistant. Use the following context to answer the user's question.

Context:
{context}

User Question: {request.message}

Answer based on the context provided. If the context doesn't contain relevant information, say so politely."""
        else:
            prompt = f"""You are a helpful insurance assistant. Answer the following question:

{request.message}"""

        # Get response from LLM
        response = llm.invoke(prompt)

        return ChatResponse(response=response, sources=sources if sources else None)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/info")
async def get_info():
    """Get system information"""
    doc_count = 0
    if vector_store:
        try:
            doc_count = vector_store._collection.count()
        except:
            doc_count = "unknown"

    return {
        "model": OLLAMA_MODEL,
        "base_url": OLLAMA_BASE_URL,
        "documents_indexed": doc_count,
        "vector_store_path": CHROMA_PERSIST_DIRECTORY,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
