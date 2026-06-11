# c:\Gereigreja\configuracao\templatetags\configuracao_tags.py
from django import template
from decimal import Decimal, InvalidOperation

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


@register.filter
def stripe_centavos_para_reais(value):
    """Converte inteiros em centavos retornados pela Stripe para valor em reais."""
    try:
        if value is None:
            return Decimal('0.00')
        return (Decimal(str(value)) / Decimal('100')).quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal('0.00')
