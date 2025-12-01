"""
Index podcast transcripts from local files or manual input into OpenSearch
Optimized for M2 MacBook Air + local RAG
"""

import os
import glob
from typing import List
from pathlib import Path

from rag import (
    PodcastEpisode,
    ingest_podcast_episode,
)
from index import get_opensearch_client, create_podcast_index_if_needed
from ingest import get_embedding_model


PODCAST_NAME = os.getenv("PODCAST_NAME", "Local Transcripts")
TRANSCRIPTS_DIR = os.getenv("TRANSCRIPTS_DIR", "data/transcripts")


def load_transcripts_from_directory(directory: str) -> List[PodcastEpisode]:
    """
    Load transcript files from a directory.
    Each .txt file → one PodcastEpisode
    """
    episodes = []
    txt_files = sorted(glob.glob(os.path.join(directory, "*.txt")))

    print(f"📂 Found {len(txt_files)} transcripts in '{directory}'")

    for i, filepath in enumerate(txt_files, 1):
        filename = os.path.basename(filepath)
        episode_id = filename.replace(".txt", "")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                transcript = f.read().strip()
        except UnicodeDecodeError:
            print(f"⚠️ Skipping unreadable file: {filename}")
            continue

        if not transcript:
            print(f"⚠️ Skipping empty file: {filename}")
            continue

        title = episode_id.replace("_", " ").replace("-", " ").title()

        episode = PodcastEpisode(
            episode_id=f"ep-{i:03d}",
            title=title,
            podcast_name=PODCAST_NAME,
            host="Unknown",
            guest=None,
            date="2024-01-01",
            duration_minutes=0,
            transcript=transcript,
            topics=[],
            url=f"file://{Path(filepath).resolve()}",
        )

        episodes.append(episode)

    return episodes


def load_transcripts_from_text(transcript_text: str, title: str, episode_id: str) -> PodcastEpisode:
    """
    Create a single PodcastEpisode from raw text.
    """
    return PodcastEpisode(
        episode_id=episode_id,
        title=title,
        podcast_name=PODCAST_NAME,
        host="Unknown",
        guest=None,
        date="2024-01-01",
        duration_minutes=0,
        transcript=transcript_text,
        topics=[],
        url=f"file://{episode_id}",
    )


def main():
    print("🚀 Podcast RAG Indexer Starting...\n")

    # ✅ Make sure embedding model loads first so vector size is known
    print("🔹 Initializing embedding model...")
    get_embedding_model()

    # ✅ OpenSearch client
    print("🔹 Connecting to OpenSearch...")
    client = get_opensearch_client()

    # ✅ Delete index if FORCE_RECREATE_COLLECTION is set
    if os.getenv("FORCE_RECREATE_COLLECTION"):
        print("🔹 Deleting existing index to recreate with new dimensions...")
        try:
            from index.vector import PODCAST_INDEX
            client.indices.delete(index=PODCAST_INDEX)
            print("✅ Index deleted")
        except Exception as e:
            print(f"⚠️ Index deletion failed (may not exist): {e}")

    # ✅ Create index if needed
    print("🔹 Checking / creating OpenSearch index...")
    create_podcast_index_if_needed(client)

    # -----------------------------
    # Option 1: Load transcripts
    # -----------------------------

    if os.path.exists(TRANSCRIPTS_DIR):

        episodes = load_transcripts_from_directory(TRANSCRIPTS_DIR)

        print(f"\n🧾 Indexing {len(episodes)} episodes...\n")

        for i, episode in enumerate(episodes, 1):
            print(f"[{i}/{len(episodes)}] Indexing → {episode.title}")
            ingest_podcast_episode(client, episode)

        print(f"\n✅ Indexed {len(episodes)} episodes successfully")

    # -----------------------------
    # Option 2: Example text
    # -----------------------------
    else:
        print(f"❌ Directory '{TRANSCRIPTS_DIR}' not found.")
        print("\nCreate it & add transcript files like:")
        print("  data/transcripts/episode01.txt")
        print("  data/transcripts/episode02.txt")

        print("\nIndexing example transcript instead...\n")

        example_transcript = """
        Host: Welcome to today's episode. We're discussing the future of technology.
        Guest: Thanks for having me. I'm excited to talk about AI and machine learning.
        Host: Let's start with the basics. What is machine learning?
        Guest: Machine learning is a subset of artificial intelligence that enables systems
        to learn and improve from experience without being explicitly programmed.
        """

        example_episode = load_transcripts_from_text(
            transcript_text=example_transcript,
            title="The Future of Technology",
            episode_id="example-001",
        )

        ingest_podcast_episode(client, example_episode)

        print("✅ Example episode indexed")


if __name__ == "__main__":
    main()

