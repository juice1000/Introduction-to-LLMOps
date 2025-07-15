"""MLflow auto-tracking for Ollama via OpenAI-compatible API."""

import mlflow
from openai import OpenAI

from app.config.config import OLLAMA_BASE_URL, OLLAMA_MODEL

# Enable auto-tracing for OpenAI
mlflow.openai.autolog()

# Set tracking URI and experiment
mlflow.set_tracking_uri("./mlruns")
mlflow.set_experiment("insurance_chatbot")

# Initialize OpenAI client for Ollama
client = OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="dummy")  # Required but not used by Ollama


def get_ollama_response(messages: list, temperature: float = 0.7, max_tokens: int = 1000):
    """Get response from Ollama using OpenAI-compatible API with auto-logging.

    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Response text from the model
    """
    response = client.chat.completions.create(
        model=OLLAMA_MODEL, messages=messages, temperature=temperature, max_tokens=max_tokens
    )
    return response.choices[0].message.content
