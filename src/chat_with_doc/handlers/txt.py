"""Text document handler."""

from typing import Dict, Any
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .base import BaseHandler


class TXTHandler(BaseHandler):
    """Handler for processing plain text documents."""
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process a text file and prepare it for querying.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dictionary with processing status and metadata
        """
        try:
            print(f"Processing text file: {file_path}")
            
            # Document Loading
            loader = TextLoader(file_path, encoding='utf-8')
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
                "message": "Text file processed successfully",
                "num_pages": len(pages),
                "num_chunks": len(texts)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing text file: {str(e)}"
            }
