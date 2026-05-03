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


@register.simple_tag(takes_context=True)
def get_churches_tree_ordered(context):
    """
    Retorna lista de igrejas em ordem hierárquica para o seletor global:
      1. Sede / Independente (A-Z)
         └─ Regional (A-Z)
              └─ Congregação (A-Z)
         └─ Congregação direta da sede (A-Z)
      2. Regionais/Congregações órfãs (superior fora do escopo permitido)
    """
    request = context.get('request')
    if not (request and request.user.is_authenticated
            and hasattr(request.user, 'perfil') and request.user.perfil):
        return []
    try:
        churches = list(get_allowed_churches_for_user(request.user))

        sedes       = sorted([c for c in churches if c.tipo_igreja in ('sede', 'independente')], key=lambda x: x.nome_igreja)
        regionais   = sorted([c for c in churches if c.tipo_igreja == 'regional'],               key=lambda x: x.nome_igreja)
        congregacoes= sorted([c for c in churches if c.tipo_igreja == 'congregacao'],            key=lambda x: x.nome_igreja)
        outros      =        [c for c in churches if c.tipo_igreja not in ('sede', 'independente', 'regional', 'congregacao')]

        ordered = []
        placed  = set()

        for sede in sedes:
            ordered.append(sede)
            placed.add(sede.pk)
            # Regionais desta sede
            for regional in [r for r in regionais if r.igreja_superior_id == sede.pk]:
                ordered.append(regional)
                placed.add(regional.pk)
                # Congregações desta regional
                for cong in [c for c in congregacoes if c.igreja_superior_id == regional.pk]:
                    ordered.append(cong)
                    placed.add(cong.pk)
            # Congregações diretas da sede (sem regional intermediária)
            for cong in [c for c in congregacoes if c.igreja_superior_id == sede.pk]:
                ordered.append(cong)
                placed.add(cong.pk)

        # Regionais órfãs (superior fora do escopo)
        for regional in [r for r in regionais if r.pk not in placed]:
            ordered.append(regional)
            placed.add(regional.pk)
            for cong in [c for c in congregacoes if c.igreja_superior_id == regional.pk]:
                ordered.append(cong)
                placed.add(cong.pk)

        # Congregações órfãs restantes
        for cong in [c for c in congregacoes if c.pk not in placed]:
            ordered.append(cong)
            placed.add(cong.pk)

        ordered.extend([c for c in outros if c.pk not in placed])
        return ordered

    except Exception as e:
        logger.error(f"Erro em get_churches_tree_ordered para usuário {request.user.username}: {e}")
        return []
