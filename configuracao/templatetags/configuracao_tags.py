# c:\Gereigreja\configuracao\templatetags\configuracao_tags.py
from django import template

register = template.Library()

@register.filter
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


# Filtro para somar dias a uma data
from datetime import timedelta

@register.filter
def add_timedelta_days(value, days):
    """Adiciona N dias a um objeto datetime/date."""
    try:
        return value + timedelta(days=int(days))
    except Exception:
        return value
