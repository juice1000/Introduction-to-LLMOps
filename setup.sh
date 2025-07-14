#!/bin/bash

# Simple LLMOps Setup Script
# This script sets up a basic LLMOps environment with Python 3.12

set -e

echo "🚀 Setting up Simple LLMOps Environment..."

# Check if Python 3.12 is installed
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12 is required but not installed."
    echo "   Install with: brew install python@3.12"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment with Python 3.12..."
    python3.12 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOF
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:1b

# Vector Store
CHROMA_PERSIST_DIRECTORY=./data/vector_store

# App Settings
API_TITLE=Simple Insurance Chatbot
API_VERSION=1.0.0
EOF
    echo "✅ Created .env file with default settings"
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install Ollama first:"
    echo "   Visit: https://ollama.ai/download"
    echo "   Or run: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

# Check if Ollama is running
echo "🔍 Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "🚀 Starting Ollama service..."
    ollama serve &
    sleep 3
    
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "❌ Failed to start Ollama service. Please start it manually:"
        echo "   Run: ollama serve"
        exit 1
    fi
fi

# Pull the required model
echo "📥 Checking for Gemma 3:1B model..."
if ! ollama list | grep -q "gemma3:1b"; then
    echo "🤖 Pulling Gemma 3:1B model (this may take a few minutes)..."
    ollama pull gemma3:1b
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to pull Gemma 3:1B model. Please check your internet connection."
        exit 1
    fi
else
    echo "✅ Gemma 3:1B model is already available"
fi

# Test the model
echo "🧪 Testing Ollama model..."
test_response=$(ollama run gemma3:1b "Hello, respond with 'Working'")
if [[ "$test_response" == *"Working"* ]] || [[ "$test_response" == *"working"* ]]; then
    echo "✅ Ollama model is working correctly"
else
    echo "⚠️  Ollama model test uncertain, but continuing setup..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/vector_store data/documents

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add documents to data/documents/"
echo "2. Start the chatbot: uvicorn app.main:app --reload"
echo "3. Visit http://localhost:8000/docs to test the API"
echo ""
echo "🎯 Simple LLMOps Environment Ready!"
