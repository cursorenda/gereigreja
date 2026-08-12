# Financeiro - Fase 3C (Fluxo em Services)

## Objetivo
Enxugar as views de receita, movendo preparacao de payload e contexto para service dedicado, sem mudar regra de negocio.

## Escopo implementado
- Novo service de fluxo em [financeiro/services.py](financeiro/services.py): `ReceitaFluxoService`.
- Views migradas para usar o service:
  - [financeiro/views.py](financeiro/views.py) em `cadastrar_receita_evento`.
  - [financeiro/views.py](financeiro/views.py) em `cadastrar_receita_caixa_eventos`.

## Metodos introduzidos
- `construir_post_data_receita_evento`
- `construir_initial_receita_evento`
- `construir_contexto_receita_evento`
- `resolver_igreja_padrao_receita_caixa_eventos`
- `construir_post_data_receita_caixa_eventos`
- `aplicar_defaults_receita_fluxo_evento`
- `construir_initial_receita_caixa_eventos`

## Beneficios
- Menos logica procedural dentro de view.
- Menor duplicacao entre fluxos de evento e caixa de eventos.
- Melhor base para evolucao de fluxo/politica sem tocar controllers.

## Compatibilidade
- Sem alteracao de schema.
- Sem alteracao de URLs.
- Sem alteracao visual em templates.
- Regras de categoria/conta por evento preservadas.
