from django import template
from contas.constants import ADMIN_MINISTERIO

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.simple_tag
def user_is_admin_ministerio(user):
    """Verifica se o usuário é Admin Ministerio"""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name=ADMIN_MINISTERIO).exists()
