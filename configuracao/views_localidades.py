import logging

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from .services_localidades import buscar_cidades_catalogo, serializar_cidade

logger = logging.getLogger('configuracao')


@login_required
@require_GET
def api_buscar_cidades(request):
    """Endpoint global para autocomplete de cidades com suporte a idioma e país."""
    termo = (request.GET.get('q') or '').strip()
    idioma = (request.GET.get('lang') or 'pt-BR').strip()
    pais = (request.GET.get('country') or '').strip().upper() or None

    try:
        limite = int(request.GET.get('limit', '30'))
    except (TypeError, ValueError):
        limite = 30

    if len(termo) < 2:
        return JsonResponse({'results': [], 'meta': {'q': termo, 'lang': idioma, 'country': pais, 'limit': limite}})

    try:
        cidades = buscar_cidades_catalogo(termo=termo, pais_iso2=pais, idioma=idioma, limite=limite)
        resultados = [serializar_cidade(cidade, idioma=idioma) for cidade in cidades]
        return JsonResponse({'results': resultados, 'meta': {'q': termo, 'lang': idioma, 'country': pais, 'limit': limite}})
    except Exception as exc:
        logger.error('Erro ao buscar cidades no catálogo global: %s', exc, exc_info=True)
        return JsonResponse({'results': [], 'error': 'Erro ao buscar cidades no catálogo.'}, status=500)
