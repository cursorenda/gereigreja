# Release v1.14.25 - 12/08/2026

## Resumo Executivo
Esta release consolida a governanca departamental, amplia a camada de documentacao tecnica, fortalece o fluxo de eventos com prestacao de contas e eleva o financeiro com fundos departamentais e lancamento em lote.

## Entregas Principais
- Documentacao adicionada para frontend, design system e arquitetura financeira por fases.
- Configuracao do ministerio e departamentos ajustada para suportar conta padrao de eventos e melhor visao executiva.
- Gestao de departamentos com cards recolhidos por padrao e acesso contextual ao financeiro.
- Fluxo de eventos atualizado com governanca operacional, conta do evento e prestacao de contas.
- Financeiro fortalecido com politicas centralizadas, selectors, services e command para departamentos financeiros.
- Receitas e despesas com lote operacional:
  - adicionar em lista temporaria;
  - editar item pendente;
  - duplicar item pendente;
  - manter ultimos valores por igreja/tipo;
  - atalho Enter para adicionar.
- Ajuste pontual na secretaria para simplificar a UI de sugestao de naturalidade.

## Arquivos Alterados
- CHANGELOG.md
- docs/frontend/09-HTMX.md
- docs/frontend/10-AlpineJS.md
- docs/frontend/11-Dashboards.md
- docs/design-system/*
- docs/sistema/FINANCEIRO_*.md
- configuracao/*
- eventos/*
- financeiro/*
- secretaria/templates/partials/_form_pessoa_oficial.html

## Validacoes Executadas
- python manage.py check --settings=core.settings
- python manage.py test tests.test_financeiro.ReceitasViewTest tests.test_financeiro.DespesasViewTest --settings=core.settings_test
- git status verificado com working tree limpa apos commits

## Observacoes
- Nenhuma migracao manual pendente apos os commits realizados.
- Branch de release/deploy continua sendo master.
