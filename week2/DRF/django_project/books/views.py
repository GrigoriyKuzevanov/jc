import django.db.utils
from django.db.models import F
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


class AuthorViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Author.objects.all().prefetch_related("books")
    serializer_class = AuthorSerializer


class BookViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @action(detail=True, methods=["get"])
    def buy(self, request, pk):
        try:
            book = self.get_object()
            book.count = F("count") - 1
            book.save(update_fields=("count",))
            return Response({"status": "success"})
        except django.db.utils.IntegrityError as e:
            return Response({"status": "error", "detail": "all books are sold"})
