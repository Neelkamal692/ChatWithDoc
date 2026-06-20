"""Base handler class for document processing."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss
from pydantic import BaseModel, Field
from langchain.docstore.document import Document
from typing import List
from langgraph.graph import StateGraph

from ..core.config import settings


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
            # Create state graph
            graph_builder = StateGraph(State)
            
            # Define retrieval step
            def retrieve(state: State):
                retrieved_docs = self.vector_store.similarity_search(state.question)
                return {"context": retrieved_docs}
            
            # Define generation step
            def generate(state: State):
                from langchain import hub
                prompt = hub.pull("rlm/rag-prompt")
                docs_content = "\n\n".join(doc.page_content for doc in state.context)
                messages = prompt.invoke({
                    "question": state.question,
                    "context": docs_content
                })
                response = self.llm.invoke(messages)
                return {"answer": response.content}
            
            # Build and compile the graph
            graph = graph_builder.add_sequence([retrieve, generate]).set_entry_point("retrieve").compile()
            
            # Execute the query
            response = graph.invoke({"question": query})
            
            return {
                "status": "success",
                "answer": response["answer"],
                "query": query
            }
        except Exception as e:
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
            FAISS vector store instance
        """
        embedding_dim = len(self.embedding_model.embed_query("test"))
        index = faiss.IndexFlatL2(embedding_dim)
        
        vector_store = FAISS(
            embedding_function=self.embedding_model,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        
        vector_store.add_documents(documents=documents)
        return vector_store
    
    def get_content(self) -> str:
        """Get extracted content (optional for some handlers)."""
        return ""
