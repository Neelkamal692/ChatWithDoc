"""Configuration and settings for ChatWithDoc."""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # API Keys
    # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # LLM Configuration
    # LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash")
    # LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google_genai")

    # Embedding Configuration
    # EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    # EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))  # Gemini recommended default

    # Ollama Configuration
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    OLLAMA_CLOUD_MODEL = os.getenv("OLLAMA_CLOUD_MODEL")
    OLLAMA_CLOUD_BASE_URL = os.getenv("OLLAMA_CLOUD_BASE_URL")
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

    OLLAMA_LOCAL_MODEL = os.getenv("OLLAMA_LOCAL_MODEL")
    OLLAMA_LOCAL_BASE_URL = os.getenv("OLLAMA_LOCAL_BASE_URL")

    # Vector database 
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE")
    # Text Processing
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Application Settings
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploaded_files")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "26214400"))  # 25MB

    # API Settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    API_TITLE = "ChatWithDoc API"
    API_VERSION = "1.0.0"

    @staticmethod
    def get_llm():
        """Return the Ollama Cloud LLM, falling back to the local Ollama LLM on failure."""
        # health_check_llm = init_chat_model(
        #     Settings.OLLAMA_CLOUD_MODEL,
        #     model_provider="openai",
        #     base_url=Settings.OLLAMA_CLOUD_BASE_URL,
        #     api_key=Settings.OLLAMA_API_KEY,
        #     timeout=10,
        #     max_retries=0,
        # )
        try:
            
            return init_chat_model(
                Settings.OLLAMA_CLOUD_MODEL,
                model_provider="openai", # OpenAI-compatible provider — Ollama Cloud needs Bearer-token auth that ChatOllama doesn't support cleanly
                base_url=Settings.OLLAMA_CLOUD_BASE_URL,
                api_key=Settings.OLLAMA_API_KEY,
            )
        except Exception:
            return init_chat_model(
                Settings.OLLAMA_LOCAL_MODEL,
                model_provider="openai",
                base_url=Settings.OLLAMA_LOCAL_BASE_URL,
                api_key="ollama",
            )

    @staticmethod
    def get_embeddings():
        """Initialize and return the embeddings instance."""
        from ..embeddings.embedding_service import EmbeddingService

        return EmbeddingService.create()


# Singleton instance
settings = Settings()
