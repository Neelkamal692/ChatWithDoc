"""Generation node for the RAG graph."""

from langchain_core.prompts import ChatPromptTemplate


def generate(state, llm):
    """Generate an answer using only retrieved context."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Answer the user's question using only "
         "the provided context. If the answer is not in the context, say that you do not know."),
        ("human", "Context:\n{context}\n\nQuestion:\n{question}"),
    ])
    messages = prompt.invoke({
        "question": state.question,
        "context": "\n\n".join(doc.page_content for doc in state.context),
    })
    return {"answer": llm.invoke(messages).content}
