from django.views.generic import ListView, DetailView
from .models import Book

class BookList(ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"


class BookDetail(DetailView):
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"


