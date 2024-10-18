from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    count = models.PositiveIntegerField()

    author = models.ForeignKey("Author", related_name="books", on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
