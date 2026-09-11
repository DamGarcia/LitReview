"""This module contains the forms for the LitReview project"""
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()
# this function automatically finds the user model that is currently active in the project
# this is defined in the settings.py file as AUTH_USER_MODEL

class UserLoginForm(AuthenticationForm):
    """This class defines the form for user login"""

class UserSignUpForm(UserCreationForm):
    """This class defines the form for user signup"""
    class Meta(UserCreationForm.Meta):
        """This class defines the meta information for the UserSignUpForm"""
        model = User
        fields = ('username', 'password1', 'password2')
