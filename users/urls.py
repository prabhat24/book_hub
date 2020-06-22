from django.urls import path
from .views import SignUp

urlpatterns = [
    path("register/", SignUp.as_view(), name='register_user')
]
