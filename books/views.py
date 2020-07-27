import json
import os

import requests
import stripe
from django.conf import settings
from django.contrib.auth import login
from django.db.models import Q
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.models import Group

from .decorators import authenticate_roles
from .forms import ReviewCreationForm, SearchBooksForm
from .models import *
from .scripts import GoogleBooksClient


class BookList(View):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"

    def create_cookies(self, cookie_dict, response, **kwargs):
        default_mapping = {
            'total_cart_items': '0',
            'cart': '{}',
            'session_id': kwargs['session_id']
        }
        for key, value in default_mapping.items():
            if not cookie_dict.get(key):
                response.set_cookie(key, value)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            order, created = Order.objects.get_or_create(customer=request.user, completed=False)
            context = {
                'total_cart_items': order.total_cart_items,
                self.context_object_name: self.get_queryset(request)
            }
            response = render(request, self.template_name, context)
        else:
            # create user
            session_id = request.COOKIES.get('session_id', str(uuid.uuid4()))
            username = 'anonymous_' + session_id
            anonymous_user, created = get_user_model().objects.get_or_create(username=username, is_unknown=True)
            customer_role = Group.objects.get(name='customer')
            if not hasattr(anonymous_user, 'backend'):
                for backend in settings.AUTHENTICATION_BACKENDS:
                    anonymous_user.backend = backend
                    break
            anonymous_user.groups.add(customer_role)
            anonymous_user.save()
            login(request, anonymous_user)
            order, created = Order.objects.get_or_create(customer=anonymous_user, completed=False)
            context = {
                'total_cart_items': order.total_cart_items,
                self.context_object_name: self.get_queryset(request)
            }
            response = render(request, self.template_name, context)
            self.create_cookies(request.COOKIES, response, session_id=session_id)
        return response

    def get_queryset(self, request):
        if 'query' in request.GET:
            query = request.GET['query']
            return self.model.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
        return self.model.objects.all()


@method_decorator(authenticate_roles(allowed_roles=['admin', 'customer']), name='dispatch')
class BookDetail(View):
    model = Book
    template_name = "books/book_detail.html"
    form_class = ReviewCreationForm
    context_data = {}

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        book = self.model.objects.get(id=self.kwargs['id'])
        order, created = Order.objects.get_or_create(customer=request.user, completed=False)
        self.context_data['id'] = self.kwargs['id']
        self.context_data['book'] = book
        self.context_data['form'] = form
        self.context_data['reviews'] = book.reviews.all()
        self.context_data['all_reviewers'] = [review.reviewer.username for review in book.reviews.all()]
        self.context_data['total_cart_items'] = order.total_cart_items
        return render(request, self.template_name, self.context_data)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        self.context_data['id'] = self.kwargs['id']
        book = self.model.objects.get(id=self.kwargs['id'])
        self.context_data['all_reviewers'] = [review.reviewer.username for review in book.reviews.all()]
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


@method_decorator(authenticate_roles(allowed_roles=['admin', 'customer']), name='dispatch')
class BuyBooks(View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(customer=request.user, completed=False)
        context = {
            'order': order
        }
        return render(request, 'books/charge.html', context)

    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        publish_key = settings.STRIPE_PUBLISHABLE_KEY
        order = Order.objects.get(customer=request.user, completed=False)
        order_items = order.order_items.all()
        amount = int(order.total_order_cost * 100)
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
        context = {
            'order_transaction_id': order.transaction_id,
            'shipping_details': order.shipping_detail,
            'order_items': order_items,
            'order': order,
        }
        # after verification
        order.completed = True
        order.save()
        return render(request, 'books/order_success.html', context)


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


@method_decorator(authenticate_roles(allowed_roles=['seller', 'admin']), name='dispatch')
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


@authenticate_roles(allowed_roles=['seller', 'admin'])
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
            description=post_values.get('description', None),
        )
        cover_url = required_book.get('cover', None)
        created_book = Book.objects.create(title=book.title,
                                           author=book.author,
                                           price=book.price,
                                           publisher=book.publisher,
                                           isbn10=book.isbn10,
                                           published_date=book.published_date,
                                           language=book.language,
                                           description=book.description,
                                           cover=cover_url,
                                           )
        return HttpResponse("books added")


@authenticate_roles(allowed_roles=['customer', 'admin'])
def like_review(request):
    review_id = None
    if request.method == 'GET':
        review_id = request.GET['review_id']
    likes = 0
    if review_id:
        review = Review.objects.get(id=int(review_id))
        if review:
            likes = review.likes + 1
            review.likes = likes
            review.save()
    return HttpResponse(likes)


@authenticate_roles(allowed_roles=['customer', 'admin'])
def cart(request):
    order, created = Order.objects.get_or_create(customer=request.user, completed=False)
    order_items = order.order_items.all()

    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'books/cart.html', context)


@authenticate_roles(allowed_roles=['customer', 'admin'])
def ship(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mob_no = request.POST.get('mob_no')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        country = request.POST.get('country')
        ShippingDetail.objects.create(
            name=name,
            mob_no=mob_no,
            address=address,
            city=city,
            zip_code=zip_code,
            state=state,
            country=country,
            customer=request.user
        )
    shipping_details = request.user.shipping_details.all()
    order = Order.objects.get(customer=request.user, completed=False)
    context = {
        'shipping_details': shipping_details,
        'order': order,
    }
    return render(request, 'books/shipping_details.html', context)


@authenticate_roles(allowed_roles=['customer', 'admin'])
def update_anonymous_cart(request):
    post_data = json.loads(request.body)
    book_id = post_data.get('productId', None)
    action = post_data.get('action', None)
    total_cart_items = int(request.COOKIES.get('total_cart_items', 0))
    cart = json.loads(request.COOKIES.get('cart', '{}'))
    if action == 'add_book':
        if cart.get(book_id):
            cart[book_id] += 1
        else:
            cart[book_id] = 1
        total_cart_items += 1
    response = JsonResponse("successfully added item", safe=False)
    response.set_cookie('cart', json.dumps(cart))
    response.set_cookie('total_cart_items', str(total_cart_items))
    return response


@authenticate_roles(allowed_roles=['customer', 'admin'])
def update_cart(request):
    if not request.user.is_authenticated:
        return update_anonymous_cart(request)
    post_data = json.loads(request.body)
    book_id = post_data.get('productId', None)
    action = post_data.get('action', None)
    order, created = Order.objects.get_or_create(customer=request.user, completed=False)
    order_item, created_item = order.order_items.get_or_create(book_id=book_id)
    if action == 'add_book':
        if created_item:
            order_item.quantity = 1
        else:
            order_item.quantity += 1
        order_item.save()
    elif action == 'remove_book':
        if order_item.quantity > 0:
            order_item.quantity -= 1
            order_item.save()
        if order_item.quantity == 0:
            order_item.delete()
    return JsonResponse("successfully added item", safe=False)


@authenticate_roles(allowed_roles=['customer', 'admin'])
def checkout(request):
    order = Order.objects.get(customer=request.user, completed=False)
    order_items = order.order_items.all()
    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'books/checkout.html', context)


@authenticate_roles(allowed_roles=['customer', 'admin'])
def link_address(request):
    post_data = json.loads(request.body)
    shipping_id = post_data.get('shippingId')
    action = post_data.get('action')
    order = Order.objects.get(customer=request.user, completed=False)
    if action == 'link_address':
        order.shipping_detail = ShippingDetail.objects.get(id=shipping_id)
        order.save()
        return JsonResponse("order got updated with the address", safe=False)
    return JsonResponse("action not defined", safe=False)


