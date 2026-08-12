# Financeiro - Fase 3B (Politica de Categorias)

## Objetivo
Padronizar regras de categoria de receita por fundo em um unico ponto reutilizavel, reduzindo risco de divergencia entre dominio, forms e views.

## Escopo implementado
- Novo modulo [financeiro/policies.py](financeiro/policies.py) com:
  - `categorias_receita_permitidas_por_fundo(codigo_fundo)`
  - `categoria_receita_padrao_por_fundo(codigo_fundo)`
  - `categoria_receita_por_evento(evento)`
- Dominio passou a delegar politica de permitidas para esse modulo:
  - [financeiro/models.py](financeiro/models.py)
- Selectors passaram a consumir politica central:
  - [financeiro/selectors.py](financeiro/selectors.py)

## Politica atual consolidada
- LOCAL: permitidas `dizimo`, `oferta`, `voto`, `campanha`, `outro`; default `oferta`.
- EVENTOS: permitidas `doacao`; default `doacao`.
- MISSOES: permitidas `oferta`, `campanha`, `outro`; default `oferta`.
- ASSISTENCIA: permitidas `doacao`, `campanha`, `outro`; default `doacao`.

## Compatibilidade
- Sem mudanca de schema.
- Sem mudanca de rota ou layout.
- Comportamento funcional preservado com regra centralizada.
