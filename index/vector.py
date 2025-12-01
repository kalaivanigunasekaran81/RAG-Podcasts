"""
Vector search and index management for OpenSearch.
"""

import os
from typing import Optional

try:
    from opensearchpy import OpenSearch, RequestsHttpConnection
except ImportError:
    OpenSearch = None
    RequestsHttpConnection = None

from ingest.embed import EMBEDDING_DIMENSION, get_embedding_model

# OpenSearch configuration
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "http://localhost:9200")
OPENSEARCH_USER = os.getenv("OPENSEARCH_USER", "admin")
OPENSEARCH_PASS = os.getenv("OPENSEARCH_PASS", "admin")
PODCAST_INDEX = os.getenv("PODCAST_INDEX", "podcast-transcripts")


def get_opensearch_client() -> OpenSearch:
    """
    Return an OpenSearch client configured for the project.
    
    Returns:
        OpenSearch client instance
    
    Raises:
        RuntimeError: If opensearchpy is not installed
    """
    if OpenSearch is None or RequestsHttpConnection is None:
        raise RuntimeError("`opensearchpy` is required. Install it with: `pip install opensearch-py`.")

    http_auth = (OPENSEARCH_USER, OPENSEARCH_PASS) if OPENSEARCH_USER or OPENSEARCH_PASS else None

    # OPENSEARCH_HOST can be "http://localhost:9200" OR {"host": "...", "port": ...}
    hosts = [OPENSEARCH_HOST] if isinstance(OPENSEARCH_HOST, str) else [OPENSEARCH_HOST]

    return OpenSearch(
        hosts=hosts,
        http_auth=http_auth,
        use_ssl=str(OPENSEARCH_HOST).startswith("https"),
        verify_certs=False,
        connection_class=RequestsHttpConnection,
    )


def create_podcast_index_if_needed(client: OpenSearch):
    """
    Create the OpenSearch index for podcast chunks if it doesn't already exist.
    
    Args:
        client: OpenSearch client instance
    """
    if client.indices.exists(index=PODCAST_INDEX):
        print(f"Index {PODCAST_INDEX} already exists")
        return

    # Force-load the embedding model to discover vector size
    if EMBEDDING_DIMENSION is None:
        get_embedding_model()
        if EMBEDDING_DIMENSION is None:
            raise RuntimeError(
                "Embedding dimension not initialized, even after loading model. "
                "Check the embedding model configuration."
            )

    body = {
        "settings": {
            "index.knn": True,
        },
        "mappings": {
            "properties": {
                "episode_id": {"type": "keyword"},
                "title": {"type": "text"},
                "podcast_name": {"type": "keyword"},
                "host": {"type": "keyword"},
                "guest": {"type": "keyword"},
                "date": {"type": "date", "format": "strict_date_optional_time||yyyy-MM-dd"},
                "chunk_text": {"type": "text"},
                "chunk_id": {"type": "keyword"},
                "chunk_index": {"type": "integer"},
                "timestamp": {"type": "keyword"},
                "url": {"type": "keyword"},
                "topics": {"type": "keyword"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": EMBEDDING_DIMENSION,
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "lucene",
                        "parameters": {"ef_construction": 128, "m": 16},
                    },
                },
            }
        },
    }

    client.indices.create(index=PODCAST_INDEX, body=body)
    print(f"Created index {PODCAST_INDEX} with vector size {EMBEDDING_DIMENSION}")


def vector_search(
    client: OpenSearch,
    query_embedding: list[float],
    size: int = 5,
    podcast_name: Optional[str] = None,
    topics: Optional[list[str]] = None,
) -> list[dict]:
    """
    Perform vector similarity search.
    
    Args:
        client: OpenSearch client
        query_embedding: Query embedding vector
        size: Number of results to return
        podcast_name: Optional podcast name filter
        topics: Optional topics filter
    
    Returns:
        List of search hits
    """
    filters = []
    if podcast_name:
        filters.append({"term": {"podcast_name": podcast_name}})
    if topics:
        filters.append({"terms": {"topics": topics}})

    body = {
        "size": size,
        "query": {
            "bool": {
                "must": [
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

