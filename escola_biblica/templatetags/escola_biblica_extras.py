

from django import template
from django.utils.safestring import SafeString

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    if isinstance(field, SafeString):
        return field
    return field.as_widget(attrs={**field.field.widget.attrs, 'class': css_class})

# Novo filtro: add_attrs
@register.filter(name='add_attrs')
def add_attrs(field, arg):
    """
    Adiciona múltiplos atributos ao widget do campo do formulário.
    Uso: {{ field|add_attrs:'class=form-control,autofocus=autofocus,placeholder=Nome da classe' }}
    """
    from django.forms.boundfield import BoundField
    if not hasattr(field, 'as_widget'):
        return field
    attrs = {}
    for pair in arg.split(','):
        if '=' in pair:
            k, v = pair.split('=', 1)
            attrs[k.strip()] = v.strip()
    return field.as_widget(attrs={**getattr(field.field.widget, 'attrs', {}), **attrs})
