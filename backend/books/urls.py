from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AskQuestionAPIView, BookViewSet, QAHistoryAPIView

router = DefaultRouter()
router.register("books", BookViewSet, basename="books")

urlpatterns = [
    path("", include(router.urls)),
    path("rag/ask/", AskQuestionAPIView.as_view(), name="rag-ask"),
    path("rag/history/", QAHistoryAPIView.as_view(), name="rag-history"),
]
