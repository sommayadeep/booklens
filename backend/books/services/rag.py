from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

from django.conf import settings
from django.core.cache import cache

from books.models import Book, BookChunk

from .ai_client import AIClient
from .chunking import SmartChunker
from .embeddings import EmbeddingService, cosine_similarity

try:
    import chromadb
except Exception:  # pragma: no cover
    chromadb = None


class RagService:
    def __init__(self) -> None:
        self.chunker = SmartChunker(chunk_size=settings.CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP)
        self.embedding_service = EmbeddingService()
        self.ai_client = AIClient()
        self._client = None
        self._collection = None

        if chromadb is not None:
            try:
                self._client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
                self._collection = self._client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION,
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception:
                self._client = None
                self._collection = None

    def index_book(self, book: Book) -> int:
        text = self._book_corpus(book)
        chunks = self.chunker.chunk(text)

        if not chunks:
            BookChunk.objects.filter(book=book).delete()
            return 0

        existing_vector_ids = list(BookChunk.objects.filter(book=book).values_list("vector_id", flat=True))
        if self._collection and existing_vector_ids:
            try:
                self._collection.delete(ids=existing_vector_ids)
            except Exception:
                pass

        BookChunk.objects.filter(book=book).delete()

        ids = [f"book-{book.id}-chunk-{chunk.index}" for chunk in chunks]
        docs = [chunk.content for chunk in chunks]
        embeddings = self.embedding_service.embed_texts(docs)
        metadatas = [
            {
                "book_id": int(book.id),
                "book_title": book.title,
                "book_url": book.book_url,
                "chunk_index": int(chunk.index),
            }
            for chunk in chunks
        ]

        db_rows = [
            BookChunk(
                book=book,
                chunk_index=chunk.index,
                content=chunk.content,
                token_count=chunk.token_count,
                vector_id=chunk_id,
            )
            for chunk, chunk_id in zip(chunks, ids)
        ]
        BookChunk.objects.bulk_create(db_rows)

        if self._collection:
            try:
                self._collection.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)
            except Exception:
                pass

        return len(chunks)

    def answer_question(self, question: str, book_id: Optional[int] = None) -> Dict:
        cache_key = self._cache_key(question, book_id)
        cached = cache.get(cache_key)
        if cached:
            return cached

        context_chunks = self.retrieve_chunks(question, book_id=book_id, top_k=settings.TOP_K_CHUNKS)
        if not context_chunks:
            payload = {
                "answer": "I could not find relevant content for this question in the indexed books.",
                "sources": [],
                "book_id": book_id,
            }
            cache.set(cache_key, payload)
            return payload

        context_text = "\n\n".join(
            [f"[S{i+1}] {item['book_title']} (chunk {item['chunk_index']}): {item['content']}" for i, item in enumerate(context_chunks)]
        )

        system_prompt = (
            "You are a book assistant. Answer only using provided context. "
            "Cite sources using [S1], [S2] style after each important statement."
        )
        user_prompt = (
            f"Question: {question}\n\n"
            f"Context:\n{context_text}\n\n"
            "Return a concise answer with source citations."
        )
        generated = self.ai_client.generate(system_prompt=system_prompt, user_prompt=user_prompt, max_tokens=420)
        answer = generated or self._fallback_answer(question, context_chunks)

        payload = {
            "answer": answer,
            "sources": [
                {
                    "source_id": f"S{i+1}",
                    "book_id": item["book_id"],
                    "book_title": item["book_title"],
                    "book_url": item["book_url"],
                    "chunk_index": item["chunk_index"],
                    "snippet": item["content"][:280],
                }
                for i, item in enumerate(context_chunks)
            ],
            "book_id": book_id,
        }
        cache.set(cache_key, payload)
        return payload

    def retrieve_chunks(self, question: str, book_id: Optional[int], top_k: int = 5) -> List[Dict]:
        query_embedding = self.embedding_service.embed_text(question)

        if self._collection is not None:
            try:
                where = {"book_id": int(book_id)} if book_id else None
                results = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where,
                    include=["documents", "metadatas", "distances"],
                )
                documents = results.get("documents", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]
                if documents and metadatas:
                    merged = []
                    for doc, meta in zip(documents, metadatas):
                        merged.append(
                            {
                                "content": doc,
                                "book_id": meta.get("book_id"),
                                "book_title": meta.get("book_title", "Unknown"),
                                "book_url": meta.get("book_url", ""),
                                "chunk_index": meta.get("chunk_index", 0),
                            }
                        )
                    return merged
            except Exception:
                pass

        queryset = BookChunk.objects.select_related("book")
        if book_id:
            queryset = queryset.filter(book_id=book_id)

        scored = []
        for chunk in queryset[:5000]:
            emb = self.embedding_service.embed_text(chunk.content)
            score = cosine_similarity(query_embedding, emb)
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]

        return [
            {
                "content": chunk.content,
                "book_id": chunk.book_id,
                "book_title": chunk.book.title,
                "book_url": chunk.book.book_url,
                "chunk_index": chunk.chunk_index,
            }
            for _, chunk in top
        ]

    @staticmethod
    def _book_corpus(book: Book) -> str:
        return "\n\n".join(
            [
                f"Title: {book.title}",
                f"Author: {book.author}",
                f"Description: {book.description}",
                f"Summary: {book.summary}",
                f"Genre: {book.genre}",
            ]
        )

    @staticmethod
    def _fallback_answer(question: str, chunks: List[Dict]) -> str:
        lead = "Based on the indexed book context, here is what I found:"
        evidence = " ".join([f"[{f'S{i+1}'}] {chunk['content'][:160]}" for i, chunk in enumerate(chunks[:3])])
        return f"{lead} {evidence}"

    @staticmethod
    def _cache_key(question: str, book_id: Optional[int]) -> str:
        payload = f"{book_id or 'all'}::{question.strip().lower()}"
        digest = hashlib.md5(payload.encode("utf-8")).hexdigest()
        return f"booklens:rag:{digest}"
