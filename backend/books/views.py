from __future__ import annotations

from typing import Dict, List

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book, BookChunk, QAInteraction
from .serializers import (
    AskQuestionSerializer,
    BookDetailSerializer,
    BookListSerializer,
    BulkUploadSerializer,
    QAInteractionSerializer,
    ScrapeRequestSerializer,
)
from .services.insights import InsightService
from .services.rag import RagService
from .services.scraper import scrape_books


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookDetailSerializer

    @action(detail=True, methods=["get"])
    def recommendations(self, request, pk=None):
        book = self.get_object()
        service = InsightService()
        recommended = service.recommend_related(book, top_k=4)
        payload = BookListSerializer(recommended, many=True, context={"request": request}).data
        return Response({"book_id": book.id, "recommendations": payload})

    @action(detail=False, methods=["post"], url_path="scrape")
    def scrape_and_process(self, request):
        # Lowered defaults for demo speed
        serializer = ScrapeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pages = serializer.validated_data.get("pages", 2)
        max_books = serializer.validated_data.get("max_books", 10)
        process_ai = serializer.validated_data.get("process_ai", True)
        ai_limit = serializer.validated_data.get("ai_limit", 10)

        raw_books = scrape_books(pages=pages, max_books=max_books)
        if not raw_books:
            return Response(
                {"detail": "No books were scraped. Verify network and scraping setup."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        insight_service = InsightService()
        rag_service = RagService()
    @action(detail=False, methods=["post"], url_path="demo-upload")
    def demo_upload(self, request):
        """Instantly load fallback/sample books for demo speed."""
        from .services.scraper import _fallback_books
        fallback_books = _fallback_books(max_books=8)
        insight_service = InsightService()
        rag_service = RagService()
        created = 0
        indexed_chunks = 0
        processed_books = []
        for item in fallback_books:
            defaults = {
                "title": item["title"],
                "author": item.get("author") or "Unknown",
                "rating": item.get("rating") or 0,
                "reviews_count": item.get("reviews_count") or 0,
                "description": item.get("description", ""),
                "image_url": item.get("image_url", ""),
                "metadata": item.get("metadata", {}),
            }
            book, was_created = Book.objects.update_or_create(book_url=item["book_url"], defaults=defaults)
            if was_created:
                created += 1
            insight_service.enrich_book(book)
            indexed_chunks += rag_service.index_book(book)
            processed_books.append({"id": book.id, "title": book.title})
        return Response(
            {
                "detail": "Demo books uploaded and processed.",
                "created": created,
                "indexed_chunks": indexed_chunks,
                "books": processed_books,
            },
            status=status.HTTP_201_CREATED,
        )

        created = 0
        updated = 0
        indexed_chunks = 0
        processed_books: List[Dict] = []

        ai_processed_count = 0
        for idx, item in enumerate(raw_books):
            defaults = {
                "title": item.get("title", "Untitled"),
                "author": item.get("author", "Unknown") or "Unknown",
                "rating": item.get("rating") or 0,
                "reviews_count": item.get("reviews_count") or 0,
                "description": item.get("description", ""),
                "image_url": item.get("image_url", ""),
                "metadata": item.get("metadata", {}),
            }
            book, was_created = Book.objects.update_or_create(book_url=item["book_url"], defaults=defaults)
            if was_created:
                created += 1
            else:
                updated += 1

            if process_ai and idx < ai_limit:
                insight_service.enrich_book(book)
                indexed_chunks += rag_service.index_book(book)
                ai_processed_count += 1
            processed_books.append({"id": book.id, "title": book.title})

        return Response(
            {
                "detail": "Scraping and AI processing completed.",
                "created": created,
                "updated": updated,
                "total_processed": len(processed_books),
                "ai_processed_count": ai_processed_count,
                "indexed_chunks": indexed_chunks,
                "books": processed_books,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="upload")
    def upload_books(self, request):
        serializer = BulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        insight_service = InsightService()
        rag_service = RagService()

        upserted = 0
        chunks = 0

        with transaction.atomic():
            for item in serializer.validated_data["books"]:
                defaults = {
                    "title": item["title"],
                    "author": item.get("author") or "Unknown",
                    "rating": item.get("rating") or 0,
                    "reviews_count": item.get("reviews_count") or 0,
                    "description": item.get("description", ""),
                    "image_url": item.get("image_url", ""),
                }
                book, _ = Book.objects.update_or_create(book_url=item["book_url"], defaults=defaults)
                insight_service.enrich_book(book)
                chunks += rag_service.index_book(book)
                upserted += 1

        return Response(
            {
                "detail": "Books uploaded and processed successfully.",
                "upserted": upserted,
                "indexed_chunks": chunks,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        book_count = Book.objects.count()
        ai_processed = Book.objects.filter(ai_processed=True).count()
        chunk_count = BookChunk.objects.count()
        genre_count = Book.objects.exclude(genre="").values("genre").distinct().count()
        qa_count = QAInteraction.objects.count()

        return Response(
            {
                "total_books": book_count,
                "ai_processed": ai_processed,
                "text_chunks": chunk_count,
                "genres": genre_count,
                "qa_sessions": qa_count,
            }
        )


class AskQuestionAPIView(APIView):
    def post(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data["question"]
        book_id = serializer.validated_data.get("book_id")

        book = None
        if book_id:
            book = Book.objects.filter(id=book_id).first()
            if not book:
                return Response({"detail": "Invalid book_id"}, status=status.HTTP_400_BAD_REQUEST)

        rag_service = RagService()
        response_payload = rag_service.answer_question(question=question, book_id=book_id)

        log = QAInteraction.objects.create(
            book=book,
            question=question,
            answer=response_payload["answer"],
            sources=response_payload["sources"],
        )

        return Response({"id": log.id, **response_payload}, status=status.HTTP_200_OK)


class QAHistoryAPIView(APIView):
    def get(self, request):
        logs = QAInteraction.objects.select_related("book").all()[:50]
        serializer = QAInteractionSerializer(logs, many=True)
        return Response(serializer.data)
