from django.db.models import Q

from .models import HinoGlobal, HinoDaIgreja, HinoTema


def listar_hinos_globais_publicos(colecao=None, busca=None, tema=None):
    """Retorna hinos globais disponíveis para exibição pública."""
    queryset = HinoGlobal.objects.disponiveis_publicacao().prefetch_related('temas')

    if colecao:
        queryset = queryset.filter(colecao=colecao)

    if busca:
        queryset = queryset.filter(
            Q(titulo__icontains=busca)
            | Q(numero__icontains=busca)
            | Q(colecao__icontains=busca)
        )

    if tema:
        queryset = queryset.filter(temas__slug=tema, temas__ativo=True)

    return queryset.distinct().order_by('colecao', 'numero')


def listar_hinos_igreja_publicos(igreja, colecao=None, busca=None, tema=None):
    """Retorna hinos customizados da igreja liberados para uso público."""
    if not igreja:
        return HinoDaIgreja.objects.none()

    queryset = HinoDaIgreja.objects.disponiveis_publicacao().filter(igreja=igreja).prefetch_related('temas')

    if colecao:
        queryset = queryset.filter(colecao=colecao)

    if busca:
        queryset = queryset.filter(
            Q(titulo__icontains=busca)
            | Q(numero__icontains=busca)
            | Q(colecao__icontains=busca)
        )

    if tema:
        queryset = queryset.filter(temas__slug=tema, temas__ativo=True)

    return queryset.distinct().order_by('colecao', 'numero')


def get_hino_global(colecao, numero):
    """Busca um hino global por coleção e número."""
    return HinoGlobal.objects.prefetch_related('temas').filter(colecao=colecao, numero=numero).first()


def get_hino_igreja(igreja, colecao, numero):
    """Busca a versão customizada de uma igreja."""
    if not igreja:
        return None
    return HinoDaIgreja.objects.prefetch_related('temas').filter(
        igreja=igreja,
        colecao=colecao,
        numero=numero,
    ).first()


def listar_colecoes_disponiveis(igreja=None):
    """Lista coleções com ao menos um hino público."""
    colecoes = set(
        HinoGlobal.objects.disponiveis_publicacao().values_list('colecao', flat=True)
    )

    if igreja:
        colecoes.update(
            HinoDaIgreja.objects.disponiveis_publicacao()
            .filter(igreja=igreja)
            .values_list('colecao', flat=True)
        )

    return sorted(colecoes)


def listar_temas_disponiveis(igreja=None):
    """Lista temas ativos que possuem ao menos um hino público no contexto informado."""
    tema_map = {}

    globais = HinoTema.objects.filter(
        ativo=True,
        hinos_globais__in=HinoGlobal.objects.disponiveis_publicacao(),
    ).values('nome', 'slug').distinct()
    for item in globais:
        tema_map[item['slug']] = item['nome']

    if igreja:
        locais = HinoTema.objects.filter(
            ativo=True,
            hinos_igreja__in=HinoDaIgreja.objects.disponiveis_publicacao().filter(igreja=igreja),
        ).values('nome', 'slug').distinct()
        for item in locais:
            tema_map[item['slug']] = item['nome']

    return [
        {'nome': nome, 'slug': slug}
        for slug, nome in sorted(tema_map.items(), key=lambda pair: pair[1].lower())
    ]
