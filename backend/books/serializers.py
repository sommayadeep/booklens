from rest_framework import serializers

from .models import Book, QAInteraction


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "rating",
            "reviews_count",
            "description",
            "book_url",
            "image_url",
            "genre",
            "summary",
            "ai_processed",
            "created_at",
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "rating",
            "reviews_count",
            "description",
            "book_url",
            "image_url",
            "summary",
            "genre",
            "sentiment",
            "ai_processed",
            "metadata",
            "created_at",
            "updated_at",
        ]


class ScrapeRequestSerializer(serializers.Serializer):
    pages = serializers.IntegerField(min_value=1, max_value=200, default=50)
    max_books = serializers.IntegerField(min_value=1, max_value=10000, default=1000)
    process_ai = serializers.BooleanField(default=True)
    ai_limit = serializers.IntegerField(min_value=0, max_value=2000, default=120)


class UploadBookSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    author = serializers.CharField(max_length=255, required=False, allow_blank=True)
    rating = serializers.FloatField(required=False, allow_null=True)
    reviews_count = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    book_url = serializers.URLField()
    image_url = serializers.URLField(required=False, allow_blank=True)


class BulkUploadSerializer(serializers.Serializer):
    books = UploadBookSerializer(many=True)


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000)
    book_id = serializers.IntegerField(required=False, allow_null=True)


class QAInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAInteraction
        fields = ["id", "book", "question", "answer", "sources", "created_at"]
