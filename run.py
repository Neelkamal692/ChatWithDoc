"""Application entry point."""

import uvicorn

from src.chat_with_doc.main import app

if __name__ == "__main__":
    uvicorn.run(
        "src.chat_with_doc.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

