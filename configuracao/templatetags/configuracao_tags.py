# c:\Gereigreja\configuracao\templatetags\configuracao_tags.py
from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def add_timedelta_days(value, days):
    if value:
        try:
            # Tenta converter 'days' para int, caso venha como string do template
            num_days = int(days)
            return value + timedelta(days=num_days)
        except (ValueError, TypeError):
            # Se a conversão falhar, retorna o valor original ou None
            return value # ou None, dependendo do comportamento desejado
    return None
