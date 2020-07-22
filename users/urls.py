from django.urls import path
from .views import signup, login

urlpatterns = [
    path("login/", login, name='custom_login'),
    path("signup/", signup, name='custom_signup'),
]
