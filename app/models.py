from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    use_context: bool = True


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None


class HealthResponse(BaseModel):
    status: str
    ollama_status: str
    vector_store_status: str
