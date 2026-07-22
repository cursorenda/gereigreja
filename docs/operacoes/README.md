# Operações

Esta pasta documenta a operação do SaaS.

Finalidade da pasta:

- orientar execução operacional em produção;
- consolidar runbooks e checklists de rotina;
- registrar procedimentos de mitigação e continuidade.

Inclui:

- GOC
- Logs
- Observabilidade
- Alertas
- Filas
- Monitoramento
- Operação diária

## Como criar um novo documento de Operações

1. Defina o escopo operacional (runbook, checklist, plano, rotação, incidente).
2. Nomeie no padrão `MODULO_TEMA_TIPO.md` quando for específico de módulo.
3. Para conteúdo transversal, use `TEMA_TIPO.md` sem prefixo de módulo.
4. Documente pré-condições, execução, validação e rollback.
5. Atualize este README e o `docs/INDEX.md`.

## Padrão de Nomenclatura

- Módulo específico: `COMUNICACAO_TEMA_TIPO.md`
- Transversal: `TEMA_TIPO.md`
- Exemplos: `COMUNICACAO_WAHA_RUNBOOK.md`, `COMUNICACAO_DEPLOY_CHECKLIST.md`

## Índice

- [COMUNICACAO_WAHA_RUNBOOK.md](COMUNICACAO_WAHA_RUNBOOK.md)
- [COMUNICACAO_DEPLOY_CHECKLIST.md](COMUNICACAO_DEPLOY_CHECKLIST.md)
- [PLANO_AUTOMACOES_COMUNICACAO.md](PLANO_AUTOMACOES_COMUNICACAO.md)
- [ROTACAO_API_KEY_WAHA.md](ROTACAO_API_KEY_WAHA.md)


