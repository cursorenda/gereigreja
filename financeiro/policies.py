"""Politicas de categoria de receita por contexto/fundo.

Fase 3B: centraliza defaults e permitidas para evitar regra espalhada.
"""

FUNDO_LOCAL = 'LOCAL'
FUNDO_EVENTOS = 'EVENTOS'
FUNDO_MISSOES = 'MISSOES'
FUNDO_ASSISTENCIA = 'ASSISTENCIA'

CATEGORIA_RECEITA_PADRAO = 'oferta'

_CATEGORIAS_PERMITIDAS_POR_FUNDO = {
    FUNDO_LOCAL: {'dizimo', 'oferta', 'voto', 'campanha', 'outro'},
    FUNDO_EVENTOS: {'doacao', 'outro'},
    FUNDO_MISSOES: {'oferta', 'campanha', 'outro'},
    FUNDO_ASSISTENCIA: {'doacao', 'campanha', 'outro'},
}


_CATEGORIA_PADRAO_POR_FUNDO = {
    FUNDO_LOCAL: 'oferta',
    FUNDO_EVENTOS: 'doacao',
    FUNDO_MISSOES: 'oferta',
    FUNDO_ASSISTENCIA: 'doacao',
}


_CATEGORIAS_DESPESA_EVENTOS_PADRAO = (
    'Estrutura de Evento',
    'Alimentacao de Equipe',
    'Transporte de Evento',
    'Hospedagem de Convidados',
    'Divulgacao e Midia',
    'Material de Apoio',
    'Decoracao e Ambientacao',
    'Cache e Ministracao',
    'Taxas e Licencas',
    'Outros Custos do Evento',
)


def categorias_receita_permitidas_por_fundo(codigo_fundo):
    """Retorna categorias de receita permitidas para o codigo do fundo."""
    return _CATEGORIAS_PERMITIDAS_POR_FUNDO.get(
        codigo_fundo,
        _CATEGORIAS_PERMITIDAS_POR_FUNDO[FUNDO_LOCAL],
    )


def categoria_receita_padrao_por_fundo(codigo_fundo):
    """Retorna categoria default de receita para o codigo do fundo."""
    return _CATEGORIA_PADRAO_POR_FUNDO.get(codigo_fundo, CATEGORIA_RECEITA_PADRAO)


def categoria_receita_por_evento(evento):
    """Retorna categoria de receita para contexto com/sem evento."""
    codigo = FUNDO_EVENTOS if getattr(evento, 'pk', None) else FUNDO_LOCAL
    return categoria_receita_padrao_por_fundo(codigo)


def categorias_despesa_padrao_eventos():
    """Retorna nomes de categorias de despesa especificas para contexto de eventos."""
    return _CATEGORIAS_DESPESA_EVENTOS_PADRAO
