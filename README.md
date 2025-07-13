# Introduction to LLMOps

A comprehensive example of Large Language Model Operations (LLMOps) featuring a production-ready chatbot with Retrieval-Augmented Generation (RAG) capabilities, evaluation frameworks, and operational best practices.

## 🎯 What is LLMOps?

LLMOps (Large Language Model Operations) is the practice of operationalizing and maintaining LLM-powered applications in production environments. This repository demonstrates key LLMOps concepts including:

- **Model Integration**: Seamless integration with OpenAI's GPT models
- **RAG Implementation**: Retrieval-Augmented Generation for knowledge-grounded responses
- **Evaluation & Testing**: Comprehensive evaluation using RAGAS and PromptFoo
- **Data Pipeline**: Document ingestion, processing, and vector storage
- **Monitoring**: Performance tracking and quality assessment
- **Deployment**: Docker-based deployment with vector database

## 🏗 Architecture Overview

```
├── app/                    # Core application logic
│   ├── main.py            # FastAPI app & API endpoints
│   ├── chains.py          # LangChain RAG implementation
│   ├── config.py          # Environment config & settings
│   └── prompts/           # Versioned prompt templates
├── data/                  # Documents for RAG
│   ├── raw/              # Original documents (PDF, Markdown, etc.)
│   └── processed/        # Cleaned, chunked documents
├── embedder/              # Vector store setup
│   ├── index.py          # Build and store embeddings
│   └── loader.py         # Load data from files
├── eval/                  # Evaluation & testing
│   ├── promptfoo.py      # PromptFoo test suite
│   ├── ragas_eval.py     # RAGAS evaluation script
│   └── test_samples.json # Ground truth Q&A pairs
├── scripts/               # CLI scripts for setup/debug
│   ├── build_index.py    # Run once to create vector index
│   └── seed_data.py      # Optional: populate DB
└── notebooks/             # Experiments & prototyping
    └── eval_playground.ipynb
```

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd Introduction-to-LLMOps

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file with your API keys:

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_api_key_here
```

### 3. Seed Data and Build Index

```bash
# Create sample documents (optional)
python scripts/seed_data.py

# Build vector index from documents
python scripts/build_index.py
```

### 4. Start the Application

```bash
# Start the FastAPI server
uvicorn app.main:app --reload

# Or use Docker Compose
docker-compose up
```

The API will be available at `http://localhost:8000`

## 📊 Evaluation & Testing

### RAGAS Evaluation

[RAGAS](https://github.com/explodinggradients/ragas) provides comprehensive metrics for RAG systems:

- **Faithfulness**: How well answers are grounded in retrieved context
- **Answer Relevancy**: How relevant answers are to questions
- **Context Precision**: How precise the retrieved context is
- **Context Recall**: How well retrieval captures relevant information

```bash
# Run RAGAS evaluation
python -c "
from eval.ragas_eval import RAGASEvaluator
from app.config import Config

config = Config()
evaluator = RAGASEvaluator(config)
# ... evaluation code
"
```

### PromptFoo Integration

[PromptFoo](https://promptfoo.dev/) enables systematic prompt testing:

```bash
# Install PromptFoo globally
npm install -g promptfoo

# Run evaluation suite
promptfoo eval promptfoo.yaml
```

### Interactive Evaluation

Use the Jupyter notebook for interactive evaluation:

```bash
jupyter lab notebooks/eval_playground.ipynb
```

## 🛠 Key Features

### 1. Retrieval-Augmented Generation (RAG)

- **Vector Store**: Chroma database for document embeddings
- **Document Loaders**: Support for PDF, Markdown, Text, JSON, CSV
- **Chunking Strategy**: Recursive character-based splitting
- **Retrieval**: Semantic similarity search with configurable top-k

### 2. API Endpoints

- `GET /`: Health check
- `POST /chat`: Process chat messages with optional RAG
- `GET /conversations/{id}`: Retrieve conversation history

### 3. Configuration Management

Environment-based configuration with sensible defaults:

```python
from app.config import Config

config = Config()
print(config.OPENAI_MODEL)  # gpt-3.5-turbo
print(config.VECTOR_STORE_PATH)  # ./data/vector_store
```

### 4. Document Processing Pipeline

```python
from embedder.loader import DataLoader
from embedder.index import DocumentEmbedder

# Load and process documents
loader = DataLoader("./data/raw", "./data/processed")
documents = loader.load_all_documents()
processed = loader.preprocess_documents(documents)

# Create embeddings
embedder = DocumentEmbedder(config)
vector_store = embedder.create_vector_store(processed)
```

## 📈 Monitoring & Observability

### Response Quality Metrics

- Response length and structure analysis
- Source attribution tracking
- Conversation flow monitoring
- Error rate and latency tracking

### Evaluation Automation

- Automated testing with ground truth datasets
- Continuous evaluation pipeline
- Performance regression detection
- A/B testing framework

## 🐳 Deployment

### Docker Compose

The included `docker-compose.yml` provides:

- **API Server**: FastAPI application
- **Vector Database**: Chroma for embeddings
- **PostgreSQL**: Conversation storage
- **Jupyter**: Development environment

```bash
docker-compose up -d
```

### Production Considerations

1. **Scaling**: Use container orchestration (Kubernetes)
2. **Security**: Implement authentication and rate limiting
3. **Monitoring**: Add APM tools (DataDog, New Relic)
4. **Caching**: Redis for response caching
5. **Load Balancing**: Nginx or cloud load balancers

## 🔧 Development

### Adding New Document Types

1. Create loader in `embedder/loader.py`
2. Update `DocumentEmbedder` in `embedder/index.py`
3. Add test cases in `eval/test_samples.json`

### Creating Custom Evaluations

1. Add test cases to `eval/test_samples.json`
2. Implement custom metrics in `eval/ragas_eval.py`
3. Update PromptFoo configuration in `eval/promptfoo.yaml`

### Extending the API

1. Add endpoints in `app/main.py`
2. Update chain logic in `app/chains.py`
3. Modify configuration in `app/config.py`

## 📚 Learning Resources

### LLMOps Concepts

- [LLMOps: Best Practices](https://neptune.ai/blog/llmops)
- [RAG Systems Guide](https://arxiv.org/abs/2005.11401)
- [Vector Databases Explained](https://www.pinecone.io/learn/vector-database/)

### Tools & Frameworks

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [RAGAS Documentation](https://docs.ragas.io/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Vector store not found**: Run `python scripts/build_index.py` first

**OpenAI API errors**: Check your API key in `.env` file

**Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

**Empty responses**: Verify documents exist in `data/raw/` directory

### Getting Help

- Check the issues section for common problems
- Review the documentation in each module
- Run the evaluation notebook for debugging
- Enable debug logging by setting `DEBUG=True` in `.env`
