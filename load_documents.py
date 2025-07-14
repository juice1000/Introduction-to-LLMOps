"""
Simple document loader and indexer
Loads documents from data/documents and creates a vector index
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_ollama import OllamaEmbeddings

load_dotenv()

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:12b")
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/vector_store")
DOCUMENTS_PATH = "./data/documents"


def load_documents():
    """Load documents from the documents directory"""
    documents = []
    docs_path = Path(DOCUMENTS_PATH)

    if not docs_path.exists():
        print(f"Documents directory {DOCUMENTS_PATH} not found. Creating it...")
        docs_path.mkdir(parents=True, exist_ok=True)
        return documents

    # Support txt and md files
    for file_path in docs_path.rglob("*.txt"):
        try:
            loader = TextLoader(str(file_path))
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = str(file_path)
                doc.metadata["file_type"] = "txt"
            documents.extend(docs)
            print(f"Loaded {len(docs)} documents from {file_path}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    for file_path in docs_path.rglob("*.md"):
        try:
            loader = UnstructuredMarkdownLoader(str(file_path))
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = str(file_path)
                doc.metadata["file_type"] = "md"
            documents.extend(docs)
            print(f"Loaded {len(docs)} documents from {file_path}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return documents


def create_vector_store(documents):
    """Create vector store from documents"""
    if not documents:
        print("No documents to index")
        return None

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks")

    # Initialize embeddings
    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

    # Create vector store
    vector_store = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=CHROMA_PERSIST_DIRECTORY
    )

    print(f"Created vector store with {len(chunks)} chunks")
    return vector_store


def main():
    """Main function"""
    print("🔍 Loading documents...")
    documents = load_documents()

    if not documents:
        print("No documents found. Add .txt or .md files to data/documents/")
        return

    print(f"📚 Found {len(documents)} documents")

    print("🔧 Creating vector store...")
    vector_store = create_vector_store(documents)

    if vector_store:
        print("✅ Vector store created successfully!")
    else:
        print("❌ Failed to create vector store")


if __name__ == "__main__":
    main()
