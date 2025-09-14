from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={**field.field.widget.attrs, 'class': css_class})

@register.filter(name='has_group')
def has_group(user, group_names):
    """Verifica se o usuário pertence a algum dos grupos informados (separados por vírgula)."""
    if not user.is_authenticated:
        return False
    group_list = [g.strip() for g in group_names.split(',')]
    return user.groups.filter(name__in=group_list).exists()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Permite acessar um item de um dicionário pela chave em templates."""
    try:
        return dictionary[key]
    except (KeyError, IndexError, TypeError):
        return ''
