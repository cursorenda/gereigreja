from django import template
from secretaria.utils import is_secretaria_leader

register = template.Library()

@register.simple_tag
def user_is_secretaria_leader_tag(user):
    if user and user.is_authenticated:
        return is_secretaria_leader(user)
    return False
