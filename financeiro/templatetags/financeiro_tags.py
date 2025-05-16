# c:\Gereigreja\financeiro\templatetags\financeiro_tags.py
from django import template
from financeiro.utils import is_finance_leader # Importa a função que já criamos

register = template.Library()

@register.simple_tag(takes_context=False) # takes_context=False se não precisar do contexto do template
def user_is_finance_leader(user):
    """
    Verifica se o usuário logado é um líder financeiro.
    Retorna True se for, False caso contrário.
    """
    if user and user.is_authenticated:
        return is_finance_leader(user)
    return False

