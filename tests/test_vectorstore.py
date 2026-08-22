"""Tests for the FAISS vector store manager."""

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from src.chat_with_doc.vectorstore.faiss_store import VectorStoreManager


class FakeEmbeddings(Embeddings):
    """Deterministic embeddings so tests don't call any external API."""

    def embed_documents(self, texts):
        return [[float(len(text))] for text in texts]

    def embed_query(self, text):
        return [float(len(text))]


def test_create_builds_faiss_store():
    manager = VectorStoreManager(FakeEmbeddings())
    documents = [Document(page_content="hello world"), Document(page_content="goodbye")]

    store = manager.create(documents)

    assert store is manager.store
    assert store.similarity_search("hello", k=1)
