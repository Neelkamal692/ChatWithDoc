"""Retrieval node for the RAG graph."""


def retrieve(state, vector_store):
    """Retrieve documents relevant to the current question."""
    return {"context": vector_store.similarity_search(state.question)}
