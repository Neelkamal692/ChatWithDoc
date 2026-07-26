"""Base handler class for document processing."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field

from ..core.config import settings

logger = logging.getLogger(__name__)


class State(BaseModel):
    """State model for RAG pipeline."""

    question: str = Field(..., description="Type your question here")
    context: List[Document] = Field(
        default_factory=list,
        description="A list of Document objects",
    )
    answer: str = Field(default="", description="Answer will be here")


class BaseHandler(ABC):
    """Abstract base class for document handlers."""

    def __init__(self):
        """Initialize the base handler."""
        self.llm = settings.get_llm()
        self.embedding_model = settings.get_embedding_model()
        self.embedding_dim = settings.EMBEDDING_DIM
        # Fixed: use PineconeVectorStore, not FAISS
        self.vector_store: Optional[PineconeVectorStore] = None
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
            # Fixed: correct StateGraph construction
            graph_builder = StateGraph(State)

            # Define retrieval step
            def retrieve(state: State):
                retrieved_docs = self.vector_store.similarity_search(state.question)
                return {"context": retrieved_docs}

            # Define generation step
            def generate(state: State):
                
                prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    "You are a helpful assistant. Answer the user's question using only "
                    "the provided context. If the answer is not in the context, say that "
                    "you do not know."
                ),
                (
                    "human",
                    "Context:\n{context}\n\nQuestion:\n{question}"
                ),
                    ])
                logger.info(f"Prompt pulled: {prompt}")
                docs_content = "\n\n".join(doc.page_content for doc in state.context)
                messages = prompt.invoke({
                    "question": state.question,
                    "context": docs_content
                })
                response = self.llm.invoke(messages)
                return {"answer": response.content}

            # Build graph with explicit nodes and edges
            graph_builder.add_node("retrieve", retrieve)
            graph_builder.add_node("generate", generate)
            graph_builder.add_edge("retrieve", "generate")
            graph_builder.set_entry_point("retrieve")
            graph = graph_builder.compile()

            # Execute the query
            response = graph.invoke({"question": query})

            return {
                "status": "success",
                "answer": response["answer"],
                "query": query
            }
        except Exception as e:
            logger.error(f"Query failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Error querying document: {str(e)}"
            }

    def _create_vector_store(self, documents: List[Document]) -> PineconeVectorStore:
        """
        Create a Pinecone vector store from documents.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            PineconeVectorStore instance
            
        Raises:
            Exception: If Pinecone initialization or indexing fails
        """
        logger.info("Creating Pinecone vector store")
        try:
            # Optional: verify connection (you can remove this if not needed)
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            # Just a sanity check to ensure the index exists
            if settings.PINECONE_INDEX_NAME not in pc.list_indexes().names():
                raise ValueError(f"Index '{settings.PINECONE_INDEX_NAME}' does not exist in Pinecone.")
            vector_store = PineconeVectorStore.from_documents(
                documents,
                embedding=self.embedding_model,
                index_name=settings.PINECONE_INDEX_NAME,
                namespace=settings.PINECONE_NAMESPACE or "default",
                pinecone_api_key=settings.PINECONE_API_KEY,
            )
            logger.info("Pinecone vector store created successfully")
            return vector_store
        except Exception as e:
            logger.error(f"Pinecone initialization failed: {e}", exc_info=True)
            # Re-raise so the caller knows it failed (no silent None)
            raise RuntimeError(f"Failed to create Pinecone vector store: {e}")

    # Optional: helper to assign the store (to be used in subclasses)
    def _initialize_store(self, documents: List[Document]) -> None:
        """Convenience method to create and assign the vector store."""
        self.vector_store = self._create_vector_store(documents)