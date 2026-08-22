"""RAG state and API schemas."""

from typing import List

from langchain_core.documents import Document
from pydantic import BaseModel, Field


class State(BaseModel):
    """State passed through the retrieval and generation graph."""

    question: str = Field(..., description="Type your question here")
    context: List[Document] = Field(default_factory=list)
    answer: str = ""
