from django import template
from contas.constants import ADMIN_MINISTERIO

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    from contas.constants import user_tem_grupo
    return user_tem_grupo(user, group_name)


@register.simple_tag
def user_is_admin_ministerio(user):
    """Verifica se o usuário é Admin Ministerio"""
    if not user.is_authenticated:
        return False
    from contas.constants import user_tem_grupo
    return user.is_superuser or user_tem_grupo(user, ADMIN_MINISTERIO)
