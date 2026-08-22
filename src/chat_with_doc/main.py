"""FastAPI application entry point."""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.chat import router as chat_router
from .api.documents import router as documents_router
from .config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    force=True,
)
os.environ["LANGCHAIN_USER_AGENT"] = "ChatWithDoc/1.0"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description="Chat with your documents using Retrieval Augmented Generation (RAG)",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(documents_router, prefix="/api", tags=["documents"])
    app.include_router(chat_router, prefix="/api", tags=["chat"])
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend")
    if os.path.exists(frontend_path):
        app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


    return app


app = create_app()

