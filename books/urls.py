from django.urls import path
from .views import BookDetail, BookList

urlpatterns = [
    path("", BookList.as_view(), name='book_list'),
    path("<slug:slug>", BookDetail.as_view(), name='book_detail'),
]