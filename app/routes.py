from fastapi import APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import (
    API_TITLE,
    API_VERSION,
    CHROMA_PERSIST_DIRECTORY,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)
from .llm import embeddings, llm
from .models import ChatRequest, ChatResponse, HealthResponse
from .vector_store import get_context, vector_store

router = APIRouter()


@router.get("/", response_model=dict)
async def root():
    return {"message": "Simple Insurance Chatbot API", "docs": "/docs", "health": "/health"}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        test_response = llm.invoke("Hello")
        ollama_status = "healthy" if test_response else "unhealthy"
    except Exception as e:
        ollama_status = f"unhealthy: {str(e)}"
    if vector_store:
        try:
            vector_store._collection.count()
            vector_store_status = "healthy"
        except Exception as e:
            vector_store_status = f"unhealthy: {str(e)}"
    else:
        vector_store_status = "not initialized"
    overall_status = "healthy" if ollama_status == "healthy" else "degraded"
    return HealthResponse(status=overall_status, ollama_status=ollama_status, vector_store_status=vector_store_status)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        sources = []
        context = ""
        embeddings_supported = True
        try:
            _ = embeddings.embed_query("test")
        except Exception as e:
            print(f"Embeddings not supported: {e}")
            embeddings_supported = False
        print(
            f"Using context: {request.use_context}, embeddings supported: {embeddings_supported}, vector_store:  {vector_store}"
        )
        if request.use_context and vector_store and embeddings_supported:
            context, sources = get_context(request.message)
        if context:
            prompt = f"""You are a helpful insurance assistant. Use the following context to answer the user's question.\n\nContext:\n{context}\n\nUser Question: {request.message}\n\nAnswer based on the context provided. If the context doesn't contain relevant information, say so politely."""
        else:
            prompt = f"""You are a helpful insurance assistant. Answer the following question:\n\n{request.message}"""
        response = llm.invoke(prompt)
        return ChatResponse(response=response, sources=sources if sources else None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.get("/info")
async def get_info():
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
