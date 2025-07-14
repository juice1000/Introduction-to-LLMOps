"""
Simple Insurance Chatbot API
A basic LLMOps application using FastAPI, LangChain, and Ollama
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.config import API_TITLE, API_VERSION
from app.routes import router

origins = ["http://localhost:5173"]  # Vite dev server

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="A simple insurance chatbot using Ollama and LangChain",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
