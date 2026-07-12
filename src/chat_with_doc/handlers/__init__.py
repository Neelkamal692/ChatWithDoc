"""Document handlers for processing different file types."""

from .base import BaseHandler
from .doc import DOCHandler
from .pdf import PDFHandler
from .txt import TXTHandler
from .web import WebHandler

__all__ = [
    "BaseHandler",
    "PDFHandler",
    "DOCHandler",
    "TXTHandler",
    "WebHandler",
]
