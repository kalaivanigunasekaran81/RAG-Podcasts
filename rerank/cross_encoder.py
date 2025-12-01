"""
Cross-encoder reranking for improving search result relevance.
"""

from typing import List, Dict, Any, Optional

try:
    from sentence_transformers import CrossEncoder
except ImportError:
    CrossEncoder = None

# Default cross-encoder model for reranking
DEFAULT_RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_rerank_model: Optional[CrossEncoder] = None


def get_rerank_model(model_name: Optional[str] = None) -> CrossEncoder:
    """
    Lazy-load the cross-encoder model for reranking.
    
    Args:
        model_name: Optional model name (defaults to DEFAULT_RERANK_MODEL)
    
    Returns:
        Loaded CrossEncoder model
    
    Raises:
        RuntimeError: If sentence-transformers is not installed
    """
    global _rerank_model
    if _rerank_model is None:
        if CrossEncoder is None:
            raise RuntimeError(
                "`sentence-transformers` is required for reranking. "
                "Install it with: `pip install sentence-transformers`."
            )
        model = model_name or DEFAULT_RERANK_MODEL
        print(f"Loading reranking model: {model}")
        _rerank_model = CrossEncoder(model)
    return _rerank_model


def rerank_results(
    query: str,
    hits: List[Dict[str, Any]],
    top_k: Optional[int] = None,
    model_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Rerank search results using a cross-encoder model.
    
    Args:
        query: Search query
        hits: List of search hits with _source containing chunk_text
        top_k: Number of top results to return (None = return all)
        model_name: Optional reranking model name
    
    Returns:
        Reranked list of hits sorted by relevance score
    """
    if not hits:
        return []

    # Extract query-document pairs
    pairs = []
    for hit in hits:
        chunk_text = hit.get("_source", {}).get("chunk_text", "")
        pairs.append([query, chunk_text])

    # Get reranking scores
    model = get_rerank_model(model_name)
    scores = model.predict(pairs)

    # Add rerank scores to hits
    for i, hit in enumerate(hits):
        hit["_rerank_score"] = float(scores[i])

    # Sort by rerank score (descending)
    reranked = sorted(hits, key=lambda x: x.get("_rerank_score", 0), reverse=True)

    # Return top_k if specified
    if top_k is not None:
        reranked = reranked[:top_k]

    return reranked

