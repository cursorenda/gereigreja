from django.db.models import Q

from .models import CidadeCatalogo, normalizar_texto_catalogo


def buscar_cidades_catalogo(termo='', pais_iso2=None, idioma='pt-BR', limite=30):
    """Busca cidades no catálogo global com tolerância a acento e filtro opcional por país."""
    qs = CidadeCatalogo.objects.filter(ativo=True, pais__ativo=True).select_related('pais', 'subdivisao')

    if pais_iso2:
        qs = qs.filter(pais__codigo_iso2=str(pais_iso2).upper().strip())

    termo_normalizado = normalizar_texto_catalogo(termo)
    if termo_normalizado:
        filtros = Q(nome_normalizado__icontains=termo_normalizado)
        filtros |= Q(traducoes__idioma=idioma, traducoes__nome__icontains=termo)
        filtros |= Q(subdivisao__nome_normalizado__icontains=termo_normalizado)
        filtros |= Q(subdivisao__traducoes__idioma=idioma, subdivisao__traducoes__nome__icontains=termo)
        filtros |= Q(pais__nome_normalizado__icontains=termo_normalizado)
        filtros |= Q(pais__traducoes__idioma=idioma, pais__traducoes__nome__icontains=termo)
        qs = qs.filter(filtros)

    return qs.distinct().order_by('nome_normalizado')[: max(1, int(limite))]


def serializar_cidade(cidade, idioma='pt-BR'):
    """Converte cidade em payload de API reutilizável."""
    pais_nome = cidade.pais.nome_exibicao(idioma=idioma)
    subdivisao_nome = cidade.subdivisao.nome_exibicao(idioma=idioma) if cidade.subdivisao else ''
    cidade_nome = cidade.nome_exibicao(idioma=idioma)

    return {
        'id': cidade.id,
        'cidade': cidade_nome,
        'subdivisao': subdivisao_nome,
        'subdivisao_codigo': cidade.subdivisao.codigo if cidade.subdivisao else '',
        'pais': pais_nome,
        'pais_iso2': cidade.pais.codigo_iso2,
        'display': f"{cidade_nome} - {subdivisao_nome}/{cidade.pais.codigo_iso2}" if subdivisao_nome else f"{cidade_nome} - {cidade.pais.codigo_iso2}",
    }
