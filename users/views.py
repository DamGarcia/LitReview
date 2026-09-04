"""This module contains the views for the LitReview project"""
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import User
from .forms import UserSignUpForm

# A class-based view is a class that defines methods to handle HTTP requests (GET, POST, etc.)
# All class-based views must inherit from the base class `View` provided by Django

class UserLoginView(LoginView):
    """This class handles the login page for the LitReview project"""

    def get_success_url(self):
        """Returns the URL to redirect to after a successful login"""
        # returns a string representing the URL to redirect to after a successful login
        return f"/users/{self.request.user.username}/" # redirect to user profile

class UserSignUpView(CreateView):
    """This class handles the signup page for the LitReview project"""
    form_class = UserSignUpForm
    template_name = 'users/signup_page.html'
    success_url = reverse_lazy('login-page') # redirect to login page after successful signup
