from django.views.generic import ListView, DetailView
from .models import Book, Review
from django.views import View
from .forms import ReviewCreationForm, SearchBooksForm
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
import stripe
from django.http import HttpResponse
from .scripts import GoogleBooksClient


class BookList(ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"


class BookDetail(View):
    model = Book
    template_name = "books/book_detail.html"
    form_class = ReviewCreationForm
    context_data = {}

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        book = self.model.objects.filter(slug=self.kwargs['slug']).first()
        self.context_data['book'] = book
        self.context_data['form'] = form
        self.context_data['reviews'] = book.reviews.all()
        self.context_data['slug'] = self.kwargs['slug']
        return render(request, self.template_name, self.context_data)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        self.context_data['slug'] = self.kwargs['slug']
        book = self.model.objects.filter(slug=self.kwargs['slug']).first()
        self.context_data['book'] = book
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.book = book
            review.save()
            self.context_data['reviews'] = book.reviews.all()
        else:
            print(form.errors)
            self.context_data['reviews'] = book.reviews.all()
        return render(request, self.template_name, self.context_data)


class BuyBook(View):
    def get(self, request, *args, **kwargs):
        book = Book.objects.filter(slug=self.kwargs['book']).first()
        context = {
            'book': book
        }
        return render(request, 'books/charge.html', context)

    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        publish_key = settings.STRIPE_PUBLISHABLE_KEY
        book = Book.objects.filter(slug=self.kwargs['book']).first()
        amount = int(book.price * 100)
        print(f'data:{request.POST}')
        stripe_token = request.POST['stripeToken']

        customer = stripe.Customer.create(
            email=request.user.email,
            name=request.user.username,
            source=stripe_token
        )
        charge = stripe.Charge.create(
            customer=customer,
            amount=amount,
            currency='inr',
            description='example',
        )
        return HttpResponse('payment successful')


def add_book(request):
    parsed_books = []

    class NewBook():
        def __init__(self, title, author, price, cover, publisher, isbn10, isbn13, published_date, pages,
                     language):
            self.title = title
            self.author = author
            self.price = price
            self.cover = cover
            self.publisher = publisher
            self.isbn10 = isbn10
            self.isbn13 = isbn13
            self.published_date = published_date
            self.pages = pages
            self.language = language

    if request.method == "POST":
        search_form = SearchBooksForm(request.POST)
        if search_form.is_valid():
            cleaned_form = search_form.cleaned_data
            data = cleaned_form.get('search_field')
            api = GoogleBooksClient()
            book_list = api.list(data).get('items', None)
            for book in book_list:
                volume_info = book.get("volumeInfo")
                retailPrice = book.get("retailPrice", None)
                image_links = volume_info.get("imageLinks", None)
                industry_identifiers = volume_info.get("industryIdentifiers", None)
                isbn_13 = None
                isbn_10 = None
                for item in industry_identifiers:
                    isbn_13 = item["identifier"] if item['type'] == "ISBN_13" else isbn_13
                    isbn_10 = item["identifier"] if item['type'] == "ISBN_10" else isbn_10
                new_book = NewBook(
                    title=volume_info.get("title") + " " + volume_info.get("subtitle"),
                    author=volume_info.get("authors")[0],
                    price=retailPrice.get("amount", None),
                    cover=image_links('thumbnail', None) if image_links else None,
                    publisher=volume_info.get("publisher", None),
                    isbn10=isbn_10,
                    isbn13=isbn_13,
                    published_date=volume_info.get('publishedDate', None),
                    pages=volume_info.get('pageCount', None),
                    language=volume_info.get('language', None)
                )
                parsed_books = parsed_books.append(new_book)
        else:
            search_form = SearchBooksForm()

        context = {
            'form': search_form,
            'books': parsed_books
        }
        return render(request, 'books/add_books.html', context)
