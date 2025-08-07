from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
import os
from langchain import hub
from dotenv import load_dotenv
from langgraph.graph import START, StateGraph
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from langchain.docstore.document import Document

load_dotenv()

class State(BaseModel):
    question: str = Field(..., description="Type your question here")
    context: List[Document] = Field(
        default_factory=list,
        description="A list of Document objects",
    )
    answer: str = Field(default="", description="Answer will be here")

class WebProcessor:
    def __init__(self):
        # Load model provider
        if not os.environ.get("GOOGLE_API_KEY"):
            raise ValueError("Google Gemini API key not found in environment variables")

        self.llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        self.prompt = hub.pull("rlm/rag-prompt")
        self.vector_store = None
        self.chunk_size = 1000
        self.chunk_overlap = 200

    def process_url(self, url: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Process a URL or list of URLs and prepare for querying
        
        Args:
            url: Single URL string or list of URLs to process
            
        Returns:
            Dict[str, Any]: Processing status and information
        """
        try:
            # Convert single URL to list
            urls = [url] if isinstance(url, str) else url

            # Document Loading
            loader = WebBaseLoader(urls)
            pages = loader.load()

            # Text Splitting
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                is_separator_regex=False,
            )
            texts = text_splitter.split_documents(pages)

            # Vector Store Setup
            embedding_dim = len(self.embedding_model.embed_query("test"))
            index = faiss.IndexFlatL2(embedding_dim)

            self.vector_store = FAISS(
                embedding_function=self.embedding_model,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
            )

            # Index chunks
            self.vector_store.add_documents(documents=texts)

            return {
                "status": "success",
                "message": "URLs processed successfully",
                "num_pages": len(pages),
                "num_chunks": len(texts),
                "urls_processed": urls
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing URLs: {str(e)}"
            }

    def query_response(self, query: str) -> Dict[str, Any]:
        """
        Query the processed web content
        
        Args:
            query (str): The question to ask about the content
            
        Returns:
            Dict[str, Any]: Answer and relevant context
        """
        if not self.vector_store:
            return {
                "status": "error",
                "message": "No content has been processed yet"
            }

        try:
            # Create state graph
            graph_builder = StateGraph(State)

            # Define retrieval step
            def retrieve(state: State):
                retrieved_docs = self.vector_store.similarity_search(state.question)
                return {"context": retrieved_docs}

            # Define generation step
            def generate(state: State):
                docs_content = "\n\n".join(doc.page_content for doc in state.context)
                messages = self.prompt.invoke({
                    "question": state.question,
                    "context": docs_content
                })
                response = self.llm.invoke(messages)
                return {"answer": response.content}

            # Build and compile the graph
            graph = graph_builder.add_sequence([retrieve, generate]).set_entry_point("retrieve").compile()

            # Execute the query
            response = graph.invoke({
                "question": query
            })

            return {
                "status": "success",
                "answer": response["answer"],
                "query": query
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error querying content: {str(e)}"
            }

