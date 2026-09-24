"""This module creates custom widgets that handle how some HTML renders"""
from django import forms

class StarRatingWidget(forms.RadioSelect):
    """Reuses RadioSelect's data extraction; only changes the template used to render."""
    template_name = "widgets/star_rating.html"   # 1. custom outer wrapper
    option_template_name = "widgets/star_option.html"  # 2. custom per-star markup

    class Media:
        """Claims the widgets own CSS for styling"""
        # 3. widget owns its own CSS — anywhere it's used, styles come along
        css = {"all": ("css/star_rating.css",)}
