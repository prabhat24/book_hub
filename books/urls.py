from django.urls import path
from .views import BookDetail, BookList, BuyBook, gbook_search
urlpatterns = [
    path("", BookList.as_view(), name='book_list'),
    path("<slug:slug>", BookDetail.as_view(), name='book_detail'),
    path("buy/<slug:book>", BuyBook.as_view(), name='buy'),
]
