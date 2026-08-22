"""Chat / question-answering API endpoints."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .documents import doc_engine

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat queries."""
    message: str = Field(..., description="User's question")


class ChatResponse(BaseModel):
    """Response model for chat queries."""
    response: str = Field(..., description="Answer to the user's question")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_documents(chat_request: ChatRequest):
    """
    Chat with the processed documents.

    Answers questions based on the uploaded and processed documents.
    """
    logger.info(f"Received message : {chat_request.message} from user")
    query = chat_request.message

    try:
        logger.info("waiting for query response...")
        result = doc_engine.query_documents(query)
        if result["status"] == "error":
            return JSONResponse(status_code=400, content={"error": result["message"]})

        return ChatResponse(response=result["answer"])

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
