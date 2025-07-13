"""
Ollama utilities for LLM integration and health checks.
Handles Ollama connection, model availability, and initialization.
"""

import json
import logging
import subprocess
import time
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class OllamaManager:
    """Manages Ollama connection and model operations."""

    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "gemma3:12b"):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.api_url = f"{self.base_url}/api"

    def is_ollama_running(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models in Ollama."""
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching models: {e}")
            return []

    def is_model_available(self, model_name: str = None) -> bool:
        """Check if a specific model is available."""
        model_name = model_name or self.model_name
        models = self.get_available_models()
        return any(model.get("name", "").startswith(model_name) for model in models)

    def pull_model(self, model_name: str = None) -> bool:
        """Pull a model from Ollama registry."""
        model_name = model_name or self.model_name
        logger.info(f"Pulling model {model_name}...")

        try:
            response = requests.post(
                f"{self.api_url}/pull", json={"name": model_name}, stream=True, timeout=300  # 5 minutes timeout
            )

            if response.status_code == 200:
                # Stream the response to show progress
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "status" in data:
                                logger.info(f"Pull status: {data['status']}")
                        except json.JSONDecodeError:
                            pass

                logger.info(f"Model {model_name} pulled successfully")
                return True
            else:
                logger.error(f"Failed to pull model: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error pulling model: {e}")
            return False

    def test_model_generation(self, model_name: str = None, prompt: str = "Hello, how are you?") -> Optional[str]:
        """Test model generation with a simple prompt."""
        model_name = model_name or self.model_name

        try:
            response = requests.post(
                f"{self.api_url}/generate", json={"model": model_name, "prompt": prompt, "stream": False}, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                logger.error(f"Generation failed: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error testing generation: {e}")
            return None

    def setup_model(self, force_pull: bool = False) -> bool:
        """Set up the model for use."""
        logger.info(f"Setting up model: {self.model_name}")

        # Check if Ollama is running
        if not self.is_ollama_running():
            logger.error("Ollama is not running. Please start Ollama first.")
            return False

        # Check if model is available or needs to be pulled
        if not self.is_model_available() or force_pull:
            logger.info(f"Model {self.model_name} not found. Attempting to pull...")
            if not self.pull_model():
                logger.error(f"Failed to pull model {self.model_name}")
                return False
        else:
            logger.info(f"Model {self.model_name} is already available")

        # Test the model
        test_response = self.test_model_generation(prompt="Test message")
        if test_response is None:
            logger.error("Model test failed")
            return False

        logger.info(f"Model {self.model_name} is ready for use")
        logger.debug(f"Test response: {test_response[:100]}...")
        return True

    def get_model_info(self, model_name: str = None) -> Optional[Dict[str, Any]]:
        """Get detailed information about a model."""
        model_name = model_name or self.model_name
        models = self.get_available_models()

        for model in models:
            if model.get("name", "").startswith(model_name):
                return model
        return None

    def start_ollama_service(self) -> bool:
        """Attempt to start Ollama service (if installed)."""
        try:
            # Try to start Ollama as a background service
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Wait a bit for the service to start
            time.sleep(3)

            # Check if it's running
            return self.is_ollama_running()

        except FileNotFoundError:
            logger.error("Ollama not found. Please install Ollama first.")
            return False
        except Exception as e:
            logger.error(f"Error starting Ollama: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for Ollama setup."""
        health_status = {
            "ollama_running": False,
            "model_available": False,
            "model_functional": False,
            "available_models": [],
            "errors": [],
        }

        # Check if Ollama is running
        health_status["ollama_running"] = self.is_ollama_running()
        if not health_status["ollama_running"]:
            health_status["errors"].append("Ollama service is not running")
            return health_status

        # Get available models
        health_status["available_models"] = self.get_available_models()

        # Check if target model is available
        health_status["model_available"] = self.is_model_available()
        if not health_status["model_available"]:
            health_status["errors"].append(f"Model {self.model_name} is not available")

        # Test model functionality
        if health_status["model_available"]:
            test_response = self.test_model_generation(prompt="Hello")
            health_status["model_functional"] = test_response is not None
            if not health_status["model_functional"]:
                health_status["errors"].append("Model failed functionality test")

        return health_status
