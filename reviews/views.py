"""This module contains the book reviews view for the LitReview Project"""
from urllib.parse import urlencode
from django.views.generic import DeleteView, DetailView, CreateView, ListView, UpdateView
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import InvalidPage
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Avg
from django.db import IntegrityError
from django.views import View
from .forms import BookForm, ReviewForm
from .models import Book, Review

User = get_user_model()

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
    model = Book
    form_class = BookForm
    template_name = 'reviews/book_create.html'
    login_url = 'login-page' # explicit redirect in view but also set in settings.LOGIN_URL
    redirect_field_name = 'next' # preserves ?next= auto directs user here after login

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

class SearchRedirectView(View):
    """This view will act as the entry point for the sitewide search bar"""
    # mpas the <select> value to the URL name of the intended search view
    SEARCH_DESTINATIONS = {
        'book': 'book-search',
        'user': 'user-search',
    }

    def get(self, request, *args, **kwargs):
        """This function identifies the search time and search type
        to redirect the user search"""
        search_term = request.GET.get('search', '').strip()
        search_type = request.GET.get('type', 'book')

        destination_name = self.SEARCH_DESTINATIONS.get(search_type, 'book-search')

        destination_url = reverse(destination_name)
        query_params = urlencode({'search': search_term})
        return HttpResponseRedirect(f"{destination_url}?{query_params}")

# Helper Method
# Retrieves URL query string to perform a search
class QueryStringSearchMixin:
    """Filters a ListView by the ?search= value in the URL"""
    #  custom Mixins must appear BEFORE ListView in the class bases
    # so its get_queryset() runs first
    searchable_fields: list[str] = [] # list of model fields to match against, set per view
    query_string_key = 'search' # URL: /books/search/?search=dune

    def paginate_queryset(self, queryset, page_size):
        """Redirects to page 1 of a bare 404
        when a page no longer exists within
        the current result count"""
        paginator = self.get_paginator(
            queryset, page_size, 
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        requested_page = self.kwargs.get(self.page_kwarg) or self.request.GET.get(self.page_kwarg) or 1

        try:
            page = paginator.page(requested_page)
        except InvalidPage:
            # sets a user-facing recovery vs dead-end 404
            page = paginator.page(1)
        return (paginator, page, page.object_list, page.has_other_pages())

    def get_query_string(self):
        """Identifies the user's search term from the URL string"""
        search_term = self.request.GET.get(self.query_string_key, "")
        return search_term.strip()

    def _validate_searchable_fields(self, model, field_paths):
        """Confirms searchable fields exist for search against a model"""
        for path in field_paths:
            try:
                model._meta.get_field(path.split('__')[0])
            except FieldDoesNotExist as exc:
                raise ImproperlyConfigured(f"Invalid searchable field: {path}") from exc

    def get_queryset(self):
        """Searches the results of the query"""
        all_rows = super().get_queryset() # ListView applies model + ordering here
        search_term = self.get_query_string()

        if not search_term:
            return all_rows.none() # no search term --> empty result set, not the whole table

        field_matches = Q() # an empty Q() matches nothing until we OR into it
        for field_name in self.searchable_fields:
            field_contains_term = Q(**{f"{field_name}__icontains": search_term})
            field_matches |= field_contains_term # row results qualify if ANY field matches

        return all_rows.filter(field_matches)

    def get_context_data(self, **kwargs):
        """Returns context object data to pass in the template"""
        context = super().get_context_data(**kwargs)
        context["search_term"] = self.get_query_string()
        # template will refill the search box with this
        return context

class BookSearchView(QueryStringSearchMixin, ListView):
    """This view performs a book search"""
    model = Book
    searchable_fields = ['title', 'author']
    ordering = ['title']
    paginate_by = 10
    template_name = 'reviews/book_search.html'
    context_object_name = 'books'

    def get_queryset(self):
        """This function will retrieve additional data from the resulting book query"""
        # annotate computes summaries for individual items in a result list
        # computes count + average per book on page, not per row
        # makes review_count + avg_score temp data columns to pull in the template
        return super().get_queryset().annotate(
            review_count=Count('reviews', distinct=True),
            avg_score=Avg('reviews__rating', default=0)
        )

class UserSearchView(LoginRequiredMixin, QueryStringSearchMixin, ListView): # login check runs first
    """This view performs a user search"""
    model = User
    searchable_fields = ['username', 'first_name', 'last_name']
    ordering = ['username']
    paginate_by = 15
    template_name = 'users/user_search.html'
    context_object_name = 'users'

    def get_queryset(self):
        matching_users = super().get_queryset() # search filtering from the mixin
        return matching_users.filter(is_active=True) # hides deactivated accounts


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
