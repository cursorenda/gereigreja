from django.core.paginator import Paginator

from core.utils import get_ministerio_or_error
from secretaria.utils import get_allowed_churches_for_membros

from .selectors import (
    listar_hinos_globais_publicos,
    listar_hinos_igreja_publicos,
    get_hino_global,
    get_hino_igreja,
    listar_colecoes_disponiveis,
    listar_temas_disponiveis,
)


def resolver_igreja_contexto(request, ministerio=None):
    """Resolve a igreja ativa permitida para o membro."""
    if ministerio is None:
        ministerio = get_ministerio_or_error(request)

    igrejas_permitidas = get_allowed_churches_for_membros(request.user, ministerio)
    igreja_contexto = None

    if getattr(request, 'igreja_ativa', None) and igrejas_permitidas.filter(pk=request.igreja_ativa.pk).exists():
        igreja_contexto = request.igreja_ativa
    elif getattr(request.user, 'membro_secretaria', None) and getattr(request.user.membro_secretaria, 'igreja_id', None):
        igreja_usuario = request.user.membro_secretaria.igreja
        if igrejas_permitidas.filter(pk=igreja_usuario.pk).exists():
            igreja_contexto = igreja_usuario
    elif igrejas_permitidas.exists():
        igreja_contexto = igrejas_permitidas.first()

    return ministerio, igreja_contexto, igrejas_permitidas


def _hino_esta_liberado(hino):
    return bool(hino and hino.can_render_public_text())


def montar_hino_publico(hino_global, hino_igreja=None):
    """Monta um payload seguro para exibição no portal."""
    if hino_igreja and (hino_global is None or getattr(hino_igreja, 'override_global', False)):
        origem = hino_igreja
    else:
        origem = hino_global or hino_igreja

    if origem is None:
        return None

    liberado = _hino_esta_liberado(origem)
    temas = [
        {'nome': tema.nome, 'slug': tema.slug}
        for tema in sorted(
            [tema for tema in origem.temas.all() if tema.ativo],
            key=lambda item: item.nome.lower(),
        )
    ]
    return {
        'id': origem.id,
        'colecao': origem.colecao,
        'numero': origem.numero,
        'titulo': origem.titulo,
        'origem_tipo': 'igreja' if origem.__class__.__name__ == 'HinoDaIgreja' else 'global',
        'igreja_nome': getattr(getattr(origem, 'igreja', None), 'nome', None),
        'license_status': origem.license_status,
        'license_status_display': origem.get_license_status_display(),
        'blocked_for_public_use': origem.blocked_for_public_use,
        'can_render_public_text': liberado,
        'letra': origem.letra if liberado else None,
        'cifra': origem.cifra if liberado else None,
        'rights_holder': getattr(origem, 'rights_holder', None),
        'license_reference': getattr(origem, 'license_reference', None),
        'legal_notes': getattr(origem, 'legal_notes', None),
        'reviewed_at': getattr(origem, 'reviewed_at', None),
        'reviewed_by': getattr(getattr(origem, 'reviewed_by', None), 'get_full_name', lambda: None)(),
        'source_origin': getattr(origem, 'source_origin', None),
        'is_license_expired': origem.is_license_expired() if hasattr(origem, 'is_license_expired') else False,
        'temas': temas,
    }


def listar_hinos_para_portal(igreja=None, colecao=None, busca=None, ordem='numero_asc', tema=None):
    """Retorna lista mesclada de hinos públicos para o portal do membro."""
    globais = list(listar_hinos_globais_publicos(colecao=colecao, busca=busca, tema=tema))
    personalizados = list(listar_hinos_igreja_publicos(igreja, colecao=colecao, busca=busca, tema=tema)) if igreja else []

    personalizados_map = {
        (hino.colecao, hino.numero): hino
        for hino in personalizados
    }

    resultados = []
    for hino_global in globais:
        override = personalizados_map.get((hino_global.colecao, hino_global.numero))
        payload = montar_hino_publico(hino_global, override)
        if payload:
            resultados.append(payload)

    globais_chaves = {(hino.colecao, hino.numero) for hino in globais}
    for hino_igreja in personalizados:
        chave = (hino_igreja.colecao, hino_igreja.numero)
        if chave in globais_chaves:
            continue
        payload = montar_hino_publico(None, hino_igreja)
        if payload:
            resultados.append(payload)

    if ordem == 'titulo_asc':
        resultados.sort(key=lambda item: (item['titulo'].lower(), item['colecao'], item['numero']))
    elif ordem == 'titulo_desc':
        resultados.sort(key=lambda item: (item['titulo'].lower(), item['colecao'], item['numero']), reverse=True)
    elif ordem == 'numero_desc':
        resultados.sort(key=lambda item: (item['colecao'], item['numero']), reverse=True)
    else:
        resultados.sort(key=lambda item: (item['colecao'], item['numero']))

    return resultados


def obter_hino_para_exibicao(igreja, colecao, numero):
    """Retorna a versão segura a ser exibida para um hino específico."""
    hino_global = get_hino_global(colecao, numero)
    hino_igreja = get_hino_igreja(igreja, colecao, numero)

    if hino_igreja and (not hino_global or getattr(hino_igreja, 'override_global', False)):
        return montar_hino_publico(hino_global, hino_igreja)

    if hino_global:
        return montar_hino_publico(hino_global, hino_igreja)

    if hino_igreja:
        return montar_hino_publico(None, hino_igreja)

    return None


def paginar_hinos(hinos, page_number, per_page=12):
    """Aplica paginação sobre uma lista de hinos já mesclada."""
    paginator = Paginator(hinos, per_page)
    return paginator.get_page(page_number)


def listar_resumo_portal(igreja=None):
    """Retorna os resumos usados pela tela inicial do hinário."""
    return {
        'colecoes': listar_colecoes_disponiveis(igreja),
        'temas': listar_temas_disponiveis(igreja),
        'total_globais': listar_hinos_globais_publicos().count(),
        'total_igreja': listar_hinos_igreja_publicos(igreja).count() if igreja else 0,
    }
