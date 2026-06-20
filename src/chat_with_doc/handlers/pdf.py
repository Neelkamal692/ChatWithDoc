"""PDF document handler."""

from typing import Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .base import BaseHandler


class PDFHandler(BaseHandler):
    """Handler for processing PDF documents."""
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process a PDF file and prepare it for querying.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary with processing status and metadata
        """
        try:
            print(f"Processing PDF file: {file_path}")
            
            # Document Loading
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            # Text Splitting
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            texts = text_splitter.split_documents(pages)
            
            # Create vector store
            self.vector_store = self._create_vector_store(texts)
            
            return {
                "status": "success",
                "message": "PDF processed successfully",
                "num_pages": len(pages),
                "num_chunks": len(texts)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing PDF: {str(e)}"
            }
