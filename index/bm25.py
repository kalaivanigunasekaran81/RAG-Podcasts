"""
BM25 text search for podcast transcripts.
"""

import os
from typing import Optional, List, Dict, Any

PODCAST_INDEX = os.getenv("PODCAST_INDEX", "podcast-transcripts")


def bm25_search(
    client,
    user_query: str,
    size: int = 5,
    podcast_name: Optional[str] = None,
    topics: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Perform BM25 keyword search over indexed chunks.
    
    Args:
        client: OpenSearch client instance
        user_query: Search query text
        size: Number of results to return
        podcast_name: Optional podcast name filter
        topics: Optional topics filter
    
    Returns:
        List of search hits with _id, _score, and _source
    """
    filters = []
    if podcast_name:
        filters.append({"term": {"podcast_name": podcast_name}})
    if topics:
        filters.append({"terms": {"topics": topics}})

    must_clause = [{"match": {"chunk_text": user_query}}] if user_query else [{"match_all": {}}]

    body = {
        "size": size,
        "query": {
            "bool": {
                "must": must_clause,
                **({"filter": filters} if filters else {}),
            }
        },
    }

    response = client.search(index=PODCAST_INDEX, body=body)
    hits = response.get("hits", {}).get("hits", [])

    return [
        {
            "_id": hit.get("_id"),
            "_score": hit.get("_score"),
            "_source": hit.get("_source", {}),
        }
        for hit in hits
    ]

