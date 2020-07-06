from django.core.management import BaseCommand
from books.models import Book


class DummyBook:
    def ___init__(self, title, author, price, cover):
        self.title = title
        self.author = author
        self.price = price
        self.cover = cover


class Command(BaseCommand):
    def handle(self, *args, **options):
        books = [
            DummyBook(title="Django for Professionals", author="abc")
        ]
