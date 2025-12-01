"""
Chunking utilities for podcast transcripts.

This module contains functions for splitting transcripts into semantic
windows and extracting guest names from episode titles.
"""

from typing import List, Optional, Dict, Any
import re


def chunk_by_semantic_windows(text: str, max_tokens: int = 240, overlap: int = 40) -> List[Dict[str, Any]]:
    """
    Chunk transcript into overlapping semantic windows.
    Retains timestamps and speaker lines where possible.

    Best for podcast transcripts.
    
    Args:
        text: Transcript text to chunk
        max_tokens: Maximum tokens per chunk
        overlap: Number of tokens to overlap between chunks
    
    Returns:
        List of chunk dictionaries with 'text', 'timestamp', and 'paragraph_index'
    """
    # Split into speaker blocks if possible
    speaker_pattern = re.compile(r"^(Host|Guest|Speaker \d+|Interviewer):", re.IGNORECASE)
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    blocks = []
    current = []

    for line in lines:
        if speaker_pattern.match(line):
            if current:
                blocks.append(" ".join(current))
                current = []
        current.append(line)

    if current:
        blocks.append(" ".join(current))

    # Simple fallback if no speaker format
    if len(blocks) < 3:
        blocks = re.split(r"\n\s*\n", text)
        blocks = [b.strip() for b in blocks if b.strip()]

    # Token estimation (no tokenizer dependency)
    def estimate_tokens(txt):
        return int(len(txt.split()) * 1.3)

    chunks = []
    buffer = []
    token_count = 0

    for block in blocks:
        tokens = estimate_tokens(block)

        if token_count + tokens > max_tokens:
            # Emit chunk
            chunk_text = " ".join(buffer)
            chunks.append(chunk_text)

            # Overlap buffer
            overlap_words = int(overlap / 1.3)
            buffer = chunk_text.split()[-overlap_words:]
            token_count = estimate_tokens(" ".join(buffer))

        buffer.append(block)
        token_count += tokens

    if buffer:
        chunks.append(" ".join(buffer))

    return [
        {
            "text": chunk,
            "timestamp": None,
            "paragraph_index": idx,
        }
        for idx, chunk in enumerate(chunks)
    ]


def extract_guest_from_title(title: str) -> tuple[str, Optional[str]]:
    """
    Extract guest name from episode title using common patterns.
    
    Args:
        title: Episode title
    
    Returns:
        Tuple of (cleaned_title, guest_name or None)
    """
    match = re.search(r"\bwith\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", title, re.IGNORECASE)
    if match:
        return title, match.group(1)

    match = re.search(r"\b(?:ft\.?|featuring)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", title, re.IGNORECASE)
    if match:
        return title, match.group(1)

    match = re.search(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+on\s+", title)
    if match:
        return title, match.group(1)

    match = re.search(r"[|\-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*$", title)
    if match:
        return title, match.group(1)

    return title, None

