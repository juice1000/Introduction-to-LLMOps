#!/usr/bin/env python3
"""
Seed data script for the LLMOps system.
Populates the raw data directory with sample documents for testing.
"""

import json
import os
from pathlib import Path


def create_sample_documents(data_path: str):
    """Create sample documents for testing the LLMOps system."""
    raw_data_path = Path(data_path) / "raw"
    raw_data_path.mkdir(parents=True, exist_ok=True)

    # Sample FAQ document
    faq_content = """# Frequently Asked Questions

## What is LLMOps?
LLMOps (Large Language Model Operations) is the practice of operationalizing and maintaining large language models in production environments. It encompasses the entire lifecycle of LLM-powered applications, from development and testing to deployment and monitoring.

## How does RAG work?
Retrieval-Augmented Generation (RAG) combines the power of retrieval systems with generative language models. It works by:
1. Retrieving relevant documents from a knowledge base
2. Using these documents as context for the language model
3. Generating responses based on both the query and retrieved context

## What are the benefits of using vector databases?
Vector databases offer several advantages:
- Semantic search capabilities
- Fast similarity searches
- Scalable storage for embeddings
- Support for real-time updates
- Integration with machine learning workflows

## How do you evaluate LLM performance?
LLM performance can be evaluated using various metrics:
- BLEU scores for text generation quality
- ROUGE scores for summarization tasks
- Human evaluation for subjective quality
- Task-specific metrics like accuracy or F1 score
- RAGAS metrics for RAG systems (faithfulness, relevancy, etc.)
"""

    with open(raw_data_path / "faq.md", "w") as f:
        f.write(faq_content)

    # Sample technical documentation
    tech_docs = """# LLMOps System Architecture

## Overview
This LLMOps system is designed to provide a robust, scalable chatbot solution with retrieval-augmented generation capabilities.

## Components
- **FastAPI Application**: REST API for chat interactions
- **Vector Store**: Chroma database for document embeddings
- **LangChain Integration**: For chain orchestration and memory management
- **Evaluation Framework**: RAGAS and PromptFoo integration
- **Data Pipeline**: Document loading and preprocessing

## API Endpoints
- GET /: Health check
- POST /chat: Process chat messages
- GET /conversations/{id}: Retrieve conversation history

## Configuration
The system uses environment variables for configuration:
- OPENAI_API_KEY: Required for OpenAI integration
- VECTOR_STORE_PATH: Path to vector database
- DATABASE_URL: Database connection string

## Deployment
The system can be deployed using:
- Docker containers
- Cloud platforms (AWS, GCP, Azure)
- Kubernetes clusters
"""

    with open(raw_data_path / "architecture.md", "w") as f:
        f.write(tech_docs)

    # Sample JSON data
    sample_data = [
        {
            "title": "Getting Started with LLMOps",
            "content": "LLMOps is becoming increasingly important as organizations deploy AI systems at scale. This guide covers the essential practices and tools needed for successful LLM operations.",
            "category": "tutorial",
            "tags": ["llmops", "ai", "deployment"],
        },
        {
            "title": "Best Practices for RAG Systems",
            "content": "Implementing effective RAG systems requires careful consideration of document chunking, embedding models, retrieval strategies, and evaluation metrics.",
            "category": "guide",
            "tags": ["rag", "retrieval", "best-practices"],
        },
        {
            "title": "Monitoring LLM Applications",
            "content": "Monitoring is crucial for maintaining LLM performance in production. Key metrics include response quality, latency, token usage, and user satisfaction.",
            "category": "operations",
            "tags": ["monitoring", "production", "metrics"],
        },
    ]

    with open(raw_data_path / "articles.json", "w") as f:
        json.dump(sample_data, f, indent=2)

    # Sample plain text document
    text_content = """LLMOps Best Practices

1. Version Control
   - Track model versions and configurations
   - Use Git for code and DVC for data/models
   - Maintain reproducible environments

2. Testing and Evaluation
   - Implement automated testing pipelines
   - Use multiple evaluation metrics
   - Conduct regular performance reviews

3. Monitoring and Observability
   - Track model performance in real-time
   - Monitor resource usage and costs
   - Set up alerting for anomalies

4. Security and Privacy
   - Implement proper access controls
   - Protect sensitive data and PII
   - Regular security audits

5. Scalability and Performance
   - Design for horizontal scaling
   - Optimize inference latency
   - Implement caching strategies
"""

    with open(raw_data_path / "best_practices.txt", "w") as f:
        f.write(text_content)

    print(f"✅ Sample documents created in {raw_data_path}")
    print("Files created:")
    print("- faq.md")
    print("- architecture.md")
    print("- articles.json")
    print("- best_practices.txt")


def main():
    """Main function to seed the data directory."""
    # Get the data path relative to the script location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_path = project_root / "data"

    create_sample_documents(str(data_path))


if __name__ == "__main__":
    main()
