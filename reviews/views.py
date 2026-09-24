"""This module contains the book reviews view for the LitReview Project"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.urls import reverse
from django.views.generic import DeleteView, DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, redirect
from .models import Book, Review
from .forms import BookForm, ReviewForm

class BookView(DetailView):
    """This view displays individual book details"""
    model = Book
    template_name = 'reviews/book_detail.html'
    context_object_name = 'book'

    def get_object(self, queryset=None):
        """This method returns the individual book for viewing"""
        queryset = self.get_queryset().filter(id=self.kwargs.get('book_id'))
        return get_object_or_404(queryset)

class BookCreate(LoginRequiredMixin, CreateView):
    """This view allows users to add books"""
    form_class = BookForm
    template_name = 'reviews/book_create.html'

    def form_valid(self, form):
        book = form.save()
        return redirect('book-review', book.id)


class ReviewCreate(LoginRequiredMixin, CreateView):
    """This view allows users to post reviews"""
    form_class = ReviewForm
    template_name = 'reviews/review_create.html'

    # the create view needs access to the book
    def get_book(self):
        """Connects the review to a book by pulling from the url"""
        return get_object_or_404(Book, pk=self.kwargs['book_id'])

    def get_context_data(self, **kwargs):
        """Provides the template with the book as context"""
        context = super().get_context_data(**kwargs)
        context['book'] = self.get_book()
        return context

    def form_valid(self, form):
        # connects the book as a FK to the new review
        form.instance.book_id = self.kwargs['book_id']
        # connects the user as a FK to the new review
        form.instance.user = self.request.user
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, "You've already reviewed this book. Update previous review.")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('book-review', args=[self.object.book.id])

class ReviewUpdate(LoginRequiredMixin, UpdateView):
    """This view allows users to update reviews"""
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_update.html'

    def get_queryset(self):
        """This method filters results and restricts
        other methods from 'forgetting' the check"""
        return Review.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        """This method will return the pre-filled form"""
        queryset = self.get_queryset().filter(
            book_id=self.kwargs.get('book_id'))
        return get_object_or_404(queryset)

    def get_success_url(self):
        return reverse('book-review', args=[self.object.book.id])

class ReviewDelete(LoginRequiredMixin, DeleteView):
    """This view will allow users to delete reviews"""
    model = Review
    template_name = 'reviews/review_delete.html'

    def get_object(self, queryset=None):
        queryset = self.get_queryset().filter(id=self.kwargs.get('book_id'))
        return get_object_or_404(queryset)

    def get_success_url(self):
        return reverse('book-review', args=[self.object.user.id])
