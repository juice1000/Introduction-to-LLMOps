#!/bin/bash

# LLMOps Setup Script
# This script sets up the entire LLMOps environment

set -e

echo "🚀 Setting up LLMOps Environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3.9 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env .env.example
    echo "⚠️  Please edit .env file and configure Ollama settings if needed"
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
    sleep 5
    
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "❌ Failed to start Ollama service. Please start it manually:"
        echo "   Run: ollama serve"
        exit 1
    fi
fi

# Pull the required model
echo "📥 Checking for Gemma 3:12B model..."
if ! ollama list | grep -q "gemma3:12b"; then
    echo "🤖 Pulling Gemma 3:12B model (this may take a few minutes)..."
    ollama pull gemma3:12b
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to pull Gemma 3:12B model. Please check your internet connection."
        exit 1
    fi
else
    echo "✅ Gemma 3:12B model is already available"
fi

# Test the model
echo "🧪 Testing Ollama model..."
test_response=$(ollama run gemma3:12b "Hello, please respond with 'Ollama is working'")
if [[ "$test_response" == *"working"* ]]; then
    echo "✅ Ollama model is working correctly"
else
    echo "⚠️  Ollama model test failed, but continuing setup..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/raw data/processed data/vector_store eval/results

# Run seed data script for insurance
echo "🌱 Seeding insurance sample data..."
python scripts/seed_data_insurance.py

# Build vector index
echo "🔍 Building vector index..."
python scripts/build_index.py

# Check if PromptFoo is installed
if command -v promptfoo &> /dev/null; then
    echo "✅ PromptFoo is available"
else
    echo "ℹ️  To install PromptFoo for evaluation: npm install -g promptfoo"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Ollama is running with Gemma 2B model"
echo "2. Start the insurance chatbot: uvicorn app.main:app --reload"
echo "3. Visit http://localhost:8000 to test the API"
echo "4. Use notebooks/eval_playground.ipynb for evaluation"
echo "5. Try asking: 'How do I file an auto insurance claim?'"
echo ""
echo "� Welcome to SafeGuard Insurance AI Assistant!"
