from django import forms
from .models import Review

class SearchBooksForm(forms.Form):
    search_field = forms.CharField(widget=forms.Textarea(), help_text="search book title")

class ReviewCreationForm(forms.ModelForm):
    review = forms.CharField(widget=forms.Textarea(), help_text="add your review here")
    reviewer = None
    book = None
    class Meta:
        model = Review
        fields = ('review',)
