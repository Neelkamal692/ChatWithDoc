"""Handlers for supported document sources."""

from .base import BaseHandler
from .docx import DOCHandler
from .pdf import PDFHandler
from .txt import TXTHandler
from .web import WebHandler

__all__ = ["BaseHandler", "PDFHandler", "DOCHandler", "TXTHandler", "WebHandler"]
