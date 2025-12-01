"""
Hybrid search combining BM25 and vector similarity.
"""

from typing import List, Dict, Any, Optional

from index.vector import PODCAST_INDEX


def hybrid_search(
    client,
    user_query: str,
    query_embedding: List[float],
    size: int = 5,
    podcast_name: Optional[str] = None,
    topics: Optional[List[str]] = None,
    bm25_weight: float = 0.5,
    vector_weight: float = 0.5,
) -> List[Dict[str, Any]]:
    """
    Run a hybrid BM25 + vector search over indexed chunks.
    
    Args:
        client: OpenSearch client instance
        user_query: Search query text
        query_embedding: Query embedding vector
        size: Number of results to return
        podcast_name: Optional podcast name filter
        topics: Optional topics filter
        bm25_weight: Weight for BM25 scores (default: 0.5)
        vector_weight: Weight for vector scores (default: 0.5)
    
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
                "should": [
                    {
                        "knn": {
                            "embedding": {
                                "vector": query_embedding,
                                "k": size,
                            }
                        }
                    }
                ],
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

