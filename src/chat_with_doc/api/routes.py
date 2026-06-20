"""API route definitions."""

import os
import shutil
from typing import Dict, Any, List
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel, Field
from ..services.engine import DocumentEngine
import logging

logger = logging.getLogger(__name__)


router = APIRouter()
doc_engine = DocumentEngine()
uploaded_files = []

# Configure upload directory
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Pydantic models
class URLRequest(BaseModel):
    """Request model for URL processing."""
    url: str = Field(..., description="URL of the document to process")


class ChatRequest(BaseModel):
    """Request model for chat queries."""
    message: str = Field(..., description="User's question")


class ChatResponse(BaseModel):
    """Response model for chat queries."""
    response: str = Field(..., description="Answer to the user's question")


class UploadResponse(BaseModel):
    """Response model for file uploads."""
    message: str
    document_info: Dict[str, Any]


class ProcessResponse(BaseModel):
    """Response model for document processing."""
    message: str
    processed_count: int
    errors: List[str] = []


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a document for processing.
    
    Supported formats:
    - PDF (application/pdf)
    - DOCX (application/vnd.openxmlformats-officedocument.wordprocessingml.document)
    - TXT (text/plain)
    """
    logger.info(f"Received file: {file.filename} of type {file.content_type}")    
    # Get file extension
    file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    
    # Map file extensions to content types
    extension_to_type = {
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    # Determine content type
    if file.content_type and file.content_type in [
        "application/pdf",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]:
        content_type = file.content_type
    elif file_extension in extension_to_type:
        content_type = extension_to_type[file_extension]
    else:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=400,
            content={"error": f"Unsupported file type: {file_extension}"}
        )
    
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


@router.post("/process-documents", response_model=ProcessResponse)
async def process_documents():
    """
    Process all uploaded files.
    
    This endpoint processes files that were previously uploaded.
    """
    from fastapi.responses import JSONResponse
    
    try:
        if not uploaded_files:
            return JSONResponse(
                status_code=400,
                content={"error": "No files uploaded"}
            )
        
        processed_count = 0
        errors = []
        logger.info(f"Received files : {uploaded_files} ")
        # Process each uploaded file
        for file_info in uploaded_files:
            try:
                result = doc_engine.process_document(
                    file_info["file_location"],
                    file_info["content_type"]
                )
                
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
        
        # Clear uploaded files list
        uploaded_files.clear()
        
        if processed_count == 0:
            return JSONResponse(
                status_code=400,
                content={"error": f"Failed to process files. Errors: {'; '.join(errors)}"}
            )
        
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


@router.post("/process-url", response_model=UploadResponse)
async def process_url(url_request: URLRequest):
    """
    Process a document from a URL.
    
    Fetches and processes web page content.
    """
    from fastapi.responses import JSONResponse
    
    url = url_request.url
    
    try:
        result = doc_engine.process_url(url)
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


@router.post("/chat", response_model=ChatResponse)
async def chat_with_documents(chat_request: ChatRequest):
    """
    Chat with the processed documents.
    
    Answers questions based on the uploaded and processed documents.
    """
    from fastapi.responses import JSONResponse
    logger.info(f"Received message : {chat_request.message} from user") 
    query = chat_request.message
    
    try:
        result = doc_engine.query_documents(query)
        
        if result["status"] == "error":
            return JSONResponse(status_code=400, content={"error": result["message"]})
        
        return ChatResponse(response=result["answer"])
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/status")
async def get_status():
    """Get the current status of processed documents."""
    return doc_engine.get_status()


@router.post("/clear")
async def clear_documents():
    """Clear all processed documents."""
    return doc_engine.clear_documents()
