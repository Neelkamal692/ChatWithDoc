"""Configuration and settings for ChatWithDoc."""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # LLM Configuration
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google_genai")
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")

    
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
    
    @staticmethod
    def get_embedding_model():
        """Initialize and return the embedding model instance."""
        settings = Settings()
        return GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL
        )


# Singleton instance
settings = Settings()
