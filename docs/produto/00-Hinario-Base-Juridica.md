# FASE 0: DECLARAÇÃO DE BASE JURÍDICA E POLÍTICA DE CONFORMIDADE

## Objetivo

Este documento formaliza a decisão operacional de importar e publicar conteúdo de hinos no GereIgreja, com especial atenção aos direitos autorais e conformidade jurídica.

## Responsabilidade Legal

**A estrutura técnica do GereIgreja oferece ferramentas de compliance (bloqueio, auditoria, revisão).

**Responsabilidade operacional/legal:** O operador da plataforma (Equipe Legal/Admin do GereIgreja) pelo uso autorizado de conteúdo.

## Base Jurídica Inicial

### Harpa Cristã (640 hinos)

- **Origem:** Repositório DanielLiberato/Harpa-Crista-JSON-640-Hinos-Completa (GitHub)
- **Fonte Original:** Domínio público histórico (hinos da coleção Harpa Cristã - edições clássicas)
- **Status Padrão no Sistema:** `pending_review` + `blocked_for_public_use=True`
- **Avaliação Jurídica Necessária:** Antes do desbloqueio, validar se cada hino é:
  - Domínio público comprovado
  - Licenciado (com documentação)
  - Ou necessita remoção

## Política de Conformidade

### Default Seguro

Todo conteúdo importado inicia com:
- `license_status = "pending_review"`
- `blocked_for_public_use = True`
- `reviewed_by = None`
- `reviewed_at = None`

Isso garante que nenhum hino é exibido publicamente sem revisão explícita.

### Fluxo de Desbloqueio

1. **Revisão Jurídica:** Equipe verifica proveniência e direitos autorais.
2. **Documentação:** Preenche `license_status`, `rights_holder`, `license_reference`.
3. **Aprovação:** Admin marca `reviewed_by`, `reviewed_at`, `blocked_for_public_use=False`.
4. **Auditoria:** Todas as mudanças são registradas em `HinoAuditLog`.

### Controle de Licença Expirada

Qualquer hino com `license_expires_at` vencida é automaticamente bloqueado em leitura, sem intervenção manual.

## Evolução Futura

- **Corinhos:** Reusar mesma estrutura de compliance.
- **Cantor Cristão:** Adicionar como coleção com revisão separada.
- **Governança:** Definir papéis de revisor editorial/jurídico.

## Aprovação

Esta política é ativa imediatamente e deve ser revisada trimestralmente.

**Última atualização:** 09/07/2026

---

**Nota:** Este documento não é parecer jurídico. Serve como guideline operacional interno de conformidade técnica.
