from django.contrib import admin
from .models import Review
from books.models import Book


class ReviewInline(admin.TabularInline):
    model = Review


class BookAdmin(admin.ModelAdmin):
    inlines = [ReviewInline, ]
    list_display = ("title", "author", "price",)
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Book, BookAdmin)
