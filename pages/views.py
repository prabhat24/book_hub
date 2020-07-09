from django.shortcuts import render, redirect
from django.views import View
from books.views import BookList

def home_view(request):
    return redirect('books')