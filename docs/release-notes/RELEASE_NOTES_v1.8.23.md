# Release Notes – Gereigreja v1.8.23 (Abril/2026)

Olá, comunidade Gereigreja!

Esta versão consolida as melhorias do ciclo v1.8.10 → v1.8.23, com foco em estabilidade de permissões, fluxo de transferências de membros e comunicação entre origem/destino.

## Destaques do ciclo

✅ Hotfixes de escopo em Secretaria (`/secretaria/pessoas/`), incluindo fallback seguro para `request.igrejas_permitidas`.

✅ Base de hierarquia de grupos fortalecida (`HIERARQUIA_GRUPOS` e helpers), com refatoração de decorators e middleware para escopo consistente.

✅ Correção de acesso ao painel financeiro para Pastor Local e níveis superiores, respeitando a hierarquia local.

✅ Implantação do módulo de Transferência de Membros:
- Solicitar
- Listar
- Aprovar
- Recusar (com motivo)
- Cancelar (com motivo)

✅ Notificações e visibilidade operacional para transferência:
- Notificação no sininho para responsáveis da igreja destino
- Badge/alerta no topo com pendências de aprovação
- Item de menu lateral "Transferências" com contador
- Notificações automáticas para origem/destino conforme decisão (aprovação, recusa ou cancelamento)

✅ Correções de UX e robustez no formulário de transferência:
- Preservação de `membro_id` no POST
- Correção de validações com campo membro desabilitado
- Correção de NameError em produção

## Versões publicadas no ciclo

- v1.8.10: Hotfix `AttributeError` em Secretaria
- v1.8.11: Hotfix de lista vazia por escopo
- v1.8.12: Lote 1 (hierarquia base)
- v1.8.13: Lote 2 (docs + testes)
- v1.8.14: Lote 3 (templates/UX)
- v1.8.15: Lote 4 (core/decorators/middleware)
- v1.8.16: Hotfix financeiro para Pastor Local
- v1.8.17: Ajuste de template tags para API central de grupos
- v1.8.18: Módulo inicial de transferências
- v1.8.19: Visibilidade do botão Transferir + gate por hierarquia
- v1.8.20: Hotfix NameError (`SECRETARIO_LOCAL`)
- v1.8.21: Hotfix do formulário de transferência
- v1.8.22: Notificações + badge de pendências
- v1.8.23: Recusar/Cancelar com motivo e notificações cruzadas

Agradecemos os feedbacks rápidos durante os testes em produção, que permitiram um ciclo de melhoria contínua com entrega segura em lotes.

Equipe Gereigreja
