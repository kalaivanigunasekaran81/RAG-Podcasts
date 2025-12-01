"""
Ingestion module for cleaning, chunking, and embedding podcast transcripts.
"""

from .clean import clean_text
from .chunk import chunk_by_semantic_windows, extract_guest_from_title
from .embed import get_embedding_model, embed_text, EMBEDDING_DIMENSION

__all__ = [
    "clean_text",
    "chunk_by_semantic_windows",
    "extract_guest_from_title",
    "get_embedding_model",
    "embed_text",
    "EMBEDDING_DIMENSION",
]

