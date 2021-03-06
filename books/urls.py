from django.urls import path
from .views import *

urlpatterns = [
    path("", BookList.as_view(), name='books'),
    path("<uuid:id>", BookDetail.as_view(), name='book_detail'),
    path("add_book/<int:book_id>", add_book, name="add_book"),
    path("charge/", BuyBooks.as_view(), name='charge'),
    path("like_review/", like_review, name='like_review'),
    path("cart/", cart, name="cart"),
    path("ship/", ship, name='ship'),
    path("checkout/", checkout, name='checkout'),
    path("update_cart/", update_cart, name='update_cart'),
    path("link_address/", link_address, name='link_address'),
]
