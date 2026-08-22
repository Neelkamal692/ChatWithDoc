"""Embedding model construction."""

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from ..config.settings import settings


class EmbeddingService:
    """Build the configured Gemini embedding model."""

    @staticmethod
    def create() -> GoogleGenerativeAIEmbeddings:
        return GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            output_dimensionality=settings.EMBEDDING_DIM,
            google_api_key=settings.GOOGLE_API_KEY,
        )
