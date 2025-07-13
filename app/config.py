"""
Configuration management for the LLMOps application.
Handles environment variables, API keys, and database paths.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration class for the LLMOps application."""

    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma3:12b")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))

    # Vector Store Configuration
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/chatbot.db")

    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Data Paths
    RAW_DATA_PATH: str = os.getenv("RAW_DATA_PATH", "./data/raw")
    PROCESSED_DATA_PATH: str = os.getenv("PROCESSED_DATA_PATH", "./data/processed")

    # Evaluation Configuration
    EVAL_DATASET_PATH: str = os.getenv("EVAL_DATASET_PATH", "./eval/test_samples.json")
    EVAL_OUTPUT_PATH: str = os.getenv("EVAL_OUTPUT_PATH", "./eval/results")

    # Prompt Configuration
    SYSTEM_PROMPT_PATH: str = os.getenv("SYSTEM_PROMPT_PATH", "./app/prompts/qa_prompt_v1.txt")

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(self.VECTOR_STORE_PATH), exist_ok=True)
        os.makedirs(self.RAW_DATA_PATH, exist_ok=True)
        os.makedirs(self.PROCESSED_DATA_PATH, exist_ok=True)
        os.makedirs(self.EVAL_OUTPUT_PATH, exist_ok=True)
        os.makedirs(os.path.dirname(self.SYSTEM_PROMPT_PATH), exist_ok=True)

    @classmethod
    def from_env_file(cls, env_file: str = ".env") -> "Config":
        """Load configuration from a .env file."""
        if os.path.exists(env_file):
            from dotenv import load_dotenv

            load_dotenv(env_file)
        return cls()

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}
