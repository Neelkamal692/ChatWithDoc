"""Document engine tests."""

import pytest
from unittest.mock import Mock, patch
from src.chat_with_doc.services.engine import DocumentEngine


@pytest.fixture
def engine():
    """Create a DocumentEngine instance."""
    return DocumentEngine()


def test_document_engine_initialization(engine):
    """Test engine initializes with handlers."""
    assert engine.pdf_handler is not None
    assert engine.doc_handler is not None
    assert engine.txt_handler is not None
    assert engine.web_handler is not None
    assert engine.processed_documents == []


def test_get_status_empty(engine):
    """Test status when no documents are processed."""
    status = engine.get_status()
    assert status["total_documents"] == 0
    assert status["document_types"] == []
    assert status["filenames"] == []


def test_clear_documents(engine):
    """Test clearing documents."""
    result = engine.clear_documents()
    assert result["status"] == "success"
    assert engine.processed_documents == []
    assert engine.all_content == ""
