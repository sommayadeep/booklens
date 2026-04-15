from django.contrib import admin

from .models import Book, BookChunk, QAInteraction


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "rating", "genre", "ai_processed", "created_at")
    search_fields = ("title", "author", "description", "book_url")
    list_filter = ("ai_processed", "genre")


@admin.register(BookChunk)
class BookChunkAdmin(admin.ModelAdmin):
    list_display = ("book", "chunk_index", "token_count")
    search_fields = ("book__title", "content")


@admin.register(QAInteraction)
class QAInteractionAdmin(admin.ModelAdmin):
    list_display = ("book", "created_at")
    search_fields = ("question", "answer")
