import re
from typing import List


def normalize_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"\s+", " ", name)
    return name


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks
