# Especificação: Hinário Seguro com Compliance de Direitos Autorais

## Visão Geral

O módulo `hinario` implementa um catálogo de hinos (Harpa Cristã, Corinhos, Cantor Cristão) com:
- Compliance jurídico obrigatório (bloqueio por padrão)
- Auditoria completa de alterações
- Isolamento multi-tenant por Igreja
- Serviço de merge global + customização por Igreja

## Arquitetura

### Componentes

1. **Models (hinario/models.py)**
   - `HinoGlobal`: catálogo base compartilhado
   - `HinoDaIgreja`: override/customização por Igreja
   - `HinoAuditLog`: trilha de auditoria de compliance

2. **Managers (hinario/managers.py)**
   - Soft delete com `alive()`, `deleted()`, `soft_delete()`, `restore()`
   - Helpers de negócio: `ativos()`, `disponiveis_publicacao()`

3. **Signals (hinario/signals.py)**
   - Auditoria automática de mudanças de compliance
   - Rastreamento de quem fez o quê e quando

4. **Camadas GEA (a entregar na Fase 2)**
   - Selectors: leitura otimizada do banco
   - Services: merge global + Igreja + validação de compliance
   - Forms/Views/URLs: interface segura

## Compliance por Padrão

### Status de Licença

```
public_domain     → Domínio público comprovado
licensed          → Licença documentada e válida
restricted        → Acesso restrito/uso limitado
unknown           → Origem desconhecida (BLOQUEADO)
pending_review    → Aguardando revisão (BLOQUEADO)
```

### Bloqueio Automático

Hino é bloqueado para exibição quando:
1. `blocked_for_public_use = True` (default na importação)
2. `license_status` em `['unknown', 'pending_review', 'restricted']`
3. `license_expires_at` vencido

### Desbloqueio Seguro

Requer:
- `reviewed_by` preenchido
- `reviewed_at` preenchido
- `license_status` em `['public_domain', 'licensed']`
- `license_expires_at` não vencido (ou null)

## Multi-Tenant Seguro

- `HinoDaIgreja` vinculado a Igreja específica
- Queries sempre filtram por Igreja logada
- Isolamento validado em testes (Igreja A não vê dados de B)

## Auditoria

Registra em `HinoAuditLog`:
- Criação/edição/deleção de hinos
- Mudanças em `blocked_for_public_use`
- Mudanças em `license_status`
- Revisões (quem revisou e quando)
- Importações em lote

## Próximas Fases

- **Fase 2:** Selectors, Services, Forms, Views, URLs
- **Fase 3:** Integração no Portal (Recursos Devocionais)
- **Fase 4:** Importador JSON (management command)
- **Fase 5-6:** Testes, release, deploy

---

**Status:** Fase 1 - Fundação de Domínio e Banco ✅
**Próximo:** Fase 2 - Camadas GEA
