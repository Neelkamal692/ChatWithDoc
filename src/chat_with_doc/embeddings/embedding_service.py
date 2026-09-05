"""Embedding model construction."""

from langchain_ollama import OllamaEmbeddings

from ..config.settings import settings


class EmbeddingService:
    """Build the configured local Ollama embedding model."""

    @staticmethod
    def create() -> OllamaEmbeddings:
        return OllamaEmbeddings(
            model=settings.OLLAMA_EMBEDDING_MODEL,
            base_url=settings.OLLAMA_HOST,
        )
