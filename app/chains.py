"""
LangChain-based chat chains for RAG implementation.
Handles conversation flow and retrieval-augmented generation.
"""

import asyncio
import uuid
from typing import Any, Dict, List, Optional

from config import Config
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from ollama_utils import OllamaManager


class ChatChain:
    """Main chat chain orchestrator for the LLMOps system."""

    def __init__(self, config: Config):
        self.config = config

        # Initialize Ollama manager
        self.ollama_manager = OllamaManager(config.OLLAMA_BASE_URL, config.OLLAMA_MODEL)

        # Initialize LLM with Ollama
        self.llm = Ollama(base_url=config.OLLAMA_BASE_URL, model=config.OLLAMA_MODEL, temperature=config.TEMPERATURE)

        # Initialize embeddings with HuggingFace (local)
        self.embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL, model_kwargs={"device": "cpu"})
        self.vector_store = self._load_vector_store()

        # Conversation memory storage
        self.conversations: Dict[str, ConversationBufferWindowMemory] = {}

        # Initialize the RAG chain
        self.rag_chain = self._create_rag_chain()

    def _load_vector_store(self) -> Optional[Chroma]:
        """Load the vector store from disk."""
        try:
            vector_store = Chroma(persist_directory=self.config.VECTOR_STORE_PATH, embedding_function=self.embeddings)
            return vector_store
        except Exception as e:
            print(f"Warning: Could not load vector store: {e}")
            return None

    def _create_rag_chain(self) -> Optional[ConversationalRetrievalChain]:
        """Create the RAG chain if vector store is available."""
        if not self.vector_store:
            return None

        # Custom prompt template for RAG
        prompt_template = """You are a helpful AI assistant. Use the following context to answer the user's question. 
        If you cannot answer the question based on the context, say so clearly.

        Context: {context}

        Chat History: {chat_history}
        
        Human: {question}
        
        Assistant:"""

        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "chat_history", "question"])

        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            combine_docs_chain_kwargs={"prompt": PROMPT},
            return_source_documents=True,
            verbose=True,
        )

        return chain

    def _get_or_create_memory(self, conversation_id: str) -> ConversationBufferWindowMemory:
        """Get or create conversation memory for a given conversation ID."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationBufferWindowMemory(
                k=10, return_messages=True, memory_key="chat_history"  # Keep last 10 exchanges
            )
        return self.conversations[conversation_id]

    async def process_message(
        self, message: str, conversation_id: Optional[str] = None, use_rag: bool = True
    ) -> Dict[str, Any]:
        """
        Process a user message and return a response.

        Args:
            message: User's input message
            conversation_id: Optional conversation ID for memory
            use_rag: Whether to use RAG capabilities

        Returns:
            Dictionary containing response, conversation_id, and sources
        """
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        # Get conversation memory
        memory = self._get_or_create_memory(conversation_id)

        try:
            if use_rag and self.rag_chain:
                # Use RAG chain
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.rag_chain({"question": message, "chat_history": memory.chat_memory.messages})
                )

                response = result["answer"]
                sources = [doc.metadata.get("source", "Unknown") for doc in result.get("source_documents", [])]

                # Update memory
                memory.chat_memory.add_user_message(message)
                memory.chat_memory.add_ai_message(response)

                return {"response": response, "conversation_id": conversation_id, "sources": sources}
            else:
                # Use basic LLM without RAG
                response = await asyncio.get_event_loop().run_in_executor(None, lambda: self.llm.predict(message))

                # Update memory
                memory.chat_memory.add_user_message(message)
                memory.chat_memory.add_ai_message(response)

                return {"response": response, "conversation_id": conversation_id, "sources": []}

        except Exception as e:
            # Fallback response
            fallback_response = f"I apologize, but I encountered an error: {str(e)}"
            return {"response": fallback_response, "conversation_id": conversation_id, "sources": []}

    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Retrieve conversation history for a given conversation ID."""
        if conversation_id not in self.conversations:
            return []

        memory = self.conversations[conversation_id]
        messages = memory.chat_memory.messages

        history = []
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                history.append({"user": messages[i].content, "assistant": messages[i + 1].content})

        return history
