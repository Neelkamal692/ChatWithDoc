from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from task_manager import DocumentManager
import warnings

# Disable all LangSmith related warnings
warnings.filterwarnings("ignore", message=".*LangSmith.*")
warnings.filterwarnings("ignore", message=".*API key.*")

# Also disable UserAgent warning
os.environ["LANGCHAIN_USER_AGENT"] = "ChatWithDoc/1.0"

app = FastAPI()

# Initialize document manager
doc_manager = DocumentManager()

# Store uploaded files temporarily before processing
uploaded_files = []

class UploadResponse(BaseModel):
    message: str
    document_info: Dict[str, Any]

class URLRequest(BaseModel):
    url: str = Field(..., description="URL of the document to process")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's question")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Answer to the user's question")

class ProcessResponse(BaseModel):
    message: str
    processed_count: int
    errors: List[str] = []

# Allow CORS (update this with your frontend URL in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your React frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a document (just stores it, doesn't process yet)
    
    - **file**: The document file to upload (PDF, DOCX, TXT)
    - Returns upload confirmation
    """
    print(f"Received file: {file.filename} of type {file.content_type}")
    
    # Get file extension and determine content type
    file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    
    # Map file extensions to content types
    extension_to_type = {
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    # Use file extension to determine content type if content_type is not reliable
    if file.content_type and file.content_type in ["application/pdf", "text/plain", "application/msword", 
                                                   "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        content_type = file.content_type
    elif file_extension in extension_to_type:
        content_type = extension_to_type[file_extension]
    else:
        return JSONResponse(status_code=400, content={"error": f"Unsupported file type: {file_extension}"})
    
    print(f"Using content type: {content_type}")

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save the file
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store file info for later processing
    file_info = {
        "filename": file.filename,
        "file_location": file_location,
        "content_type": content_type
    }
    uploaded_files.append(file_info)
    
    print("File uploaded successfully, ready for processing")
    return UploadResponse(
        message="File uploaded successfully",
        document_info={
            "filename": file.filename,
            "content_type": content_type,
            "status": "uploaded",
            "location": file_location
        }
    )

@app.post("/process-documents")
async def process_documents():
    """
    Process all uploaded files using your processor architecture
    """
    try:
        if not uploaded_files:
            return JSONResponse(status_code=400, content={"error": "No files uploaded"})
        
        processed_count = 0
        errors = []
        
        # Process each uploaded file
        for file_info in uploaded_files:
            try:
                result = doc_manager.process_document(file_info["file_location"], file_info["content_type"])
                
                if result["status"] == "success":
                    processed_count += 1
                    print(f"Successfully processed: {file_info['filename']}")
                else:
                    error_msg = f"{file_info['filename']}: {result['message']}"
                    errors.append(error_msg)
                    print(f"Failed to process {file_info['filename']}: {result['message']}")
                    
            except Exception as e:
                error_msg = f"{file_info['filename']}: {str(e)}"
                errors.append(error_msg)
                print(f"Exception processing {file_info['filename']}: {e}")
        
        # Clear uploaded files list after processing attempt
        uploaded_files.clear()
        
        if processed_count == 0:
            return JSONResponse(status_code=400, content={
                "error": f"Failed to process any files. Errors: {'; '.join(errors)}"
            })
        
        response_message = f"Successfully processed {processed_count} files"
        if errors:
            response_message += f". {len(errors)} files had errors."
        
        return ProcessResponse(
            message=response_message,
            processed_count=processed_count,
            errors=errors
        )
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/process-url")
async def process_url(url_request: URLRequest):
    """
    Process a document from URL using your web processor
    
    - **url**: The URL of the document to process
    - Returns document processing information
    """
    url = url_request.url
    
    try:
        # Process the URL using your web processor
        result = doc_manager.process_url(url)
        print("URL processing result:", result)
        
        if result["status"] == "error":
            return JSONResponse(status_code=400, content={"error": result["message"]})
        
        return UploadResponse(
            message="URL processed successfully",
            document_info={
                "url": url,
                "status": "processed",
                "type": "url",
                "title": result.get("title", "Untitled"),
                "num_pages": result.get("num_pages", 0),
                "num_chunks": result.get("num_chunks", 0),
                "word_count": result.get("word_count", 0)
            }
        )
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/chat")
async def chat_with_doc(chat_request: ChatRequest):
    """
    Process a query against processed documents using your processors
    
    - **query**: The user's question
    - Returns an answer
    """
    try:
        print(f"Received query: {chat_request.message}")
        result = doc_manager.query_document(chat_request.message)
        print("Query result:", result)
        
        if result["status"] == "error":
            return JSONResponse(status_code=400, content={"error": result["message"]})
        
        return ChatResponse(
            response=result["answer"]
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/clear-documents")
async def clear_documents():
    """
    Clear all previously processed documents and uploaded files
    """
    print("Clearing all documents...")
    try:
        doc_manager.clear_documents()
        uploaded_files.clear()
        return {"message": "Documents cleared successfully"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/status")
async def get_status():
    """
    Get current status of uploaded and processed documents
    """
    try:
        # Get status from your document manager if it has a get_status method
        if hasattr(doc_manager, 'get_status'):
            doc_status = doc_manager.get_status()
        else:
            # Fallback for original single-document architecture
            doc_status = {
                "total_documents": 1 if hasattr(doc_manager, 'current_processor') and doc_manager.current_processor else 0,
                "current_document": getattr(doc_manager, 'current_document', None)
            }
        
        return {
            "uploaded_files": len(uploaded_files),
            "status": doc_status
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "message": "ChatWithDoc API is running"}

# Mount the frontend directory as a static path.
# This should be after all API routes to ensure they are not overridden.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)