
from pdfHandler import PDFProcessor
from docHandler import DocProcessor
from txtHandler import TextProcessor
from webHandler import WebProcessor
from typing import Dict, Any

class DocumentManager:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.doc_processor = DocProcessor()
        self.txt_processor = TextProcessor()
        self.web_processor = WebProcessor()
        self.current_processor = None
        self.current_document = None

    def process_document(self, file_path: str, content_type: str) -> Dict[str, Any]:
        try:
            result = {"status": "error", "message": "Unknown file type"}  # Initialize result
            print(f"Processing file: {file_path} with content type: {content_type}")
            if content_type == "application/pdf":
                result = self.pdf_processor.process_pdf(file_path)
                if result["status"] == "success":
                    self.current_processor = self.pdf_processor
            elif content_type == "application/msword":
                result = self.doc_processor.process_docx(file_path)
                if result["status"] == "success":
                    self.current_processor = self.doc_processor
            elif content_type == "text/plain":
                result = self.txt_processor.process_text(file_path)
                if result["status"] == "success":
                    self.current_processor = self.txt_processor
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                result = self.doc_processor.process_docx(file_path)
                if result["status"] == "success":
                    self.current_processor = self.doc_processor
            
            if result["status"] == "success":
                self.current_document = file_path
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def query_document(self, query: str) -> Dict[str, Any]:
        if not self.current_processor:
            return {"status": "error", "message": "No document processed"}
        print(f"Querying document with question: {query}")
        return self.current_processor.query_response(query)

    def clear_documents(self):
        """Clear all previously processed documents"""
        self.current_processor = None
        self.current_document = None
        print("Documents cleared - ready for new uploads")

    def process_url(self, url: str) -> Dict[str, Any]:
        """Process a URL and set it as the current document"""
        try:
            result = self.web_processor.process_url(url)
            if result["status"] == "success":
                self.current_processor = self.web_processor
                self.current_document = url
                print(f"URL processed successfully: {url}")
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}