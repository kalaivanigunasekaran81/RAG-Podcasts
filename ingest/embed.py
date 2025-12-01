"""
Embedding generation for podcast transcripts.
"""

import os
from typing import List, Optional

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# Embedding model configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

_embedding_model: Optional[SentenceTransformer] = None
EMBEDDING_DIMENSION: Optional[int] = None


def get_embedding_model() -> SentenceTransformer:
    """
    Lazy-load the sentence-transformers embedding model and capture its vector size.
    
    Returns:
        Loaded SentenceTransformer model
    
    Raises:
        RuntimeError: If sentence-transformers is not installed
    """
    global _embedding_model, EMBEDDING_DIMENSION
    if _embedding_model is None:
        if SentenceTransformer is None:
            raise RuntimeError(
                "`sentence-transformers` is required. Install it with: `pip install sentence-transformers`."
            )
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        EMBEDDING_DIMENSION = _embedding_model.get_sentence_embedding_dimension()
        print(f"Embedding dimension: {EMBEDDING_DIMENSION}")
    return _embedding_model


def embed_text(text: str) -> List[float]:
    """
    Generate an embedding for a piece of text.
    
    Args:
        text: Text to embed
    
    Returns:
        List of float values representing the embedding vector
    """
    model = get_embedding_model()
    # For long transcripts you can consider batching externally
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_batch(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """
    Generate embeddings for a batch of texts.
    
    Args:
        texts: List of texts to embed
        batch_size: Number of texts to process at once
    
    Returns:
        List of embedding vectors
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
    return embeddings.tolist()

