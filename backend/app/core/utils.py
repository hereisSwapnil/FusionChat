import re
from typing import List, Dict, Any
import nltk
from nltk.tokenize import sent_tokenize

# Download required NLTK data (run once)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)


def normalize_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"\s+", " ", name)
    return name


def detect_content_type(text: str) -> str:
    """Detect the type of content in a chunk."""
    # Code block detection
    if re.search(r"```|^\s{4,}", text, re.MULTILINE):
        return "code"
    # List detection
    if re.search(r"^\s*[-*•]\s+", text, re.MULTILINE) or re.search(
        r"^\s*\d+\.\s+", text, re.MULTILINE
    ):
        return "list"
    # Table detection
    if re.search(r"\|.*\|", text):
        return "table"
    return "narrative"


def extract_headings(text: str) -> List[str]:
    """Extract markdown-style headings from text."""
    headings = []
    for line in text.split("\n"):
        if re.match(r"^#{1,6}\s+", line):
            headings.append(line.strip("# ").strip())
    return headings


def chunk_text_semantic(
    text: str,
    target_chunk_size: int = 1000,
    min_chunk_size: int = 500,
    max_chunk_size: int = 1500,
    overlap: int = 150,
) -> List[Dict[str, Any]]:
    """
    Smart semantic chunking that respects sentence and paragraph boundaries.

    Returns list of dicts with 'content' and 'metadata' keys.
    """
    # Split into paragraphs
    paragraphs = re.split(r"\n\s*\n", text)

    chunks = []
    current_chunk = []
    current_size = 0
    chunk_index = 0
    total_chars = len(text)
    char_position = 0

    for para_idx, paragraph in enumerate(paragraphs):
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        # Detect if paragraph is a special structure (code, list, table)
        content_type = detect_content_type(paragraph)

        # Keep special structures together if possible
        if (
            content_type in ["code", "list", "table"]
            and len(paragraph) < max_chunk_size
        ):
            # If current chunk + this structure is too big, flush current chunk
            if current_size + len(paragraph) > max_chunk_size and current_chunk:
                chunk_content = "\n\n".join(current_chunk)
                chunks.append(
                    {
                        "content": chunk_content,
                        "metadata": {
                            "chunk_index": chunk_index,
                            "char_start": char_position - current_size,
                            "char_end": char_position,
                            "position_ratio": (char_position - current_size)
                            / total_chars
                            if total_chars > 0
                            else 0,
                            "content_type": detect_content_type(chunk_content),
                            "headings": extract_headings(chunk_content),
                        },
                    }
                )
                chunk_index += 1
                current_chunk = []
                current_size = 0

            current_chunk.append(paragraph)
            current_size += len(paragraph) + 2  # +2 for \n\n
            char_position += len(paragraph) + 2
            continue

        # For narrative text, split into sentences
        sentences = sent_tokenize(paragraph)

        for sent_idx, sentence in enumerate(sentences):
            sentence_len = len(sentence)

            # If adding this sentence exceeds max size, flush current chunk
            if current_size + sentence_len > max_chunk_size and current_chunk:
                chunk_content = "\n\n".join(current_chunk)
                chunks.append(
                    {
                        "content": chunk_content,
                        "metadata": {
                            "chunk_index": chunk_index,
                            "char_start": char_position - current_size,
                            "char_end": char_position,
                            "position_ratio": (char_position - current_size)
                            / total_chars
                            if total_chars > 0
                            else 0,
                            "content_type": detect_content_type(chunk_content),
                            "headings": extract_headings(chunk_content),
                        },
                    }
                )
                chunk_index += 1

                # Keep overlap from previous chunk
                overlap_text = (
                    chunk_content[-overlap:]
                    if len(chunk_content) > overlap
                    else chunk_content
                )
                current_chunk = [overlap_text]
                current_size = len(overlap_text)

            # Add sentence to current chunk
            if current_chunk and not current_chunk[-1].endswith(sentence):
                current_chunk.append(sentence)
            elif not current_chunk:
                current_chunk.append(sentence)
            else:
                current_chunk[-1] += " " + sentence

            current_size += sentence_len + 1  # +1 for space
            char_position += sentence_len + 1

            # If we've reached a good chunk size and we're at paragraph boundary, flush
            if current_size >= target_chunk_size and sent_idx == len(sentences) - 1:
                chunk_content = "\n\n".join(current_chunk)
                chunks.append(
                    {
                        "content": chunk_content,
                        "metadata": {
                            "chunk_index": chunk_index,
                            "char_start": char_position - current_size,
                            "char_end": char_position,
                            "position_ratio": (char_position - current_size)
                            / total_chars
                            if total_chars > 0
                            else 0,
                            "content_type": detect_content_type(chunk_content),
                            "headings": extract_headings(chunk_content),
                        },
                    }
                )
                chunk_index += 1
                current_chunk = []
                current_size = 0

    # Flush remaining content
    if current_chunk:
        chunk_content = "\n\n".join(current_chunk)
        chunks.append(
            {
                "content": chunk_content,
                "metadata": {
                    "chunk_index": chunk_index,
                    "char_start": char_position - current_size,
                    "char_end": char_position,
                    "position_ratio": (char_position - current_size) / total_chars
                    if total_chars > 0
                    else 0,
                    "content_type": detect_content_type(chunk_content),
                    "headings": extract_headings(chunk_content),
                },
            }
        )

    return chunks


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Legacy chunking function - kept for backward compatibility."""
    chunks_with_metadata = chunk_text_semantic(
        text, target_chunk_size=chunk_size, overlap=overlap
    )
    return [chunk["content"] for chunk in chunks_with_metadata]
