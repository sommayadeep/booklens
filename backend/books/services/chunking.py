from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class TextChunk:
    index: int
    content: str
    token_count: int


class SmartChunker:
    """Simple overlapping word window chunker with sentence-aware joins."""

    def __init__(self, chunk_size: int = 220, overlap: int = 40) -> None:
        self.chunk_size = max(80, chunk_size)
        self.overlap = max(10, min(overlap, self.chunk_size // 2))

    def chunk(self, text: str) -> List[TextChunk]:
        words = text.split()
        if not words:
            return []

        chunks: List[TextChunk] = []
        start = 0
        idx = 0
        while start < len(words):
            end = min(len(words), start + self.chunk_size)
            window = words[start:end]
            content = " ".join(window).strip()
            if content:
                chunks.append(TextChunk(index=idx, content=content, token_count=len(window)))
                idx += 1

            if end >= len(words):
                break
            start = max(0, end - self.overlap)

        return chunks
