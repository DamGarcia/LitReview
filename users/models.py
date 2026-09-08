"""This module contains the model objects for the LitReview project"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user class that has the "following" field"""

    # We reuse the fields definitions from the parent class, but change `blank` to False
    # We want to make sure first and last names are always provided
    first_name = models.CharField(_("first name"), max_length=150, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=False)

    # This is our custom field
    following = models.ManyToManyField("self", related_name="user_following", symmetrical=False)
    followers = models.ManyToManyField("self", related_name="user_followers", symmetrical=False)
    reviews = models.ManyToManyField("self", related_name="user_reviews", symmetrical=False)
    username = models.CharField(_("username"), max_length=150, unique=True)
    password = models.CharField(_("password"), max_length=128)
    email = models.EmailField(_("email address"), unique=True)

    @property
    def full_name(self):
        """Returns the full name of the user"""
        return f"{self.first_name} {self.last_name}"
