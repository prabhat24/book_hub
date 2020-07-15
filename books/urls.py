from django.urls import path
from .views import BookDetail, BookList, BuyBook, add_book, like_review, cart, checkout, update_cart

urlpatterns = [
    path("", BookList.as_view(), name='books'),
    path("<slug:slug>", BookDetail.as_view(), name='book_detail'),
    path("add_book/<int:book_id>", add_book, name="add_book"),
    path("buy/<slug:book>", BuyBook.as_view(), name='buy'),
    path("like_review/", like_review, name='like_review'),
    path("cart/", cart, name="cart"),
    path("checkout/", checkout, name='checkout'),
    path("update_cart/", update_cart ,name='update_cart'),
]
