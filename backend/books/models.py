from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, default="Unknown")
    rating = models.FloatField(null=True, blank=True)
    reviews_count = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True, default="")
    book_url = models.URLField(unique=True)
    image_url = models.URLField(blank=True, default="")

    summary = models.TextField(blank=True, default="")
    genre = models.CharField(max_length=100, blank=True, default="General")
    sentiment = models.CharField(max_length=100, blank=True, default="Neutral")
    ai_processed = models.BooleanField(default=False)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class BookChunk(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.PositiveIntegerField()
    content = models.TextField()
    token_count = models.PositiveIntegerField(default=0)
    vector_id = models.CharField(max_length=128, unique=True)

    class Meta:
        ordering = ["book", "chunk_index"]
        unique_together = ("book", "chunk_index")

    def __str__(self) -> str:
        return f"{self.book.title} [{self.chunk_index}]"


class QAInteraction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, related_name="qa_logs", null=True, blank=True)
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Q&A #{self.pk}"
