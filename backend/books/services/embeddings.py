from __future__ import annotations

import hashlib
import math
import os
import re
from functools import lru_cache
from typing import List


class EmbeddingService:
    """Tries local sentence-transformer, then deterministic hash embeddings."""

    def __init__(self) -> None:
        self.dim = int(os.getenv("FALLBACK_EMBEDDING_DIM", "384"))

    @lru_cache(maxsize=1)
    def _sentence_model(self):
        model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        try:
            from sentence_transformers import SentenceTransformer

            return SentenceTransformer(model_name)
        except Exception:
            return None

    def embed_text(self, text: str) -> List[float]:
        text = (text or "").strip()
        if not text:
            return [0.0] * self.dim

        model = self._sentence_model()
        if model is not None:
            try:
                vector = model.encode([text], normalize_embeddings=True)[0]
                return [float(v) for v in vector]
            except Exception:
                pass

        return self._hash_embedding(text)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        model = self._sentence_model()
        if model is not None:
            try:
                vectors = model.encode(texts, normalize_embeddings=True)
                return [[float(v) for v in row] for row in vectors]
            except Exception:
                pass

        return [self._hash_embedding(text or "") for text in texts]

    def _hash_embedding(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dim
            sign = -1.0 if digest[4] % 2 else 1.0
            weight = 1.0 + (len(token) % 3) * 0.2
            vec[bucket] += sign * weight

        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return float(sum(x * y for x, y in zip(a, b)))
