"""FAISS vector store management."""

from typing import List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class VectorStoreManager:
    """Create and hold a FAISS store for one document source."""

    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.store: FAISS | None = None

    def create(self, documents: List[Document]) -> FAISS:
        self.store = FAISS.from_documents(documents, embedding=self.embedding_model)
        return self.store
