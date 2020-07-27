from django.contrib import admin
from .models import Review
from books.models import Book, Order, OrderItem, ShippingDetail


class ReviewInline(admin.TabularInline):
    model = Review


class BookAdmin(admin.ModelAdmin):
    inlines = [ReviewInline, ]
    list_display = ("title", "author", "price",)


admin.site.register(Book, BookAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingDetail)