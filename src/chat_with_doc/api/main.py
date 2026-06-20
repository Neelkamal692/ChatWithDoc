"""FastAPI application factory."""

import os
import warnings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ..core.config import settings
from .routes import router

os.environ["LANGCHAIN_USER_AGENT"] = "ChatWithDoc/1.0"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description="Chat with your documents using Retrieval Augmented Generation (RAG)"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(router, prefix="/api", tags=["documents"])
    
    # Serve static files (frontend)
    frontend_path = os.path.join(os.path.dirname(__file__), "../../../frontend")
    if os.path.exists(frontend_path):
        app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    return app


# Create the app instance
app = create_app()
