from langchain_chroma import Chroma

from app.config.config import CHROMA_PERSIST_DIRECTORY
from app.llm.llm import embeddings

try:
    vector_store = Chroma(persist_directory=CHROMA_PERSIST_DIRECTORY, embedding_function=embeddings)
except Exception as e:
    print(f"Warning: Could not initialize vector store: {e}")
    vector_store = None


def get_context(message: str, k: int = 3):
    sources = []
    context = ""
    if vector_store:
        try:
            docs = vector_store.similarity_search(message, k=k)
            if docs:
                context = "\n".join([doc.page_content for doc in docs])
                sources = [doc.metadata.get("source", "unknown") for doc in docs]
        except Exception as e:
            print(f"Vector search error: {e}")
    return context, sources
