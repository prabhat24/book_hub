from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    cover = models.ImageField(upload_to="covers/", blank=True)
    slug = models.SlugField(null=True, unique=True)

    def __str__(self):
        return f"title:{self.title}, author:{self.author}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Book, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'slug': self.slug})
