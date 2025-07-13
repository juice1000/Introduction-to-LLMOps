#!/usr/bin/env python3
"""
Build vector index script for the LLMOps Insurance system.
Run this script to create or update the vector store with new documents.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import logging

from app.config import Config
from app.ollama_utils import OllamaManager
from embedder.index import DocumentEmbedder
from embedder.loader import DataLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Main function to build the vector index."""
    logger.info("Starting vector index build process for SafeGuard Insurance...")

    # Load configuration
    config = Config()

    # Check Ollama setup
    ollama_manager = OllamaManager(config.OLLAMA_BASE_URL, config.OLLAMA_MODEL)
    health_status = ollama_manager.health_check()

    if not health_status["ollama_running"]:
        logger.error("Ollama is not running. Please start Ollama service first.")
        return

    if not health_status["model_available"]:
        logger.info(f"Model {config.OLLAMA_MODEL} not available. Setting up...")
        if not ollama_manager.setup_model():
            logger.error("Failed to setup Ollama model")
            return
    config = Config()

    # Initialize components
    data_loader = DataLoader(config.RAW_DATA_PATH, config.PROCESSED_DATA_PATH)
    embedder = DocumentEmbedder(config)

    try:
        # Load all documents
        logger.info(f"Loading documents from {config.RAW_DATA_PATH}")
        documents = data_loader.load_all_documents()

        if not documents:
            logger.warning("No documents found to process!")
            return

        # Get and display statistics
        stats = data_loader.get_data_statistics(documents)
        logger.info(f"Loaded {stats['total_documents']} documents")
        logger.info(f"File types: {stats['file_types']}")
        logger.info(f"Total words: {stats['total_words']}")

        # Preprocess documents
        logger.info("Preprocessing documents...")
        processed_docs = data_loader.preprocess_documents(documents)

        # Save processed documents
        data_loader.save_processed_documents(processed_docs)

        # Convert to LangChain Document format
        langchain_docs = []
        for doc in processed_docs:
            from langchain.schema import Document as LangChainDoc

            langchain_docs.append(
                LangChainDoc(
                    page_content=doc["content"],
                    metadata={
                        "source": doc["source"],
                        "filename": doc["filename"],
                        "file_type": doc["file_type"],
                        "word_count": doc["word_count"],
                        "char_count": doc["char_count"],
                    },
                )
            )

        # Create vector store
        logger.info("Creating vector embeddings...")
        vector_store = embedder.create_vector_store(langchain_docs)

        # Get document statistics for embeddings
        embedding_stats = embedder.get_document_stats(langchain_docs)
        logger.info(f"Vector store created with {embedding_stats['total_documents']} document chunks")

        logger.info("✅ Vector index build completed successfully!")
        logger.info(f"Vector store saved to: {config.VECTOR_STORE_PATH}")

    except Exception as e:
        logger.error(f"❌ Error building vector index: {e}")
        raise


if __name__ == "__main__":
    main()
