"""This module contains the book reviews view for the LitReview Project"""
from django.views.generic import DetailView, CreateView
from django.shortcuts import get_object_or_404, render
from .models import Book
from .forms import BookForm

class BookView(DetailView):
    """This view displays individual book details"""
    model = Book
    template_name = 'reviews/book_detail.html'
    context_object_name = 'book'

    def get_object(self, queryset=None):
        """This method returns the individual book for viewing"""
        queryset = self.get_queryset().filter(id=self.kwargs.get('id'))
        return get_object_or_404(queryset)

class BookCreate(CreateView):
    """This view allows users to add books"""
    form_class = BookForm
    template_name = 'reviews/book_create.html'

    def form_valid(self, form):
        form.save()
        return render(self.request, 'reviews/book_detail.html')
