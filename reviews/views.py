"""This module contains the book reviews view for the LitReview Project"""
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from .models import Book

class BookView(DetailView):
    """This view displays individual book details"""
    model = Book
    template_name = 'reviews/book_view.html'
    context_object_name = 'book'

    def get_object(self, queryset=None):
        """This method returns the individual book for viewing"""
        queryset = self.get_queryset().filter(id=self.kwargs.get('id'))
        return get_object_or_404(queryset)
