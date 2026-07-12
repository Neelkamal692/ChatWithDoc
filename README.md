# ChatWithDoc

[![CI](https://img.shields.io/github/actions/workflow/status/Neelkamal692/ChatWithDoc/ci-cd.yml?branch=main&label=build&logo=github&logoColor=white)](https://github.com/Neelkamal692/ChatWithDoc/actions)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-supported-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-black?logo=ruff)](https://docs.astral.sh/ruff/)

Chat with your documents using Retrieval-Augmented Generation (RAG). Upload PDF/DOCX/TXT files or process a web URL, then ask questions through a browser UI or REST API.

## Features

- **Multi-format support**: PDF, DOCX, TXT, and web pages
- **Vector search**: FAISS similarity search over document chunks
- **LLM answers**: Google Gemini via LangChain / LangGraph RAG pipeline
- **Web UI**: Vanilla HTML, CSS, and JavaScript frontend
- **REST API**: FastAPI backend with upload, process, chat, status, and clear endpoints
- **Modular handlers**: Separate processors for PDF, DOCX, TXT, and web content

## Prerequisites

- Python 3.9+
- A Google Gemini API key (`GOOGLE_API_KEY`)
- Optional: Docker

## Quickstart

```bash
git clone https://github.com/Neelkamal692/ChatWithDoc.git
cd ChatWithDoc

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -e .
cp .env.example .env
```

Edit `.env` and set `GOOGLE_API_KEY`, then start the app:

```bash
python run.py
```

Open `http://localhost:8000`

## Project structure

```
ChatWithDoc/
├── .github/                   # CI/CD workflows
├── docker/                    # Production and development Dockerfiles
├── frontend/                  # Static HTML / CSS / JS UI
├── src/chat_with_doc/         # Main application package
│   ├── core/                  # Settings and model configuration
│   ├── handlers/              # Document processors (PDF, DOCX, TXT, Web)
│   ├── services/              # DocumentEngine orchestration
│   └── api/                   # FastAPI app and routes
├── tests/                     # Unit and API tests
├── .env.example               # Environment variable template
├── pyproject.toml             # Package and dependency management
├── run.py                     # Application entry point
└── README.md
```

## Supported file types

- PDF
- DOCX
- TXT
- Web pages (best for articles, docs, and blogs; heavy client-rendered SPAs may not extract well)

## Running the application

### Local development

```bash
python run.py
```

API and UI: `http://localhost:8000`  
Interactive API docs: `http://localhost:8000/docs`

### Production Docker

```bash
docker build -f docker/Dockerfile -t chatwith-doc:latest .
docker run -p 8000:8000 --env-file .env chatwith-doc:latest
```

### Development Docker

```bash
docker build -f docker/Dockerfile.dev -t chatwith-doc:dev .
docker run -p 8000:8000 --env-file .env -v $(pwd)/src:/app/src chatwith-doc:dev
```

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload a PDF, DOCX, or TXT file |
| `POST` | `/api/process-documents` | Process previously uploaded files |
| `POST` | `/api/process-url` | Fetch and process a web page |
| `POST` | `/api/chat` | Ask a question about processed documents |
| `GET` | `/api/status` | Status of processed documents |
| `POST` | `/api/clear` | Clear processed documents |
| `GET` | `/health` | Health check |

### Upload a document

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@path/to/document.pdf"
```

Example response:

```json
{
  "message": "File uploaded successfully",
  "document_info": {
    "filename": "document.pdf",
    "content_type": "application/pdf",
    "status": "uploaded",
    "location": "uploaded_files/document.pdf"
  }
}
```

### Process uploaded documents

```bash
curl -X POST "http://localhost:8000/api/process-documents"
```

### Chat

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Summarize this document\"}"
```

Example response:

```json
{
  "response": "From document.pdf:\n..."
}
```

## Configuration

Copy `.env.example` to `.env`. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | (required) | Google Gemini API key |
| `LLM_MODEL` | `gemini-3.5-flash` | Chat model name |
| `LLM_PROVIDER` | `google_genai` | LangChain model provider |
| `EMBEDDING_MODEL` | `gemini-embedding-2` | Google Gemini embeddings |
| `EMBEDDING_DIM` | `768` | FAISS vector dimension (Gemini recommended) |
| `CHUNK_SIZE` | `1000` | Text chunk size |
| `CHUNK_OVERLAP` | `200` | Chunk overlap |
| `MAX_FILE_SIZE` | `52428800` | Max upload size in bytes |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |

## Architecture

### Handlers

- **PDFHandler** — PDF via PyPDFLoader
- **DOCHandler** — DOCX via Docx2txtLoader
- **TXTHandler** — plain text via TextLoader
- **WebHandler** — HTML fetch + BeautifulSoup extraction

PDF/DOC/TXT handlers inherit from `BaseHandler`, which provides FAISS vector store creation and RAG querying (retrieve → generate with LangGraph).

### Services

- **DocumentEngine** — orchestrates processing and queries across handlers

### API

- **main.py** — FastAPI app factory, CORS, static frontend
- **routes.py** — HTTP endpoints

## Development

```bash
# Tests
pytest tests/ -v

# Coverage
pytest tests/ -v --cov=src/chat_with_doc --cov-report=html

# Lint / format
ruff check src tests
black src tests
```

Install optional dev tools:

```bash
pip install -e ".[dev]"
```

## Limitations

- Vector indexes are in-memory and cleared when the process restarts
- Chat currently queries each processed document separately (one LLM call per document)
- No authentication or rate limiting on API endpoints yet
- Web ingestion is best-effort for static / lightly dynamic pages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Open a pull request

## License

MIT — see [LICENSE](LICENSE).

## Support

Open a GitHub issue for bugs or questions.
