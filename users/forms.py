"""This module contains the forms for the LitReview project"""

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import User

class UserLoginForm(AuthenticationForm):
    """This class defines the form for user login"""
    username = forms.CharField(
        max_length=150, required=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    password = forms.CharField(
        widget=forms.PasswordInput, required=True,
        help_text='Required. At least 8 characters.')

class UserSignUpForm(UserCreationForm):
    """This class defines the form for user signup"""
    class Meta(UserCreationForm.Meta):
        """This class defines the meta information for the UserSignUpForm"""
        model = User
        Userfields = UserCreationForm.Meta.fields + (
            'username' , 'password1', 'password2', 
            'first_name' , 'last_name', 'email', 
            'following', 'followers', 'reviews'
            )
        is_active = True
