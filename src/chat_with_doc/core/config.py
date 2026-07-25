"""Configuration and settings for ChatWithDoc."""

import os
import logging
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()
logger = logging.getLogger(__name__)
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

    # @staticmethod
    # def get_embedding_model():
    #     """Initialize and return the embedding model instance."""
    #     settings = Settings()
    #     return GoogleGenerativeAIEmbeddings(
    #         model=settings.EMBEDDING_MODEL,
    #         output_dimensionality=settings.EMBEDDING_DIM
    #     )
    @staticmethod
    def get_embedding_model():
        settings_instance = Settings()

        embedding_model = GoogleGenerativeAIEmbeddings(
            model=settings_instance.EMBEDDING_MODEL,
            output_dimensionality=settings_instance.EMBEDDING_DIM,
            google_api_key=settings_instance.GOOGLE_API_KEY,
        )

        logger.info("Embedding object: %s", embedding_model)
        logger.info(
            "Object output_dimensionality: %s",
            getattr(embedding_model, "output_dimensionality", None),
        )

        test_vector = embedding_model.embed_query("dimension test")

        logger.info(
            "Requested dimension=%s, actual dimension=%s",
            settings_instance.EMBEDDING_DIM,
            len(test_vector),
        )

        if len(test_vector) != settings_instance.EMBEDDING_DIM:
            raise RuntimeError(
                f"Embedding model returned {len(test_vector)} dimensions, "
                f"but {settings_instance.EMBEDDING_DIM} were requested."
            )

        return embedding_model


# Singleton instance
settings = Settings()
