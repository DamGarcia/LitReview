"""This module creates a reusable tag for building URLs that preserve the current
request's query params -- used for pagination, sorting, and filter links across templates"""
from django import template

register = template.Library()

# used to replace hard-coding URL strings
@register.simple_tag(takes_context=True)
def querystring_replace(context, **kwargs):
    """This function will merge kwargs into current request's GET params
    and returns encoded querystring"""
    request = context.get('request')
    if request is None:
        return ''

    query_dict = request.GET.copy() # request.GET is immutable, .copy() unlocks it
    # used to save everything within a query
    for key, value in kwargs.items():
        if value is None:
            query_dict.pop(key, None) # removes 'None' from an empty querystring
        else:
            query_dict[key] = value
    return query_dict.urlencode() # replaces manual URL string-building
# the use of urlencode allows handling of &, #, spaces, and unicode correctly
# no manual escaping necessary
