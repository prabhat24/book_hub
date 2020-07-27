from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
import uuid
from .exceptions import NotValidISBN


class Book(models.Model):
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    cover = models.ImageField(upload_to="covers/", blank=True)
    slug = models.SlugField(null=True, unique=True, max_length=500)
    publisher = models.CharField(max_length=200, null=True)
    isbn10 = models.CharField(max_length=10)
    isbn13 = models.CharField(max_length=13)
    published_date = models.DateField(null=True, blank=True)
    pages = models.ImageField(null=True, blank=True)
    language = models.CharField(max_length=10)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return f"title:{self.title}, author:{self.author}"

    def save(self, *args, **kwargs):
        if self.isbn10:
            if not len(self.isbn10) == 10:
                raise NotValidISBN(10, "length of ISBN not equal to 10")
        if self.isbn13:
            if not len(self.isbn13) == 13:
                raise NotValidISBN(13, "length of ISBN not equal to 13")
        self.slug = slugify(self.title)
        super(Book, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'slug': self.slug})

    @property
    def thumbnail(self):
        if self.cover:
            return self.cover.url
        else:
            return ""


class Review(models.Model):
    review = models.CharField(max_length=1000)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_reviews')
    review_datetime = models.DateTimeField(auto_now=True)
    likes = models.IntegerField(default=0)

    # def save(self, *args, **kwargs):
    #     for review in self.reviewer.user_reviews.all():
    #         if review.book == self.book:
    #             raise ReviewsIntegrityError(
    #                 f'user {self.reviewer.username} cannot create more reviews for book {self.book.title}')
    #     super(Review, self).save()

    def __str__(self):
        return f'review: {self.review}, books: {self.book.title}, reviewer: {self.reviewer.username}'


class ShippingDetail(models.Model):
    name = models.CharField(max_length=100)
    mob_no = models.ImageField(max_length=10)
    customer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=True,
                                 related_name="shipping_details", null=True)
    address = models.CharField(max_length=1000)
    zip_code = models.CharField(max_length=6)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=30)
    country = models.CharField(max_length=20, default='India')

    def __str__(self):
        return f"Shipping_Details_id : {self.id}, customer: {self.customer}, address: {self.address}"


class Order(models.Model):
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=True, related_name="orders",
                                 null=True)
    order_date_time = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False, blank=True)
    shipping_detail = models.ForeignKey(ShippingDetail,
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        related_name='assigned_orders',
                                        blank=True)

    @property
    def total_order_cost(self):
        order_items = self.order_items.all()
        total_sum = sum([item.total_item_cost for item in order_items])
        return total_sum

    @property
    def total_cart_items(self):
        order_items = self.order_items.all()
        total_items = sum([item.quantity for item in order_items])
        return total_items

    def __str__(self):
        return f"id = {self.id}, customer = {self.customer}"


class OrderItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='order_item')
    quantity = models.IntegerField(default=1, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')

    @property
    def total_item_cost(self):
        return float(self.quantity) * float(self.book.price)

    def __str__(self):
        return f"order_id:{self.id}, book:{self.book.title}, order:{self.order.id}"
