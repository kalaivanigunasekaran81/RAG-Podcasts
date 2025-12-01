"""
Text cleaning utilities for podcast transcripts.
"""

import re
from typing import Optional


def clean_text(text: str, remove_timestamps: bool = False) -> str:
    """
    Clean podcast transcript text.
    
    Args:
        text: Raw transcript text
        remove_timestamps: If True, remove timestamp markers like [00:01:23]
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove timestamps if requested
    if remove_timestamps:
        text = re.sub(r'\[?\d{1,2}:\d{2}(?::\d{2})?\]?', '', text)
    
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    return ' '.join(text.split())


def remove_special_characters(text: str, keep_punctuation: bool = True) -> str:
    """
    Remove special characters from text.
    
    Args:
        text: Input text
        keep_punctuation: If True, keep standard punctuation marks
    
    Returns:
        Cleaned text
    """
    if keep_punctuation:
        # Keep alphanumeric, spaces, and common punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\'"]', '', text)
    else:
        # Keep only alphanumeric and spaces
        text = re.sub(r'[^\w\s]', '', text)
    
    return text

