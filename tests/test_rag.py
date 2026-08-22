"""Tests for the retrieval/generation RAG graph."""

from langchain_core.documents import Document

from src.chat_with_doc.models.schemas import State
from src.chat_with_doc.rag.generation import generate
from src.chat_with_doc.rag.graph import build_graph
from src.chat_with_doc.rag.retrieval import retrieve


class FakeVectorStore:
    """Vector store stub returning a fixed set of documents."""

    def __init__(self, docs):
        self.docs = docs

    def similarity_search(self, question):
        return self.docs


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    """LLM stub returning a fixed answer."""

    def invoke(self, messages):
        return FakeMessage("fake answer")


def test_retrieve_returns_context():
    docs = [Document(page_content="relevant text")]
    state = State(question="what?")

    result = retrieve(state, FakeVectorStore(docs))

    assert result["context"] == docs


def test_generate_uses_context_and_llm():
    state = State(question="what?", context=[Document(page_content="relevant text")])

    result = generate(state, FakeLLM())

    assert result["answer"] == "fake answer"


def test_build_graph_runs_end_to_end():
    docs = [Document(page_content="relevant text")]
    graph = build_graph(FakeVectorStore(docs), FakeLLM())

    response = graph.invoke({"question": "what?"})

    assert response["answer"] == "fake answer"
