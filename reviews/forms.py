"""This module contains the forms for the reviews app"""

from django import forms
from django.core.exceptions import ValidationError
from PIL import Image
from reviews.models import Book, Review
from reviews.widgets import StarRatingWidget

MAX_UPLOAD_SIZE = 5 * 1024 * 1024

class BookForm(forms.ModelForm):
    """Form for creating a new book"""
    class Meta:
        """Configures what model is used for this form
        and any fields to be included/excluded"""
        model = Book
        # DJango does not accept both fields and exclude to be called at once
        exclude = ['created']

    def __init__(self, *args, **kwargs):
        # allows the form fields to be editable by creating a hook
        # in this case, the class: 'create-form' is the hook
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'create-form'})
            # field.widget.attrs is a dict,
            # 'class' key becomes the HTML attribute

    def clean_image(self):
        """Confirms a clean image is uploaded to a Book"""
        # using .get() and [] retrieve values out of dictionary by key
        # bracket notation fails loudly and crashes the system -- use if we KNOW the value is there
        # .get() returns None if no matches found -- use if we are UNSURE
        # if the value is there / its not the end of the workd if the key is missing
        image = self.cleaned_data.get("image")
        # check if the value saved is an actual image
        # if not, our validations won't work
        if not image:
            return image

        # image is an UploadedFile object
        # depending on size of the object, it can be InMemoryUploadedFile or TemporaryUploadedFile
        # both affect how .seek() and .read() behave
        if image.size > MAX_UPLOAD_SIZE:
            raise ValidationError("Image must be under 5MB")

        valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
        if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
            raise ValidationError("Unsupported file type")

        try:
            # Image.open() comes from Pillow in order to read a file's header/structure
            # verifies whether the object is actually an image
            img = Image.open(image)
            # img.verify() confirms the file isn't corrupted/truncated
            img.verify()
        except Exception as exc:
            raise ValidationError("File is not a valid image") from exc

        # after the image has been checked and verified
        # the file's internal 'read cursor' is at the end and needs to be rewound
        image.seek(0)

        return image

class ReviewForm(forms.ModelForm):
    """Form for creating a new review"""
    rating = forms.ChoiceField(
        choices=[(i, i) for i in range(5, 0, -1)],
        widget=StarRatingWidget,
    )

    class Meta:
        """Configures what model is used for this form
        and any fields to be included/excluded"""
        model = Review
        exclude = ['book', 'user', 'created', 'updated']
