from __future__ import annotations

import hashlib
import re
from typing import List

from django.core.cache import cache

from books.models import Book

from .ai_client import AIClient
from .embeddings import EmbeddingService, cosine_similarity


class InsightService:
    def __init__(self) -> None:
        self.ai_client = AIClient()
        self.embedding_service = EmbeddingService()

    def generate_summary(self, title: str, description: str) -> str:
        description = (description or "").strip()
        if not description:
            return "Summary unavailable."

        cache_key = self._cache_key("summary", f"{title}:{description}")
        cached = cache.get(cache_key)
        if cached:
            return cached

        system_prompt = "You summarize books in 3 concise sentences for readers."
        user_prompt = f"Book title: {title}\nDescription:\n{description}\n\nReturn only the summary."
        generated = self.ai_client.generate(system_prompt=system_prompt, user_prompt=user_prompt)

        if not generated:
            generated = self._extractive_summary(description)

        cache.set(cache_key, generated)
        return generated

    def classify_genre(self, title: str, description: str) -> str:
        text = f"{title} {description}".lower()
        cache_key = self._cache_key("genre", text)
        cached = cache.get(cache_key)
        if cached:
            return cached

        keyword_map = {
            "Science Fiction": ["space", "future", "robot", "ai", "dystopia", "alien"],
            "Fantasy": ["magic", "dragon", "kingdom", "sword", "wizard", "myth"],
            "Mystery": ["murder", "detective", "crime", "clue", "investigation"],
            "Romance": ["love", "romance", "heart", "relationship"],
            "Thriller": ["chase", "conspiracy", "spy", "survival", "suspense"],
            "Historical Fiction": ["war", "empire", "century", "historical", "victorian"],
            "Self Help": ["habit", "mindset", "productivity", "discipline", "growth"],
            "Business": ["startup", "leadership", "strategy", "finance", "market"],
            "Non Fiction": ["biography", "memoir", "research", "true story"],
        }

        scores = {genre: 0 for genre in keyword_map}
        for genre, words in keyword_map.items():
            for word in words:
                if word in text:
                    scores[genre] += 1

        best_genre = max(scores, key=scores.get)
        if scores[best_genre] == 0:
            best_genre = "General"

        cache.set(cache_key, best_genre)
        return best_genre

    def analyze_sentiment(self, text: str) -> str:
        text = (text or "").lower()
        cache_key = self._cache_key("sentiment", text)
        cached = cache.get(cache_key)
        if cached:
            return cached

        positive_words = {
            "excellent",
            "great",
            "inspiring",
            "beautiful",
            "amazing",
            "heartwarming",
            "compelling",
            "engaging",
            "brilliant",
            "uplifting",
        }
        negative_words = {
            "boring",
            "weak",
            "predictable",
            "flat",
            "confusing",
            "slow",
            "disappointing",
            "poor",
            "dark",
            "grim",
        }

        tokens = re.findall(r"[a-zA-Z]+", text)
        positive_score = sum(1 for t in tokens if t in positive_words)
        negative_score = sum(1 for t in tokens if t in negative_words)

        if positive_score > negative_score:
            sentiment = "Positive"
        elif negative_score > positive_score:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        cache.set(cache_key, sentiment)
        return sentiment

    def enrich_book(self, book: Book) -> Book:
        summary = self.generate_summary(book.title, book.description)
        genre = self.classify_genre(book.title, book.description)
        sentiment = self.analyze_sentiment(book.description)

        book.summary = summary
        book.genre = genre
        book.sentiment = sentiment
        book.ai_processed = True
        book.save(update_fields=["summary", "genre", "sentiment", "ai_processed", "updated_at"])
        return book

    def recommend_related(self, book: Book, top_k: int = 4) -> List[Book]:
        cache_key = self._cache_key("rec", f"{book.pk}:{book.updated_at.timestamp()}:{top_k}")
        cached_ids = cache.get(cache_key)
        if cached_ids is not None:
            books_by_id = {b.id: b for b in Book.objects.filter(id__in=cached_ids)}
            return [books_by_id[b_id] for b_id in cached_ids if b_id in books_by_id]

        corpus = Book.objects.exclude(id=book.id)
        if not corpus.exists():
            return []

        anchor_text = " ".join([book.title, book.description, book.genre]).strip()
        anchor_vec = self.embedding_service.embed_text(anchor_text)

        scored = []
        for candidate in corpus:
            candidate_text = " ".join([candidate.title, candidate.description, candidate.genre]).strip()
            if not candidate_text:
                continue
            candidate_vec = self.embedding_service.embed_text(candidate_text)
            score = cosine_similarity(anchor_vec, candidate_vec)
            scored.append((score, candidate))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored[:top_k]]
        cache.set(cache_key, [book.id for book in results])
        return results

    @staticmethod
    def _extractive_summary(description: str, max_words: int = 70) -> str:
        words = description.split()
        if len(words) <= max_words:
            return description
        return " ".join(words[:max_words]).rstrip(".,") + "..."

    @staticmethod
    def _cache_key(prefix: str, content: str) -> str:
        digest = hashlib.md5(content.encode("utf-8")).hexdigest()
        return f"booklens:{prefix}:{digest}"
