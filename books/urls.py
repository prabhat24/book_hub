from django.urls import path
from .views import BookDetail, BookList, BuyBook, add_book

urlpatterns = [
    path("", BookList.as_view(), name='book_list'),
    path("<slug:slug>", BookDetail.as_view(), name='book_detail'),
    path("add_book/<int:book_id>", add_book, name="add_book"),
    path("buy/<slug:book>", BuyBook.as_view(), name='buy'),
]
