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

# kill the uvicorn process if it's running
uvicorn_pid=$(pgrep -f "uvicorn app.main:app")
if [ -n "$uvicorn_pid" ]; then
    echo "🔍 Stopping existing FastAPI app..."
    kill $uvicorn_pid
    sleep 2
    if pgrep -f "uvicorn app.main:app" > /dev/null; then
        echo "❌ Failed to stop existing FastAPI app."
        exit 1
    fi
fi
echo "🔍 FastAPI app startup..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
echo "✅ All checks passed! Environment is ready to use."

