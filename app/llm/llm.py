from langchain_ollama import OllamaEmbeddings, OllamaLLM

from app.config.config import EMBEDDING_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL

llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)
