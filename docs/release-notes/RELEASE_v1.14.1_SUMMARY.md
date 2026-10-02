# RELEASE v1.14.1 - Hotfix Financeiro do Sistema

Data: 08/07/2026

## Resumo Executivo
A release v1.14.1 corrige uma excecao em producao na tela administrativa de Financeiro do Sistema. O erro ocorria durante a agregacao mensal de receitas/gastos por mes quando o valor retornado por `TruncMonth` ja era do tipo `date`.

## Problema
- URL afetada: `/admin/financeiro-sistema/`
- Erro: `AttributeError: 'datetime.date' object has no attribute 'date'`
- Causa raiz: chamada de `.date()` sobre objeto que, em determinados cenarios, ja era `date` (nao `datetime`).

## Correcao Implementada
- Inclusao de utilitario interno para normalizar buckets mensais retornados pelo ORM.
- Normalizacao robusta para ambos os tipos (`date` e `datetime`) no primeiro dia do mes.
- Substituicao dos pontos de agregacao mensal para uso da normalizacao.

## Arquivo Alterado
- `configuracao/views_financeiro_sistema.py`

## Impacto
- Corrige o erro 500 no painel de Financeiro do Sistema.
- Preserva comportamento funcional da serie mensal de receitas, gastos e liquido.
- Nao altera modelos, migracoes ou schema.

## Validacao
- `python manage.py check` executado com sucesso (0 issues).

## Observacoes Operacionais
- Hotfix seguro e pontual.
- Recomendado monitorar logs do endpoint administrativo apos deploy para confirmar estabilidade.
