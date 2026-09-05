"""Base handler class for document processing."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from ...config.settings import settings
from ...embeddings.embedding_service import EmbeddingService
from ...rag.graph import build_graph
from ...vectorstore.faiss_store import VectorStoreManager

logger = logging.getLogger(__name__)


class BaseHandler(ABC):
    """Abstract base class for document handlers."""

    def __init__(self):
        """Initialize the base handler."""
        self.llm = settings.get_llm()
        self.embedding_model = EmbeddingService.create()
        self.embedding_dim = settings.EMBEDDING_DIM
        # Fixed: use FAISS not pinecone becuse we are working on a very small scale 
        self.vector_store: Optional[FAISS] = None
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    @abstractmethod
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary with processing status and metadata
        """
        pass

    def query(self, query: str) -> Dict[str, Any]:
        """
        Query the processed document.
        
        Args:
            query: The question to ask about the document
            
        Returns:
            Dictionary with answer and status
        """
        if not self.vector_store:
            return {
                "status": "error",
                "message": "No document has been processed yet"
            }

        try:
            graph = build_graph(self.vector_store, self.llm)
            response = graph.invoke({"question": query})

            return {
                "status": "success",
                "answer": response["answer"],
                "query": query,
                "context": response['context']
            }
        except Exception as e:
            logger.error(f"Query failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Error querying document: {str(e)}"
            }

    def _create_vector_store(self, documents: List[Document]) -> FAISS:
        """
        Create a FAISS vector store from documents.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            FAISS instance
            
        Raises:
            Exception: If FAISS initialization or indexing fails
        """
        logger.info("Creating FAISS vector store")
        try:
            vector_store = VectorStoreManager(self.embedding_model).create(documents)
            logger.info("FAISS vector store created successfully")
            return vector_store
        except Exception as e:
            logger.error(f"FAISS initialization failed: {e}", exc_info=True)
            # Re-raise so the caller knows it failed (no silent None)
            raise RuntimeError(f"Failed to create FAISS vector store: {e}")

    # Optional: helper to assign the store (to be used in subclasses)
    def _initialize_store(self, documents: List[Document]) -> None:
        """Convenience method to create and assign the vector store."""
        self.vector_store = self._create_vector_store(documents)

