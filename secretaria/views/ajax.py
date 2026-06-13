"""
secretaria/views/ajax.py
Views AJAX utilitárias: autocomplete de nomes e outros endpoints JSON menores.
"""
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from secretaria.models import Membro
from secretaria.utils import filter_people_by_name_or_nickname

logger = logging.getLogger(__name__)


@login_required
@require_GET
def autocomplete_nome(request):
    """Autocomplete geral de membros/visitantes pelo nome."""
    q = request.GET.get('q', '').strip()
    results = []
    if q and len(q) >= 1:
        membros = filter_people_by_name_or_nickname(Membro.objects.all(), q).order_by('nome')[:10]
        for m in membros:
            results.append({
                'id': m.pk,
                'nome': m.nome,
                'tipo_pessoa': m.tipo_pessoa.nome if getattr(m, 'tipo_pessoa', None) else '',
            })
    return JsonResponse({'results': results})


@login_required
@require_GET
def autocomplete_nome_membro(request):
    """Autocomplete de membros para uso em filtros de relatório."""
    termo = request.GET.get('q', '').strip()
    results = []
    if termo:
        membros = filter_people_by_name_or_nickname(Membro.objects.all(), termo)[:20]
        results = [{'id': m.id, 'nome': m.nome} for m in membros]
    return JsonResponse({'results': results})
