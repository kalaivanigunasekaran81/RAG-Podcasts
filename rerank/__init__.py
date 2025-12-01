"""
Reranking module for improving search result relevance.
"""

from .cross_encoder import rerank_results

__all__ = ["rerank_results"]

