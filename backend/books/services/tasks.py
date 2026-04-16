from celery import shared_task
from books.models import Book
from .insights import InsightService
from .rag import RagService

@shared_task
def enrich_book_ai_async(book_id):
    book = Book.objects.get(id=book_id)
    insight_service = InsightService()
    rag_service = RagService()
    insight_service.enrich_book(book)
    rag_service.index_book(book)
    return True
