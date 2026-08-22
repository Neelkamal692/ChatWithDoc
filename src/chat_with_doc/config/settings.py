"""Configuration and settings for ChatWithDoc."""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # LLM Configuration
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google_genai")

    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))  # Gemini recommended default

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

    def __init__(self):
        """Validate required settings."""
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

    @staticmethod
    def get_llm():
        """Initialize and return the LLM instance."""
        settings = Settings()
        return init_chat_model(
            settings.LLM_MODEL,
            model_provider=settings.LLM_PROVIDER
        )


# Singleton instance
settings = Settings()
