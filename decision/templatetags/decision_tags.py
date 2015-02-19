from django import template
from django.core.cache import cache

register = template.Library()


@register.filter
def get_user_choice(user, poll):
    return poll.get_user_choice(user)
