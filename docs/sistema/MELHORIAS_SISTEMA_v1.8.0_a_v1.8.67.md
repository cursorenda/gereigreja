# Melhorias do Sistema - Ciclo v1.8.0 a v1.8.67

**Data de criação:** 12/04/2026  
**Período coberto:** de v1.8.0 até v1.8.67  
**Público-alvo:** time técnico (desenvolvimento, suporte, operação e auditoria)

---

## 1. Escopo e fonte da análise

Este documento consolida as mudanças técnicas entregues no ciclo v1.8.x com base em:
- histórico de tags Git (v1.8.0 a v1.8.67);
- commits entre as versões;
- documentação já existente no projeto (changelog e docs temáticos).

Objetivo: registrar o que evoluiu em arquitetura, segurança, permissões, auditoria, transferências, financeiro, testes e deploy.

---

## 2. Resumo executivo do ciclo v1.8.x

Principais ganhos técnicos:
- consolidação da hierarquia de permissões por grupos e escopo de igreja;
- robustez de middleware/decorators para escopo automático e fallback seguro;
- módulo de transferências com fluxo completo e notificações;
- app de auditoria com painéis, análises, exportação e admin dedicado;
- hardening de migrations para cenários de banco já existente;
- evolução do pipeline de testes/deploy com settings de teste dedicadas;
- melhorias incrementais de UX em painéis, filtros, navegação e mensagens;
- correções de bugs críticos em produção por lotes curtos (hotfixes versionados).

---

## 3. Linha técnica por blocos

## 3.1 Segurança e permissões (v1.8.0-v1.8.17)

Entregas principais:
- renomeação e padronização de grupos ministeriais;
- proteção de grupos no admin para evitar renomeações acidentais;
- helpers centrais de hierarquia em contas/constants;
- decorators e verificações de acesso convergindo para lógica única;
- escopo por igreja com request.igrejas_permitidas e fallback seguro;
- ajuste de permissões para Pastor Local em módulos específicos;
- padronização de template tags de grupo para API central.

Impacto técnico:
- menor risco de divergência de regra por app;
- menos 403/500 por ausência de contexto no request;
- maior previsibilidade de autorização em views e templates.

---

## 3.2 Transferências de membros (v1.8.18-v1.8.27)

Entregas principais:
- modelo TransferenciaMembro e fluxo inicial de solicitar/listar/aprovar;
- visibilidade de ações por hierarquia e contexto da linha;
- hotfixes de formulário (membro_id e validações);
- notificações no sininho + badge de pendências;
- fluxo completo de decisão (aprovar/recusar/cancelar com motivo);
- command de backfill para notificações históricas.

Impacto técnico:
- processo transacional com rastreabilidade;
- redução de erros de entrada e inconsistência de estado;
- observabilidade funcional via notificações e contadores.

---

## 3.3 Permissões avançadas e testes/admin internos (v1.8.28-v1.8.38)

Entregas principais:
- melhorias em templatetags e helpers de auditoria;
- sistema de solicitação de permissões e painéis hierárquicos;
- ajustes idempotentes de migrations em contas;
- padronização de pytest com settings_test;
- app painel_testes com execução de pytest via admin;
- promoção de assets/admin panel e testes de cargos.

Impacto técnico:
- menor atrito para validar qualidade em ambiente real;
- mitigação de falhas de migração em deploy contínuo;
- base pronta para auditoria operacional de permissões.

---

## 3.4 Auditoria (v1.8.39-v1.8.63)

Entregas principais:
- expansão dos modelos da auditoria;
- painel e rotas de auditoria;
- API de estatísticas para gráficos;
- telas de análise, acumulação de permissões e detalhes de usuário;
- alternar modo auditoria e exportação CSV;
- infraestrutura de middleware/signals/context processor;
- admin dedicado em /admin-auditoria/ com index próprio;
- correções de UX e navegação no admin dedicado;
- consolidação de migrations da auditoria (0001 completo + 0002 compatível);
- rota canônica de atividades suspeitas com retrocompatibilidade;
- refinamento visual das telas de logs e sessões.

Impacto técnico:
- trilha auditável de ações e contexto;
- redução de riscos operacionais de acesso indevido;
- base consistente para monitoramento e investigação.

---

## 3.5 Notificações, testes e financeiro (v1.8.64-v1.8.67)

Entregas principais:
- correção do fluxo "Marcar todas lidas" em notificações;
- remoção de JS inválido na tela de notificações;
- restrição de notificação de assinatura para perfis corretos;
- estabilização da execução de testes no fluxo de deploy com core.settings_test;
- correção dos cards de Contas a Pagar no painel financeiro (valores + quantidades + links de filtro).

Impacto técnico:
- UX de notificações confiável;
- menor ruído para usuários fora do escopo financeiro;
- redução de falso negativo no pipeline de validação;
- painel financeiro com dados coerentes para decisão.

---

## 4. Melhorias de arquitetura relevantes

- Centralização de permissões por constantes e helper hierárquico.
- Uso consistente de decorators de autorização e assinatura.
- Introdução de app de auditoria com separação de responsabilidades.
- Tratamento de migrations com foco em compatibilidade de ambientes antigos.
- Melhor organização de documentação e testes ao longo dos lotes.

---

## 5. Qualidade, testes e operação

Avanços:
- suites de testes adicionadas/ajustadas em permissões e fluxos críticos;
- settings de teste dedicadas para evitar instabilidade de banco remoto;
- validações recorrentes com manage.py check e compilação de templates;
- deploy versionado por tag em lotes curtos, facilitando rollback lógico.

Riscos/residuais observados:
- existe débito de harmonização completa de migrations históricas entre apps;
- parte do ecossistema depende de cobertura de integração mais ampla por perfil.

---

## 6. Inventário resumido de versões (v1.8.x)

- v1.8.0-v1.8.17: base de segurança, escopo e permissões.
- v1.8.18-v1.8.27: módulo de transferências e notificações correlatas.
- v1.8.28-v1.8.38: permissões avançadas, testes e robustez de migrations.
- v1.8.39-v1.8.63: construção e maturidade do módulo de auditoria.
- v1.8.64-v1.8.67: hotfixes de notificações, pipeline de testes e painel financeiro.

---

## 7. Referências

- Histórico de mudanças: ../CHANGELOG.md
- Índice da documentação: INDEX.md
- Manual do usuário: USUARIO_MANUAL.md
- Permissões: HIERARQUIA_PERMISSOES.md, GRUPOS_PERMISSOES.md
- Deploy: ANALISE_SISTEMA_DEPLOY.md
