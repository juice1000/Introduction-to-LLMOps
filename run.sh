#!/bin/bash

# Simple LLMOps Run/Test Script
# This script tests if all services are running properly

set -e

echo "🚦 Running Simple LLMOps smoke test..."

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
if ! ollama list | grep -q "gemma3:12b"; then
    echo "❌ Gemma 3:12B model is not available. Please pull it with: ollama pull gemma3:12b"
    exit 1
fi

echo "🧪 Testing Ollama model response..."
test_response=$(ollama run gemma3:12b "Hello, respond with 'Working'")
if [[ "$test_response" == *"Working"* ]] || [[ "$test_response" == *"working"* ]]; then
    echo "✅ Ollama model is working correctly"
else
    echo "❌ Ollama model test failed."
    exit 1
fi

echo "🔍 Testing FastAPI app startup..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
uvicorn_pid=$!
sleep 5
if curl -s http://127.0.0.1:8000/docs | grep -q "Simple Insurance Chatbot"; then
    echo "✅ FastAPI app is running and docs are available"
else
    echo "❌ FastAPI app did not start correctly."
    kill $uvicorn_pid
    exit 1
fi
kill $uvicorn_pid

echo "✅ All checks passed! Environment is ready to use."
