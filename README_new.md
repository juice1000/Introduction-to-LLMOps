# Simple LLMOps with Ollama

A basic LLMOps application using FastAPI, LangChain, ChromaDB, and Ollama for a simple insurance chatbot.

## Features

- FastAPI web API with chat endpoints
- Ollama integration for local LLM inference
- ChromaDB for vector storage and retrieval
- Document loading and indexing
- RAG (Retrieval-Augmented Generation) capabilities
- Health checks and monitoring

## Prerequisites

- Python 3.12
- Ollama installed and running
- macOS (tested) or Linux

## Quick Start

1. **Clone and setup:**

   ```bash
   git clone <your-repo>
   cd Introduction-to-LLMOps
   ./setup.sh
   ```

2. **Add documents:**

   ```bash
   # Add your documents to data/documents/
   # Supports .txt and .md files
   ```

3. **Index documents:**

   ```bash
   python load_documents.py
   ```

4. **Start the API:**

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Test the API:**
   - Visit: http://localhost:8000/docs
   - Health check: http://localhost:8000/health
   - Chat: POST to http://localhost:8000/chat

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /info` - System information
- `POST /chat` - Chat with the bot

### Chat Request Example

```json
{
  "message": "How do I file an auto insurance claim?",
  "use_context": true
}
```

### Chat Response Example

```json
{
  "response": "To file an auto insurance claim, you should...",
  "sources": ["data/documents/insurance_faq.md"]
}
```

## Configuration

Edit `.env` file to configure:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma2:2b

# Vector Store
CHROMA_PERSIST_DIRECTORY=./data/vector_store

# App Settings
API_TITLE=Simple Insurance Chatbot
API_VERSION=1.0.0
```

## Directory Structure

```
├── app/
│   └── main.py              # FastAPI application
├── data/
│   ├── documents/           # Place your documents here
│   └── vector_store/        # ChromaDB storage
├── load_documents.py        # Document indexing script
├── setup.sh                 # Setup script
├── run.sh                   # Test script
├── requirements.txt         # Python dependencies
└── .env                     # Configuration
```

## Dependencies

Core packages:

- fastapi - Web framework
- langchain - LLM framework
- langchain_ollama - Ollama integration
- langchain_chroma - ChromaDB integration
- chromadb - Vector database
- python-dotenv - Environment management

## Development

- **Test environment:** `./run.sh`
- **Start development server:** `uvicorn app.main:app --reload`
- **Add new documents:** Add files to `data/documents/` and run `python load_documents.py`

## Troubleshooting

1. **Ollama not running:**

   ```bash
   ollama serve
   ```

2. **Model not available:**

   ```bash
   ollama pull gemma2:2b
   ```

3. **Dependencies issues:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Check health:**
   ```bash
   curl http://localhost:8000/health
   ```

## Next Steps

This is a basic setup. You can extend it by:

- Adding more document types
- Implementing user authentication
- Adding conversation memory
- Implementing evaluation frameworks
- Adding web UI
- Deploying to production

## License

MIT License
