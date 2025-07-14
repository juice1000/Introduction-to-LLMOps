"""
Configuration management for the LLMOps application.
Handles environment variables, API keys, and database paths.
"""

import os

from dotenv import load_dotenv

# Always load .env at the top
load_dotenv()

# Top-level config variables for easy import
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
CHROMA_PERSIST_DIRECTORY = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/chatbot.db")
API_TITLE = os.getenv("API_TITLE", "Simple Insurance Chatbot")
API_VERSION = os.getenv("API_VERSION", "1.0.0")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
RAW_DATA_PATH = os.getenv("RAW_DATA_PATH", "./data/raw")
PROCESSED_DATA_PATH = os.getenv("PROCESSED_DATA_PATH", "./data/processed")
EVAL_DATASET_PATH = os.getenv("EVAL_DATASET_PATH", "./eval/test_samples.json")
EVAL_OUTPUT_PATH = os.getenv("EVAL_OUTPUT_PATH", "./eval/results")
SYSTEM_PROMPT_PATH = os.getenv("SYSTEM_PROMPT_PATH", "./app/prompts/qa_prompt_v1.txt")

from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    OLLAMA_BASE_URL: str = OLLAMA_BASE_URL
    OLLAMA_MODEL: str = OLLAMA_MODEL
    TEMPERATURE: float = TEMPERATURE
    MAX_TOKENS: int = MAX_TOKENS
    VECTOR_STORE_PATH: str = CHROMA_PERSIST_DIRECTORY
    EMBEDDING_MODEL: str = EMBEDDING_MODEL
    DATABASE_URL: str = DATABASE_URL
    API_TITLE: str = API_TITLE
    API_VERSION: str = API_VERSION
    API_HOST: str = API_HOST
    API_PORT: int = API_PORT
    DEBUG: bool = DEBUG
    LOG_LEVEL: str = LOG_LEVEL
    RAW_DATA_PATH: str = RAW_DATA_PATH
    PROCESSED_DATA_PATH: str = PROCESSED_DATA_PATH
    EVAL_DATASET_PATH: str = EVAL_DATASET_PATH
    EVAL_OUTPUT_PATH: str = EVAL_OUTPUT_PATH
    SYSTEM_PROMPT_PATH: str = SYSTEM_PROMPT_PATH

    def __post_init__(self):
        os.makedirs(os.path.dirname(self.VECTOR_STORE_PATH), exist_ok=True)
        os.makedirs(self.RAW_DATA_PATH, exist_ok=True)
        os.makedirs(self.PROCESSED_DATA_PATH, exist_ok=True)
        os.makedirs(self.EVAL_OUTPUT_PATH, exist_ok=True)
        os.makedirs(os.path.dirname(self.SYSTEM_PROMPT_PATH), exist_ok=True)

    @classmethod
    def from_env_file(cls, env_file: str = ".env") -> "Config":
        if os.path.exists(env_file):
            load_dotenv(env_file)
        return cls()

    def to_dict(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}
