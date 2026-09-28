"""This module contains the book reviews view for the LitReview Project"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, CreateView, ListView, UpdateView
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


class UserOwnedReviewMixin(LoginRequiredMixin):
    """Custom mixin for views that mutate or 
    access reviews owned by the logged-in user"""

    success_url = None # can be overriden on the view class

    def get_queryset(self):
        """Filters view's base queryset"""
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get_success_url(self):
        """Returns explicitly defined success_url,
        or fallback to a default named URL"""
        if self.success_url:
            return str(self.success_url)

        if hasattr(self.object, 'get_absolute_url'):
            return self.object.get_absolute_url()

        # need to wrap in str() because the classes using this custom mixin
        # expect to return a type str(), not a _StrPromise --> reverse_lazy()
        return str(reverse_lazy('login-page'))

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

class ReviewUpdate(UserOwnedReviewMixin, UpdateView):
    """This view allows users to update reviews"""
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_update.html'

    def get_object(self, queryset=None):
        """This method will return the pre-filled form"""
        queryset = self.get_queryset().filter(
            book_id=self.kwargs.get('book_id'))
        return get_object_or_404(queryset)

class ReviewDelete(UserOwnedReviewMixin, DeleteView):
    """This view will allow users to delete reviews"""
    model = Review
    template_name = 'reviews/review_delete.html'
    success_url = reverse_lazy('login-page')

    def get_object(self, queryset=None):
        queryset = self.get_queryset().filter(
            book_id=self.kwargs.get('book_id'))
        return get_object_or_404(queryset)


class HomepageView(ListView):
    """This view will display a list of reviews"""
    model = Review
    template_name = 'reviews/home_page.html'
    # ordering = ['-created']
    # paginate_by = 3
    context_object_name = 'reviews'

    def show_all(self):
        """This function displays all relevant views in user.following"""
        return self.request.GET.get('view') == 'all'

    def get_paginate_by(self, queryset):
        """This function is called by ListView per request"""
        # replaces paginate_by, so the page size can change per request
        return 12 if self.show_all() else 4

    def get_queryset(self):
        """This function filters results shown in the ListView"""
        if not self.request.user.is_authenticated:
            return (
                Review.objects
                .select_related('user', 'book') # selected_related(col1, col2)
                .order_by('-created', '-id')
            )

        following_reviews = (
            Review.objects
            .filter(user__in=self.request.user.following.all())
            .select_related('user', 'book')
            .order_by('-created', '-id') # '-id' breaks any ties for reviews with the same timestamp
        )

        if self.show_all():
            return following_reviews # archive mode

    # highlight mode: newest --> oldest, keep FIRST review seen per book
        seen_books = set() # a set remembers books we've kept
        keep_ids = []
        for review in following_reviews:
            if review.book_id not in seen_books:
                seen_books.add(review.book_id)
                keep_ids.append(review.id)

        return following_reviews.filter(id__in=keep_ids)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_all'] = self.show_all() # allows the template to react between modes
        return context

# original idea to filter the results of homepage -- without ability to see all recent reviews
    # def get_queryset(self):
    #     """The function filters the results shown"""
    #     user = self.request.user

    #     # feed reviews should be filtered by the logged-in users following list
    #     # 'following' is a Model2Model on User, 
    #     following_reviews = Review.objects.filter(author__in=user.following.all())

# SQL:
# SELECT * FROM review
# WHERE author_id IN (
    # SELECT to_user_id FROM user_following
    # WHERE from_user_id = <you>
# )

        # for every review in users.following.all()
        # filter by the newest review to display
        # per book
        # latest_per_book = (
        #     following_reviews.values('book')
        #     .annotate(latest=Max('created'))
        # )

# SQL:
# SLECT book_id, MAX(created) AS latest
# FROM review
# WHERE author_id IN (...)
# GROUP BY book_id

        # create a filtered lookup: {book_id: latest_created_datetime}
        # latest_map = {row['book']: row['latest'] for row in latest_per_book}

        # display only the reviews that matchup the lookup
        # ids = [
        #     review.id for review in following_reviews
        #     if review.created == latest_map.get(review.book_id)
        # ]

        # return (
        #     Review.objects
        #     .filter(id__in=ids)
        #     .select_related('author', 'book')
        #     .order_by('-created')
        # )
