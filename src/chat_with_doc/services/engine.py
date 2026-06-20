"""Document processing engine."""

from typing import Dict, Any, List
from ..handlers import PDFHandler, DOCHandler, TXTHandler, WebHandler


class DocumentEngine:
    """Engine for managing and processing multiple documents."""
    
    def __init__(self):
        """Initialize the document engine."""
        self.pdf_handler = PDFHandler()
        self.doc_handler = DOCHandler()
        self.txt_handler = TXTHandler()
        self.web_handler = WebHandler()
        
        # Store processed documents
        self.processed_documents: List[Dict[str, Any]] = []
        self.all_content = ""
    
    def process_document(self, file_path: str, content_type: str) -> Dict[str, Any]:
        """
        Process a document based on content type.
        
        Args:
            file_path: Path to the document
            content_type: MIME type of the document
            
        Returns:
            Dictionary with processing status
        """
        try:
            result = {"status": "error", "message": "Unknown file type"}
            handler = None
            
            print(f"Processing file: {file_path} with content type: {content_type}")
            
            if content_type == "application/pdf":
                result = self.pdf_handler.process(file_path)
                handler = self.pdf_handler
            elif content_type == "application/msword":
                result = self.doc_handler.process(file_path)
                handler = self.doc_handler
            elif content_type == "text/plain":
                result = self.txt_handler.process(file_path)
                handler = self.txt_handler
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                result = self.doc_handler.process(file_path)
                handler = self.doc_handler
            
            if result["status"] == "success" and handler:
                # Add to processed documents list
                doc_info = {
                    "handler": handler,
                    "file_path": file_path,
                    "content_type": content_type,
                    "filename": file_path.split('/')[-1]
                }
                self.processed_documents.append(doc_info)
                
                # Update combined content
                try:
                    if hasattr(handler, 'get_content'):
                        content = handler.get_content()
                        self.all_content += f"\n\n--- Document: {doc_info['filename']} ---\n{content}"
                except:
                    pass
                
                print(f"Document added to collection. Total: {len(self.processed_documents)}")
            
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def query_documents(self, query: str) -> Dict[str, Any]:
        """
        Query all processed documents.
        
        Args:
            query: The question to ask
            
        Returns:
            Dictionary with combined answers
        """
        if not self.processed_documents:
            return {"status": "error", "message": "No documents processed"}
        
        print(f"Querying {len(self.processed_documents)} documents with: {query}")
        
        try:
            all_responses = []
            
            for doc_info in self.processed_documents:
                handler = doc_info["handler"]
                filename = doc_info["filename"].split('\\')[-1]
                
                try:
                    response = handler.query(query)
                    if response.get("status") == "success":
                        answer = response.get("answer", "")
                        if answer and answer.strip():
                            all_responses.append(f"From {filename}:\n{answer}")
                except Exception as e:
                    print(f"Error querying {filename}: {e}")
                    continue
            
            if not all_responses:
                return {"status": "error", "message": "No relevant information found"}
            
            combined_answer = "\n\n".join(all_responses)
            return {"status": "success", "answer": combined_answer}
        
        except Exception as e:
            print(f"Multi-document query failed: {e}")
            if self.processed_documents:
                last_handler = self.processed_documents[-1]["handler"]
                return last_handler.query(query)
            return {"status": "error", "message": str(e)}
    
    def process_url(self, url: str) -> Dict[str, Any]:
        """
        Process a URL and add to documents.
        
        Args:
            url: URL to process
            
        Returns:
            Dictionary with processing status
        """
        try:
            result = self.web_handler.process(url)
            if result["status"] == "success":
                doc_info = {
                    "handler": self.web_handler,
                    "file_path": url,
                    "content_type": "text/html",
                    "filename": f"webpage_{url.split('/')[-1] or 'index'}"
                }
                self.processed_documents.append(doc_info)
                
                try:
                    if hasattr(self.web_handler, 'get_content'):
                        content = self.web_handler.get_content()
                        self.all_content += f"\n\n--- Web Page: {url} ---\n{content}"
                except:
                    pass
                
                print(f"URL processed: {url}")
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def clear_documents(self) -> Dict[str, Any]:
        """Clear all processed documents."""
        self.processed_documents = []
        self.all_content = ""
        print("All documents cleared")
        return {"status": "success", "message": "All documents cleared"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of processed documents."""
        return {
            "total_documents": len(self.processed_documents),
            "document_types": list(set([doc["content_type"] for doc in self.processed_documents])),
            "filenames": [doc["filename"] for doc in self.processed_documents]
        }
