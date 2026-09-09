"""This module contains the views for the LitReview project"""
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.views import generic
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from .forms import UserSignUpForm, UserLoginForm

User = get_user_model()

# A class-based view is a class that defines methods to handle HTTP requests (GET, POST, etc.)
# All class-based views must inherit from the base class `View` provided by Django
class UserLoginView(LoginView):
    """This class handles the login page for the LitReview project"""
    form_class = UserLoginForm
    template_name = 'users/login_page.html'

    def get_success_url(self):
        """This method returns the URL to redirect to after successful login"""
        # return f"/users/{self.request.user.username}/" # hardcoded url is bad practice,
        # reverse() completes a URL lookup at line execution
        # based on the name of the url pattern and the arguments passed to it
        # only works if urls.py is loaded before line execution --
        # which is true for a view method as the urls.py is loaded before the view method is called
        return reverse('user-profile',
                       kwargs={'username': self.request.user.username}) # redirect to user profile

class UserSignUpView(CreateView):
    """This class handles the signup page for the LitReview project"""
    form_class = UserSignUpForm
    template_name = 'users/signup_page.html'
    # reverse_lazy() resolves the URL name only when its needed
    # this function completes a URL lookup at class-defintition time --
    # but defers the actual URL resolution until the view is called
    # using reverse_lazy() is necessary when defining class-based views, --
    # because the URL patterns are not yet loaded when the class is defined
    success_url = reverse_lazy('login-page') # redirect to login page after successful signup

class UserProfileView(generic.DetailView):
    """This class handles the user profile page for the LitReview project"""
    model = User
    template_name = 'users/user_profile.html'

    def get_queryset(self):
        """This method returns the queryset for the user profile page"""
        return User.objects.filter(username=self.kwargs['username'])
