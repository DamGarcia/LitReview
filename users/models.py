"""This module contains the model objects for the LitReview project"""
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """This class defines the user model for the LitReview project"""

    # We reuse the fields definitions from the parent class, but change `blank` to False
    # We want to make sure first and last names are always provided
    first_name = models.CharField(_("first name"), max_length=150, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=False)

    # This is our custom fields
    following = models.ManyToManyField("self", related_name="followers", symmetrical=False, blank=True)
    email = models.EmailField(_("email address"), unique=True, blank=False,
                              error_messages={
                                  "unique": _("A user with that email already exists.")
                                  }
                              )

    @property
    def full_name(self):
        """Returns the full name of the user"""
        return f"{self.first_name} {self.last_name}"
