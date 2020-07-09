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
from django.conf import settings
import os
import requests
import uuid
from django.db.models import Q


class BookList(View):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"

    def get(self, request, *args, **kwargs):
        context = {
            self.context_object_name: self.get_queryset(request)
        }
        return render(request, self.template_name, context)

    def get_queryset(self, request):
        if 'query' in request.GET:
            query = request.GET['query']
            return self.model.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
        return self.model.objects.all()


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


class NewBook():
    def __init__(self, title, author, price, publisher, isbn10, isbn13, published_date, pages,
                 language, cover=None, description=None):
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
        self.description = description


class GbookSearch(View):
    context = {
        'form': None,
        'books': None
    }

    def get(self, request, *args, **kwargs):
        search_form = SearchBooksForm()
        self.context['form'] = search_form
        return render(request, 'books/gbook_search.html', self.context)

    def post(self, request, *args, **kwargs):
        parsed_books = []
        serialized_parsed_books = []
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
                subtitle = volume_info.get("subtitle", None)
                for item in (industry_identifiers if industry_identifiers else list()):
                    isbn_13 = item["identifier"] if item['type'] == "ISBN_13" else isbn_13
                    isbn_10 = item["identifier"] if item['type'] == "ISBN_10" else isbn_10
                new_book = NewBook(
                    title=volume_info.get("title") + " " + subtitle if subtitle else volume_info.get("title"),
                    author=volume_info.get("authors")[0] if volume_info.get("authors") else None,
                    price=retailPrice.get("amount", None) if retailPrice else None,
                    cover=image_links.get('thumbnail', None) if image_links else None,
                    publisher=volume_info.get("publisher", None),
                    isbn10=isbn_10,
                    isbn13=isbn_13,
                    published_date=volume_info.get('publishedDate', None),
                    pages=volume_info.get('pageCount', None),
                    language=volume_info.get('language', None),
                    description=volume_info.get('description', None)
                )
                parsed_books.append(new_book)
                serialized_parsed_books.append(new_book.__dict__)

        self.context['books'] = parsed_books
        self.context['form'] = search_form
        request.session['serialized_books'] = serialized_parsed_books
        return render(request, 'books/gbook_search.html', self.context)


def add_book(request, book_id):
    global required_book
    if request.method == "GET":
        required_book = request.session.get('serialized_books')[book_id]
        for key, values in required_book.items():
            if not required_book[key]:
                required_book[key] = ""
        return render(request, 'books/add_book.html', {'book': required_book})

    elif request.method == "POST":
        post_values = request.POST
        book = NewBook(
            title=post_values.get('title'),
            author=post_values.get('author'),
            price=float(post_values.get('price')),
            publisher=post_values.get('publisher'),
            isbn10=post_values.get('isbn10'),
            isbn13=post_values.get('isbn13'),
            published_date=post_values.get('published_date'),
            pages=int(post_values.get('pages')),
            language=post_values.get('language'),
            description = post_values.get('description', None)
        )
        cover = None
        if 'cover' in request.FILES:
            cover = request.FILES['cover']
            created_book = Book.objects.create(title=book.title,
                                               author=book.author,
                                               price=book.price,
                                               publisher=book.publisher,
                                               isbn10=book.isbn10,
                                               published_date=book.published_date,
                                               language=book.language,
                                               cover=cover,
                                               description= book.description
                                               )
        else:
            cover_url = required_book.get('cover', None)
            filename = str(uuid.uuid1()) + ".jpeg"
            cover_path = os.path.join(os.path.join(settings.MEDIA_ROOT, 'covers'), filename)
            respose = requests.get(cover_url, allow_redirects=True)
            with open(cover_path, 'wb+') as f:
                f.write(respose.content)
                created_book = Book.objects.create(title=book.title,
                                                   author=book.author,
                                                   price=book.price,
                                                   publisher=book.publisher,
                                                   isbn10=book.isbn10,
                                                   published_date=book.published_date,
                                                   language=book.language,
                                                   description=book.description
                                                   )
                created_book.cover.save(filename, f)
                created_book.save()
        return HttpResponse("books added")
