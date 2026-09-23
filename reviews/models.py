"""This module contains the models for the reviews app."""
from django.core import validators
from django.db import models
from django.utils.text import Truncator


class Book(models.Model):
    """Model for the book entity"""

    title = models.CharField(
        verbose_name="Title",
        max_length=255,
        db_index=True,
        null=False,
        blank=False,
    )
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    author = models.CharField(
        verbose_name="Author",
        max_length=50,
        blank=True,
        null=True,
        )
    # upload_to= saves images for a Book under MEDIA_ROOT/images
    image = models.ImageField(upload_to='images/', verbose_name="Image", null=True, blank=True)

    def __str__(self):
        return f"{Truncator(self.title).chars(30)}"

    def __repr__(self):
        return f"<Book {self.id}>"


class Review(models.Model):
    """Model for the review entity"""

    headline = models.CharField(max_length=255)
    body = models.TextField(blank=False, null=False)
    rating = models.PositiveSmallIntegerField(
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(5)]
    )
    # related_name= sets the ForeignKey reference to 'reviews'
    book = models.ForeignKey("reviews.Book", on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{Truncator(self.headline).chars(30)} (by {self.user.full_name})"

    def __repr__(self):
        return f"<Review {self.id}>"
