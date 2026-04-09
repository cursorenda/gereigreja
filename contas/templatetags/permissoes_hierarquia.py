from django import template
from contas.constants import user_has_permission_level_or_higher, HIERARQUIA_GRUPOS

register = template.Library()

@register.filter
def tem_permissao_hierarquica(user, required_group):
    """
    Uso: {% if user|tem_permissao_hierarquica:'Admin Ministerio' %}
    Retorna True se o usuário tem permissão igual ou superior ao grupo exigido.
    """
    return user_has_permission_level_or_higher(user, required_group)


@register.filter
def get_permission_level(group_name):
    """
    Retorna o nível hierárquico do grupo (1-14).
    Uso: {% with nivel=grupo.name|get_permission_level %}
    """
    return HIERARQUIA_GRUPOS.get(group_name, "N/A")
