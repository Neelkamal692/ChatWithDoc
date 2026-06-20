"""Document handlers for processing different file types."""

from .base import BaseHandler
from .pdf import PDFHandler
from .doc import DOCHandler
from .txt import TXTHandler
from .web import WebHandler

__all__ = [
    "BaseHandler",
    "PDFHandler",
    "DOCHandler",
    "TXTHandler",
    "WebHandler",
]
