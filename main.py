from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pydantic import BaseModel, Field
from typing import Dict, Any
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

class UploadResponse(BaseModel):
    message: str
    document_info: Dict[str, Any]

class URLRequest(BaseModel):
    url: str = Field(..., description="URL of the document to process")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's question")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Answer to the user's question")

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



@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a document
    
    - **file**: The document file to upload (PDF, DOCX, TXT)
    - Returns document processing information
    """
    # Limit file types if needed
    allowed_types = ["application/pdf", "text/plain",
                     "application/msword", 
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    if file.content_type not in allowed_types:
        return JSONResponse(status_code=400, content={"error": "Unsupported file type"})

    # Clear previous documents before processing new ones
    doc_manager.clear_documents()

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = doc_manager.process_document(file_location, file.content_type)
    print("Processing result:", result)
    if result["status"] == "error":
        return JSONResponse(status_code=400, content={"error": result["message"]})
    
    return UploadResponse(
        message="File uploaded successfully",
        document_info={
            "filename": file.filename,
            "content_type": file.content_type,
            "status": "uploaded",
            "location": file_location
        }
    )

@app.post("/api/process-url")
async def process_url(url_request: URLRequest):
    """
    Process a document from URL
    
    - **url**: The URL of the document to process
    - Returns document processing information
    """
    url = url_request.url
    
    # Clear previous documents before processing new ones
    doc_manager.clear_documents()
    
    # Process the URL using the web processor
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
            "num_pages": result.get("num_pages", 0),
            "num_chunks": result.get("num_chunks", 0)
        }
    )

@app.post("/api/chat")
async def chat_with_doc(chat_request: ChatRequest):
    """
    Process a query against a specific document
    
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

@app.post("/api/clear-documents")
async def clear_documents():
    """
    Clear all previously processed documents
    """
    try:
        doc_manager.clear_documents()
        return {"message": "Documents cleared successfully"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
# Mount the frontend directory as a static path
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# For Vercel deployment - export the app
app.debug = False