from typing import List


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def chunk_text(text: str, max_chunk_size: int = 450, overlap: int = 70) -> List[str]:
    words = normalize_text(text).split()
    if not words:
        return []

    chunks: List[str] = []
    start = 0
    step = max(max_chunk_size - overlap, 1)

    while start < len(words):
        end = min(start + max_chunk_size, len(words))
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(words):
            break
        start += step
    return chunks


def snippet_for_chunk(chunk: str, max_length: int = 180) -> str:
    cleaned = normalize_text(chunk)
    if len(cleaned) <= max_length:
        return cleaned
    clipped = cleaned[:max_length]
    last_space = clipped.rfind(" ")
    if last_space > 0:
        clipped = clipped[:last_space]
    return f"{clipped}..."
