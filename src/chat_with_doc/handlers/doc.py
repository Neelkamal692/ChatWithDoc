"""DOCX document handler."""

from typing import Dict, Any
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .base import BaseHandler


class DOCHandler(BaseHandler):
    """Handler for processing DOCX documents."""
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process a DOCX file and prepare it for querying.
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Dictionary with processing status and metadata
        """
        try:
            print(f"Processing DOCX file: {file_path}")
            
            # Document Loading
            loader = Docx2txtLoader(file_path)
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
                "message": "DOCX processed successfully",
                "num_pages": len(pages),
                "num_chunks": len(texts)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing DOCX: {str(e)}"
            }
