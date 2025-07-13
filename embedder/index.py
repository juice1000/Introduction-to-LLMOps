"""
Document embedding and vector store management.
Handles the creation and maintenance of embeddings for RAG.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from langchain.document_loaders import TextLoader, UnstructuredFileLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)


class DocumentEmbedder:
    """Handles document loading, processing, and embedding."""

    def __init__(self, config):
        self.config = config
        self.embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL, model_kwargs={"device": "cpu"})
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def load_documents(self, data_path: str) -> List[Document]:
        """Load documents from a directory."""
        documents = []
        data_dir = Path(data_path)

        if not data_dir.exists():
            logger.warning(f"Data directory {data_path} does not exist")
            return documents

        # Supported file types
        loaders = {".txt": TextLoader, ".md": UnstructuredFileLoader, ".pdf": UnstructuredFileLoader}

        for file_path in data_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in loaders:
                try:
                    loader_class = loaders[file_path.suffix.lower()]
                    loader = loader_class(str(file_path))
                    docs = loader.load()

                    # Add metadata
                    for doc in docs:
                        doc.metadata.update(
                            {"source": str(file_path), "file_type": file_path.suffix, "file_name": file_path.name}
                        )

                    documents.extend(docs)
                    logger.info(f"Loaded {len(docs)} documents from {file_path}")

                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")

        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        return self.text_splitter.split_documents(documents)

    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """Create a vector store from documents."""
        if not documents:
            raise ValueError("No documents provided for vector store creation")

        # Split documents into chunks
        chunks = self.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")

        # Create vector store
        vector_store = Chroma.from_documents(
            documents=chunks, embedding=self.embeddings, persist_directory=self.config.VECTOR_STORE_PATH
        )

        # Persist the vector store
        vector_store.persist()
        logger.info(f"Vector store created and saved to {self.config.VECTOR_STORE_PATH}")

        return vector_store

    def update_vector_store(self, new_documents: List[Document]) -> Chroma:
        """Update an existing vector store with new documents."""
        # Load existing vector store
        vector_store = Chroma(persist_directory=self.config.VECTOR_STORE_PATH, embedding_function=self.embeddings)

        # Split new documents
        chunks = self.split_documents(new_documents)

        # Add new documents
        vector_store.add_documents(chunks)
        vector_store.persist()

        logger.info(f"Added {len(chunks)} new chunks to vector store")
        return vector_store

    def get_document_stats(self, documents: List[Document]) -> Dict[str, Any]:
        """Get statistics about the document collection."""
        if not documents:
            return {}

        file_types = {}
        total_chars = 0
        sources = set()

        for doc in documents:
            # Count file types
            file_type = doc.metadata.get("file_type", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1

            # Count characters
            total_chars += len(doc.page_content)

            # Collect sources
            sources.add(doc.metadata.get("source", "unknown"))

        return {
            "total_documents": len(documents),
            "total_characters": total_chars,
            "unique_sources": len(sources),
            "file_types": file_types,
            "avg_doc_length": total_chars / len(documents) if documents else 0,
        }
