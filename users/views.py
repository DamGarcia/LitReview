"""This module contains the user views for the LitReview project"""
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse
from django.shortcuts import render

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
                       kwargs={'username': self.request.user.username}
                       )  # redirect to user profile

class UserSignUpView(CreateView):
    """This class handles the signup page for the LitReview project"""
    form_class = UserSignUpForm
    template_name = 'users/signup_page.html'

    def form_valid(self, form):
        """This method defines the behavior when a form is valid"""
        form.save()  # save the user object to the database
        return render(self.request, 'users/signup_page.html',
                      {'success': True})
        # render the signup page with a success message

    # def form_invalid(self, form):
    #     """This method defines the behavior when a form is invalid"""
    #     return render(self.request, 'users/signup_page.html',
    #                   {'form': form, 'success': False})
    #     # render the signup page with the form and an error message
    # Unnecessary to override form_invalid() because
    # the default behavior is to re-render the form with errors
    # handled by the template, which is what we want
