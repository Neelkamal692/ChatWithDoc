# ChatWithDoc - Chat with Your Documents

A modern RAG (Retrieval Augmented Generation) application that allows you to chat with your documents using AI-powered search and question-answering.

## Features

- **Multi-format Support**: Process PDF, DOCX, TXT files, and web pages
- **Vector Search**: Powered by FAISS for efficient similarity search
- **LLM Integration**: Uses Google Gemini for intelligent question-answering
- **Web Interface**: Interactive React frontend
- **REST API**: FastAPI-based backend with comprehensive endpoints
- **Scalable Architecture**: Modular handler-based design for easy extension

## Project Structure

```
ChatWithDoc/
├── .github/                        # CI/CD workflows
├── config/                         # Application configuration
├── docker/                         # Docker files (dev & prod)
├── frontend/                       # React UI
├── src/chat_with_doc/              # Main application package
│   ├── core/                       # Settings and configuration
│   ├── handlers/                   # Document processors (PDF, DOCX, TXT, Web)
│   ├── services/                   # Business logic and document engine
│   └── api/                        # FastAPI routes and endpoints
├── tests/                          # Unit and integration tests
├── .env.example                    # Environment variables template
├── .gitignore                      # Git exclusions
├── pyproject.toml                  # Package and dependency management
├── README.md                       # This file
└── run.py                          # Application entry point
```

## Prerequisites

- Python 3.9+
- Google Gemini API key
- pip or uv package manager

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chat-with-doc.git
   cd ChatWithDoc
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

## Running the Application

### Development Mode

```bash
python run.py
```

The API will be available at `http://localhost:8000`

### Production Mode with Docker

```bash
# Build the image
docker build -f docker/Dockerfile -t chatwith-doc:latest .

# Run the container
docker run -p 8000:8000 --env-file .env chatwith-doc:latest
```

### Development Docker

```bash
# Build dev image with hot-reload
docker build -f docker/Dockerfile.dev -t chatwith-doc:dev .

# Run with volume mounting for development
docker run -p 8000:8000 --env-file .env -v $(pwd)/src:/app/src chatwith-doc:dev
```

## API Endpoints

### Document Management

- `POST /api/upload` - Upload a document (PDF, DOCX, TXT)
- `POST /api/process-documents` - Process uploaded documents
- `POST /api/process-url` - Process a web page
- `GET /api/status` - Get status of processed documents
- `POST /api/clear` - Clear all processed documents

### Chat

- `POST /api/chat` - Ask a question about processed documents

### Health

- `GET /health` - Health check endpoint

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ -v --cov=src/chat_with_doc --cov-report=html
```

### Linting

```bash
ruff check src tests
black src tests
```

## Architecture

### Handlers

Each document type has a dedicated handler:

- **PDFHandler**: Processes PDF files using PyPDFLoader
- **DOCHandler**: Processes DOCX files using Docx2txtLoader
- **TXTHandler**: Processes plain text files
- **WebHandler**: Fetches and processes web content

All handlers inherit from `BaseHandler` which provides:
- Vector store management
- Embedding generation
- Query response generation using RAG

### Services

- **DocumentEngine**: Orchestrates document processing and queries across multiple handlers

### API

- **main.py**: FastAPI app factory with middleware setup
- **routes.py**: Route definitions and endpoint handlers

## Configuration

Environment variables are loaded from `.env` file:

```env
GOOGLE_API_KEY=your_key_here
LLM_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

See `.env.example` for all available options.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.
