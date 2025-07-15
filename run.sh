#!/bin/bash

# Simple LLMOps Run/Test Script
# This script tests if all services are running properly

set -e


# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ venv not found. Please run setup.sh first."
    exit 1
fi
source venv/bin/activate

echo "🔍 Checking Python dependencies..."
pip check || { echo "❌ Python dependencies are not satisfied."; exit 1; }

echo "🔍 Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed."
    exit 1
fi

echo "🔍 Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama service is not running. Please start it with: ollama serve"
    exit 1
fi

echo "🔍 Checking for Gemma model..."
if ! ollama list | grep -q "gemma3:1b"; then
    echo "❌ Gemma 3:1B model is not available. Please pull it with: ollama pull gemma3:1b"
    exit 1
fi

# echo "🧪 Testing Ollama model response..."
# test_response=$(ollama run gemma3:1b "Hello, respond with 'Working'")
# if [[ "$test_response" == *"Working"* ]] || [[ "$test_response" == *"working"* ]]; then
#     echo "✅ Ollama model is working correctly"
# else
#     echo "❌ Ollama model test failed."
#     exit 1
# fi

# Kill existing processes
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
lsof -ti:5000 | xargs kill -9 2>/dev/null || true

# Start MLflow in background
echo "📊 Starting MLflow server..."
mlflow server --backend-store-uri ./mlruns --host 127.0.0.1 --port 5000 --serve-artifacts &

echo "🚀 FastAPI app startup..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &

echo "🚀 Frontend app startup..."
cd chat-interface && npm run dev &

echo ""
echo "✅ Services started!"
echo "🌐 API: http://localhost:8000"
echo "📊 MLflow: http://localhost:5000"
echo "💻 Frontend: http://localhost:5173"

