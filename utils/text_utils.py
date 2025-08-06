import re
from typing import List, Dict


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text.

    Args:
        text: Raw extracted text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters while preserving structure
    text = re.sub(r'[^\w\s\-\.\,\!\?\:\;\(\)\[\]\{\}\"\'\/\\\@\#\$\%\^\&\*\+\=\<\>\~\`]', ' ', text)

    # Normalize line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def extract_keywords(text: str, top_k: int = 10) -> List[str]:
    """Extract top keywords from text."""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1

    return sorted(word_count.keys(), key=lambda x: word_count[x], reverse=True)[:top_k]


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def count_sentences(text: str) -> int:
    """Count sentences in text."""
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])
