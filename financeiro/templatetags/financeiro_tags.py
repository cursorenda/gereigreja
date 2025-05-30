# c:\Gereigreja\financeiro\templatetags\financeiro_tags.py
from django import template
from financeiro.utils import is_finance_leader, get_allowed_churches_for_user # Importa as funções que já criamos
from configuracao.models import Igreja # Para o caso de retorno vazio na nova tag
import logging

logger = logging.getLogger(__name__)

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

@register.simple_tag(takes_context=True)
def get_allowed_churches_for_user_tag(context):
    """
    Obtém as igrejas permitidas para o usuário logado.
    Usa o contexto para acessar o request.user.
    """
    request = context.get('request')
    if request and request.user.is_authenticated and hasattr(request.user, 'perfil') and request.user.perfil:
        try:
            return get_allowed_churches_for_user(request.user)
        except Exception as e:
            logger.error(f"Erro no template tag get_allowed_churches_for_user_tag para usuário {request.user.username}: {e}")
            return Igreja.objects.none() # Retorna um queryset vazio em caso de erro
    return Igreja.objects.none()
