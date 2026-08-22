"""LangGraph definition for document question answering."""

from langgraph.graph import StateGraph

from ..models.schemas import State
from .generation import generate
from .retrieval import retrieve


def build_graph(vector_store, llm):
    """Build a retrieval-then-generation graph."""
    builder = StateGraph(State)
    builder.add_node("retrieve", lambda state: retrieve(state, vector_store))
    builder.add_node("generate", lambda state: generate(state, llm))
    builder.add_edge("retrieve", "generate")
    builder.set_entry_point("retrieve")
    return builder.compile()
