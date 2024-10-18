from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
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
            new_count = book.count - 1
            if new_count < 0:
                return Response({"status": "error", "detail": "all books are sold"})
            book.count = new_count
            book.save()

        except ObjectDoesNotExist:
            return Response(
                {"status": "error", "detail": f"Book with id {pk} does not exist"}
            )

        return Response({"status": "success", "count": new_count})
