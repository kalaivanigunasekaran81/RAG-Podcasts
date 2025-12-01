"""
Main RAG module that ties together ingestion, indexing, and querying.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from ingest import embed_text, chunk_by_semantic_windows, extract_guest_from_title
from index import get_opensearch_client, create_podcast_index_if_needed, hybrid_search
from llm import build_context, build_podcast_prompt, generate_answer
from index.vector import PODCAST_INDEX


@dataclass
class PodcastEpisode:
    episode_id: str
    title: str
    podcast_name: str
    host: str
    guest: Optional[str]
    date: str
    duration_minutes: int
    transcript: str
    topics: List[str]
    url: str


@dataclass
class TranscriptChunk:
    chunk_id: str
    episode_id: str
    title: str
    podcast_name: str
    host: str
    guest: Optional[str]
    date: str
    chunk_text: str
    chunk_index: int
    topics: List[str]
    url: str


def ingest_podcast_episode(client, episode: PodcastEpisode):
    """
    Chunk the transcript and store each paragraph with its embedding.
    
    Args:
        client: OpenSearch client
        episode: PodcastEpisode to ingest
    """
    title, extracted_guest = extract_guest_from_title(episode.title)
    guest_name = episode.guest or extracted_guest

    chunks = chunk_by_semantic_windows(episode.transcript)
    for chunk_data in chunks:
        chunk_id = f"{episode.episode_id}_chunk_{chunk_data['paragraph_index']}"
        emb = embed_text(chunk_data["text"])
        doc = {
            "chunk_id": chunk_id,
            "episode_id": episode.episode_id,
            "title": title,
            "podcast_name": episode.podcast_name,
            "host": episode.host,
            "guest": guest_name,
            "date": episode.date,
            "chunk_text": chunk_data["text"],
            "chunk_index": chunk_data["paragraph_index"],
            "timestamp": chunk_data["timestamp"],
            "topics": episode.topics,
            "url": episode.url,
            "embedding": emb,
        }
        client.index(index=PODCAST_INDEX, body=doc, id=chunk_id, refresh="true")

    print(f"Ingested episode '{episode.title}' with {len(chunks)} paragraph chunks")
    if guest_name:
        print(f"  Guest: {guest_name}")


def search_transcripts(
    client,
    user_query: str,
    query_embedding: List[float],
    size: int = 5,
    podcast_name: Optional[str] = None,
    topics: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Run a hybrid BM25 + vector search over indexed chunks.
    
    Args:
        client: OpenSearch client
        user_query: Search query text
        query_embedding: Query embedding vector
        size: Number of results to return
        podcast_name: Optional podcast name filter
        topics: Optional topics filter
    
    Returns:
        List of search hits
    """
    return hybrid_search(
        client=client,
        user_query=user_query,
        query_embedding=query_embedding,
        size=size,
        podcast_name=podcast_name,
        topics=topics,
    )


def ask_podcast_question(
    client,
    user_query: str,
    podcast_name: Optional[str] = None,
    topics: Optional[List[str]] = None,
    top_k: int = 5,
) -> str:
    """
    Answer a question using RAG pipeline.
    
    Args:
        client: OpenSearch client
        user_query: User's question
        podcast_name: Optional podcast name filter
        topics: Optional topics filter
        top_k: Number of chunks to retrieve
    
    Returns:
        Generated answer
    """
    query_emb = embed_text(user_query)
    hits = search_transcripts(
        client,
        user_query=user_query,
        query_embedding=query_emb,
        size=top_k,
        podcast_name=podcast_name,
        topics=topics,
    )

    if not hits:
        return "I couldn't find any relevant information in the podcast transcripts."

    context = build_context(hits)
    prompt = build_podcast_prompt(user_query, context)
    return generate_answer(prompt)

