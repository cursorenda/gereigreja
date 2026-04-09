from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    if hasattr(field, 'as_widget'):
        attrs = getattr(field.field.widget, 'attrs', {})
        return field.as_widget(attrs={**attrs, 'class': css_class})
    return field  # Retorna o campo sem alteração se não for um campo de formulário

@register.filter(name='has_group')
def has_group(user, group_names):
    """Verifica se o usuário pertence a algum dos grupos informados (separados por vírgula)."""
    if not user.is_authenticated:
        return False
    group_list = [g.strip() for g in group_names.split(',')]
    from contas.constants import user_tem_qualquer_grupo
    return user_tem_qualquer_grupo(user, group_list)

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Permite acessar um item de um dicionário pela chave em templates."""
    try:
        return dictionary[key]
    except (KeyError, IndexError, TypeError):
        return ''
