from pdfHandler import PDFProcessor
from docHandler import DocProcessor
from txtHandler import TextProcessor
from webHandler import WebProcessor
from typing import Dict, Any, List

class DocumentManager:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.doc_processor = DocProcessor()
        self.txt_processor = TextProcessor()
        self.web_processor = WebProcessor()
        
        # Store multiple processed documents
        self.processed_documents = []  # List of {"processor": processor, "file_path": path, "content_type": type}
        self.all_content = ""  # Combined content for multi-document queries

    def process_document(self, file_path: str, content_type: str) -> Dict[str, Any]:
        try:
            result = {"status": "error", "message": "Unknown file type"}
            processor = None
            
            print(f"Processing file: {file_path} with content type: {content_type}")
            
            if content_type == "application/pdf":
                result = self.pdf_processor.process_pdf(file_path)
                processor = self.pdf_processor
            elif content_type == "application/msword":
                result = self.doc_processor.process_docx(file_path)
                processor = self.doc_processor
            elif content_type == "text/plain":
                result = self.txt_processor.process_text(file_path)
                processor = self.txt_processor
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                result = self.doc_processor.process_docx(file_path)
                processor = self.doc_processor
            
            if result["status"] == "success" and processor:
                # Add to processed documents list
                doc_info = {
                    "processor": processor,
                    "file_path": file_path,
                    "content_type": content_type,
                    "filename": file_path.split('/')[-1]  # Extract filename
                }
                self.processed_documents.append(doc_info)
                
                # Update combined content for multi-document queries
                # Assuming processors have a method to get content
                try:
                    if hasattr(processor, 'get_content'):
                        content = processor.get_content()
                        self.all_content += f"\n\n--- Document: {doc_info['filename']} ---\n{content}"
                except:
                    pass
                
                print(f"Document added to collection. Total documents: {len(self.processed_documents)}")
            
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def query_document(self, query: str) -> Dict[str, Any]:
        if not self.processed_documents:
            return {"status": "error", "message": "No documents processed"}
        
        print(f"Querying {len(self.processed_documents)} documents with question: {query}")
        
        try:
            # Strategy 1: Try to query each document and combine results
            all_responses = []
            
            for i, doc_info in enumerate(self.processed_documents):
                processor = doc_info["processor"]
                filename = doc_info["filename"]
                just_filename = filename.split('\\')[-1]

                # Query individual document
                try:
                    response = processor.query_response(query)
                    if response.get("status") == "success":
                        answer = response.get("answer", "")
                        if answer and answer.strip():
                            all_responses.append(f"From {just_filename}:\n {answer}")
                except Exception as e:
                    print(f"Error querying {filename}: {e}")
                    continue
            
            if not all_responses:
                return {"status": "error", "message": "No relevant information found in any documents"}
            
            # Combine all responses
            combined_answer = "\n\n".join(all_responses)
            
            return {
                "status": "success",
                "answer": combined_answer
            }
            
        except Exception as e:
            # Fallback: Use the last processed document
            print(f"Multi-document query failed, using last document: {e}")
            last_processor = self.processed_documents[-1]["processor"]
            return last_processor.query_response(query)

    def clear_documents(self):
        """Clear all previously processed documents"""
        self.processed_documents = []
        self.all_content = ""
        print("All documents cleared - ready for new uploads")

    def process_url(self, url: str) -> Dict[str, Any]:
        """Process a URL and add it to the document collection"""
        try:
            result = self.web_processor.process_url(url)
            if result["status"] == "success":
                # Add URL to processed documents
                doc_info = {
                    "processor": self.web_processor,
                    "file_path": url,
                    "content_type": "text/html",
                    "filename": f"webpage_{url.split('/')[-1] or 'index'}"
                }
                self.processed_documents.append(doc_info)
                
                # Update combined content
                try:
                    if hasattr(self.web_processor, 'get_content'):
                        content = self.web_processor.get_content()
                        self.all_content += f"\n\n--- Web Page: {url} ---\n{content}"
                except:
                    pass
                
                print(f"URL processed and added to collection: {url}")
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Get current status of processed documents"""
        return {
            "total_documents": len(self.processed_documents),
            "document_types": list(set([doc["content_type"] for doc in self.processed_documents])),
            "filenames": [doc["filename"] for doc in self.processed_documents]
        }