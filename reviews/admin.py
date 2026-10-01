"""This file contains the admin configuration for the reviews app."""
from django.contrib import admin

from .models import Book, Review

admin.site.register(Book)
admin.site.register(Review)
