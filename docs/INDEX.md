
# 📚 Índice de Documentação - Sistema Gereigreja

**Última Atualização:** 02/06/2026

---


## 🎯 Documentação Principal

Regra de interpretação deste documento:

- `INDEX.md` é o mapa de navegação.
- `README.md` de cada pasta é a apresentação daquele domínio.

| Documento | Descrição | Última Atualização |
|-----------|-----------|-------------------|
| [../README.md](../README.md) | README principal do projeto | — |
| [../CHANGELOG.md](../CHANGELOG.md) | Histórico de mudanças (todas as versões) | 02/06/2026 |
| [README.md](README.md) | Diretriz oficial da documentação em `docs/` | — |
| [arquitetura/README.md](arquitetura/README.md) | Guia da documentação arquitetural | — |
| [backend/README.md](backend/README.md) | Guia dos padrões de engenharia do backend | — |
| [apps/README.md](apps/README.md) | Guia da documentação por módulo de negócio | — |
| [operacoes/README.md](operacoes/README.md) | Guia operacional (runbooks e checklists) | — |
| [qualidade/README.md](qualidade/README.md) | Guia de qualidade e gates de release | — |

---


## 📌 Consolidado v1.8.x

| Documento | Descrição | Última Atualização |
|-----------|-----------|-------------------|
| [sistema/MELHORIAS_SISTEMA_v1.8.0_a_v1.8.67.md](sistema/MELHORIAS_SISTEMA_v1.8.0_a_v1.8.67.md) | Consolidação técnica do ciclo v1.8.0 até v1.8.67 | 12/04/2026 |
| [usuario/MELHORIAS_USUARIOS_v1.8.0_a_v1.8.67.md](usuario/MELHORIAS_USUARIOS_v1.8.0_a_v1.8.67.md) | Consolidação funcional para usuários finais (v1.8.0-v1.8.67) | 12/04/2026 |

---


## 🏗️ Arquitetura & Estrutura

| Documento | Descrição |
|-----------|-----------|
| [templates/ARQUITETURA_TEMPLATES.md](templates/ARQUITETURA_TEMPLATES.md) | Estrutura de templates do sistema |
| [sistema/ARQUITETURA_ADMIN.md](sistema/ARQUITETURA_ADMIN.md) | **NOVO:** Arquitetura do admin Django (modularização, admin sites, convenções) |
| [sistema/ADMIN_MIXINS.md](sistema/ADMIN_MIXINS.md) | **NOVO:** Referência dos admin mixins reutilizáveis (`core/admin_mixins.py`) |
| [sistema/DECORATORS_SEGURANCA.md](sistema/DECORATORS_SEGURANCA.md) | Decorators de segurança e autenticação |
| [sistema/IMPLEMENTACAO_DECORATOR_DASHBOARD.md](sistema/IMPLEMENTACAO_DECORATOR_DASHBOARD.md) | Implementação de decorators no dashboard |
| [sistema/ANALISE_DECORATORS_SISTEMA.md](sistema/ANALISE_DECORATORS_SISTEMA.md) | Análise completa dos decorators |

---


## 🔐 Segurança & Permissões

| Documento | Descrição |
|-----------|-----------|
| [sistema/GRUPOS_PERMISSOES.md](sistema/GRUPOS_PERMISSOES.md) | Sistema de grupos e permissões |
| [sistema/AUDITORIA_PERMISSOES_SISTEMA_COMPLETO.md](sistema/AUDITORIA_PERMISSOES_SISTEMA_COMPLETO.md) | Auditoria completa de permissões |
| [sistema/AUDITORIA_PERMISSOES_PROFESSOR_EBD.md](sistema/AUDITORIA_PERMISSOES_PROFESSOR_EBD.md) | Permissões específicas Escola Bíblica |
| [sistema/ANALISE_MENUS_BASEADOS_PERMISSOES.md](sistema/ANALISE_MENUS_BASEADOS_PERMISSOES.md) | Sistema de menus baseado em permissões |
| [deploy/LGPD_IMPLEMENTACAO.md](deploy/LGPD_IMPLEMENTACAO.md) | Implementação de conformidade LGPD |

---


## ⚙️ Funcionalidades & Módulos

### Cadastro de Pessoas
| Documento | Descrição |
|-----------|-----------|
| [sistema/VALIDACOES_CADASTRO_PESSOAS.md](sistema/VALIDACOES_CADASTRO_PESSOAS.md) | **NOVO:** Sistema de validações (CPF, Email, Máscaras, ViaCEP) |
| [sistema/ANALISE_MELHORIAS_CADASTRO_PESSOAS.md](sistema/ANALISE_MELHORIAS_CADASTRO_PESSOAS.md) | Análise completa: 23 melhorias propostas |
| [sistema/REGRAS_TIPOS_PESSOA_STATUS.md](sistema/REGRAS_TIPOS_PESSOA_STATUS.md) | Regras de negócio: Tipos e Status de Pessoas |

### Cargos
| Documento | Descrição |
|-----------|-----------|
| [sistema/CARGOS_USUARIOS.md](sistema/CARGOS_USUARIOS.md) | Guia operacional para secretaria e liderancas no uso da tela de cargos |
| [sistema/CARGOS_SISTEMA.md](sistema/CARGOS_SISTEMA.md) | Regras tecnicas, sincronizacao de grupos e checklist pre-deploy |

### Participantes & Eventos
| Documento | Descrição |
|-----------|-----------|
| [sistema/SISTEMA_HIBRIDO_PARTICIPANTES.md](sistema/SISTEMA_HIBRIDO_PARTICIPANTES.md) | Sistema híbrido de participantes (visitantes/membros) |

### Escola Dominical (EBD)
| Documento | Descrição |
|-----------|-----------|
| [sistema/ESCOLA_DOMINICAL_GOVERNANCA_PERIODO.md](sistema/ESCOLA_DOMINICAL_GOVERNANCA_PERIODO.md) | Governanca de periodo, auto-sync de licoes e validacoes de dominio da EBD |
| [sistema/ESCOLA_DOMINICAL_ROADMAP_PREMIUM.md](sistema/ESCOLA_DOMINICAL_ROADMAP_PREMIUM.md) | Roadmap premium da EBD com fluxo operacional, decisoes de UX e plano por sprints |
| [sistema/ESCOLA_DOMINICAL_CONFIG_LOCAL_IGREJA.md](sistema/ESCOLA_DOMINICAL_CONFIG_LOCAL_IGREJA.md) | Configuracao EBD local por igreja (church-first com fallback ministerial) e plano de rollout |
| [sistema/ESCOLA_DOMINICAL_HOMOLOGACAO_CONFIG_LOCAL_IGREJA.md](sistema/ESCOLA_DOMINICAL_HOMOLOGACAO_CONFIG_LOCAL_IGREJA.md) | Checklist de homologacao para validar configuracao EBD local por igreja e fallback ministerial |

### Seletor de Igreja
| Documento | Descrição |
|-----------|-----------|
| [sistema/SELETOR_IGREJA.md](sistema/SELETOR_IGREJA.md) | Funcionalidade de seleção de igreja ativa |
| [ai/AI_CONTEXT_CHURCH_SELECTOR.md](ai/AI_CONTEXT_CHURCH_SELECTOR.md) | Contexto AI: seletor de igreja |

### Assinatura e Planos (v1.9.2)
| Documento | Público | Descrição |
|-----------|---------|-----------|
| [usuario/MANUAL_ASSINATURA_PLANOS.md](usuario/MANUAL_ASSINATURA_PLANOS.md) | Usuário | Como usar a página de assinatura, planos, limites, trial, cortesia |
| [sistema/ARQUITETURA_ASSINATURA_PLANOS.md](sistema/ARQUITETURA_ASSINATURA_PLANOS.md) | Desenvolvedor | Modelos, services, view gerenciar_assinatura, integração Stripe |
| [sistema/FLUXO_ELEGIBILIDADE_ACESSO.md](sistema/FLUXO_ELEGIBILIDADE_ACESSO.md) | Desenvolvedor/IA | **NOVO:** Fluxo completo de elegibilidade — plano pioneiro grátis × cortesia × trial × status × BETA — ordem de verificação, inconsistências e correções |
| [ai/AI_CONTEXT_SISTEMA_COMPLETO.md](ai/AI_CONTEXT_SISTEMA_COMPLETO.md) | IA | Contexto mestre do sistema: multi-tenant, permissões, padrões, anti-padrões |

### Secretaria - Documentos e Certificados (v1.12.0)
| Documento | Público | Descrição |
|-----------|---------|-----------|
| [sistema/ATUALIZACAO_v1.12.0.md](sistema/ATUALIZACAO_v1.12.0.md) | Desenvolvedor/Operação | Reorganização de menu, evolução de certificados, novo módulo de carta de recomendação e governança de templates por ministério |

---


## 🧩 Apps (Módulos)

| Documento | Descrição |
|-----------|-----------|
| [apps/README.md](apps/README.md) | Índice e padrão dos documentos por módulo |
| [apps/04-Comunicacao.md](apps/04-Comunicacao.md) | Arquitetura e operação do módulo Comunicação |

---


## 🚀 Deploy & Infraestrutura

| Documento | Descrição |
|-----------|-----------|
| [deploy/ANALISE_SISTEMA_DEPLOY.md](deploy/ANALISE_SISTEMA_DEPLOY.md) | Análise completa do sistema de deploy |

---


## 🛠️ Operações & Qualidade (Comunicação)

| Documento | Descrição |
|-----------|-----------|
| [operacoes/COMUNICACAO_WAHA_RUNBOOK.md](operacoes/COMUNICACAO_WAHA_RUNBOOK.md) | Runbook operacional da integração WAHA no módulo Comunicação |
| [qualidade/COMUNICACAO_CHECKLIST_RELEASE_WAHA.md](qualidade/COMUNICACAO_CHECKLIST_RELEASE_WAHA.md) | Checklist de release para mudanças de Comunicação com impacto em WAHA |

---


## 🐛 Troubleshooting & UX

| Documento | Descrição |
|-----------|-----------|
| [relatorios/PROBLEMA_UX_PAGINA_VAZIA.md](relatorios/PROBLEMA_UX_PAGINA_VAZIA.md) | Solução: problema de páginas vazias |

---


## 📝 Release Notes

### Versões Recentes
- [release-notes/RELEASE_NOTES_v1.13.13.md](release-notes/RELEASE_NOTES_v1.13.13.md) - EBD com pontuacao configuravel, ranking de alunos e ajustes de preview social do blog
- [release-notes/RELEASE_NOTES_v1.13.12.md](release-notes/RELEASE_NOTES_v1.13.12.md) - EBD church-first por igreja e chamada com selecao segura de aula
- [release-notes/RELEASE_NOTES_v1.8.23.md](release-notes/RELEASE_NOTES_v1.8.23.md) - Ciclo v1.8.10 até v1.8.23
- [release-notes/RELEASE_NOTES_v1.7.2.md](release-notes/RELEASE_NOTES_v1.7.2.md)

### Histórico Completo
Ver pasta [release-notes/](release-notes/) para histórico de versões.

---

## 📊 Relatórios e Análises

| Documento | Descrição |
|-----------|-----------|
| [relatorios/RESUMO_EXECUTIVO_CADASTROS.md](relatorios/RESUMO_EXECUTIVO_CADASTROS.md) | Resumo executivo dos cadastros |
| [relatorios/README_ANALISE_CADASTROS.md](relatorios/README_ANALISE_CADASTROS.md) | README análise de cadastros |
| [relatorios/INDICE_ANALISE_CADASTROS.md](relatorios/INDICE_ANALISE_CADASTROS.md) | Índice análise de cadastros |
| [relatorios/ANTES_E_DEPOIS_CONSOLIDACAO.md](relatorios/ANTES_E_DEPOIS_CONSOLIDACAO.md) | Antes e depois da consolidação |
| [relatorios/ANALISE_CADASTRO_PESSOA_ALUNO.md](relatorios/ANALISE_CADASTRO_PESSOA_ALUNO.md) | Análise cadastro pessoa/aluno |

---


## 👤 Documentação do Usuário

| Documento | Descrição |
|-----------|-----------|
| [usuario/USUARIO_MANUAL.md](usuario/USUARIO_MANUAL.md) | Manual do usuário |
| [usuario/README_IGREJA_USER.md](usuario/README_IGREJA_USER.md) | Guia rápido - Página Igreja |
| [usuario/MELHORIAS_USUARIOS_v1.7.2.md](usuario/MELHORIAS_USUARIOS_v1.7.2.md) | Novidades v1.7.2 |
| [usuario/MELHORIAS_USUARIOS_v1.8.0_a_v1.8.67.md](usuario/MELHORIAS_USUARIOS_v1.8.0_a_v1.8.67.md) | Novidades v1.8.0 a v1.8.67 |
| [usuario/MELHORIAS_USUARIOS_v1.8.75.md](usuario/MELHORIAS_USUARIOS_v1.8.75.md) | Novidades v1.8.75 |
| [usuario/chat_respostas.md](usuario/chat_respostas.md) | Respostas rápidas/FAQ |

---

## 📂 Estrutura de Diretórios

```
Gereigreja/
├── docs/                          # 📚 Documentação técnica (VOCÊ ESTÁ AQUI)
│   ├── INDEX.md                   # Este índice
│   ├── release-notes/             # Release notes por versão
│   │   ├── RELEASE_NOTES_v1.0.0.md
│   │   ├── ...
│   │   ├── RELEASE_NOTES_v1.3.1.md
│   │   └── RELEASE_NOTES_v1.8.23.md
│   ├── VALIDACOES_CADASTRO_PESSOAS.md
│   ├── ANALISE_MELHORIAS_CADASTRO_PESSOAS.md
│   ├── REGRAS_TIPOS_PESSOA_STATUS.md
│   ├── SISTEMA_HIBRIDO_PARTICIPANTES.md
│   ├── ARQUITETURA_TEMPLATES.md
│   ├── DECORATORS_SEGURANCA.md
│   ├── GRUPOS_PERMISSOES.md
│   ├── LGPD_IMPLEMENTACAO.md
│   ├── SELETOR_IGREJA.md
│   └── ... (ver lista completa acima)
│
├── notes/                         # 📔 Notas e backups
│   ├── ANALISE_GRUPOS_PERMISSOES.md
│   ├── CHANGELOG_v1.2.0.md
│   ├── FASE2_COMPLETA.md
│   └── README_old_backup.md
│
├── README.md                      # 📖 README principal
├── CHANGELOG.md                   # 📝 Changelog ativo
└── CHANGELOG.md                   # 📝 Histórico consolidado de mudanças
```

---

## 🆕 Documentações Recentes

### 02/06/2026 - Release Notes v1.13.13
- **Arquivo:** [release-notes/RELEASE_NOTES_v1.13.13.md](release-notes/RELEASE_NOTES_v1.13.13.md)
- **Conteúdo:**
   - pontuacao EBD configuravel por igreja
   - ranking de melhores alunos por pontos no dashboard
   - correcoes de Open Graph/Twitter no blog para preview social

### 01/06/2026 - Release Notes v1.13.12
- **Arquivo:** [release-notes/RELEASE_NOTES_v1.13.12.md](release-notes/RELEASE_NOTES_v1.13.12.md)
- **Conteúdo:**
   - consolidacao do modelo EBD church-first por igreja
   - melhorias operacionais da chamada com seletor seguro por licao valida
   - validacoes, impacto e checklist operacional de deploy

### 01/06/2026 - Escola Dominical: Checklist de Homologacao (Config Local por Igreja)
- **Arquivo:** [sistema/ESCOLA_DOMINICAL_HOMOLOGACAO_CONFIG_LOCAL_IGREJA.md](sistema/ESCOLA_DOMINICAL_HOMOLOGACAO_CONFIG_LOCAL_IGREJA.md)
- **Conteúdo:**
   - cenarios de teste local x herdado
   - validacao de dashboard, turmas, wizard e eventos
   - validacao da mini-lista de classes na aba EBD da igreja
   - criterio de Go/No-Go e rollback funcional rapido

### 01/06/2026 - Escola Dominical: Configuracao Local por Igreja (Fase 1)
- **Arquivo:** [sistema/ESCOLA_DOMINICAL_CONFIG_LOCAL_IGREJA.md](sistema/ESCOLA_DOMINICAL_CONFIG_LOCAL_IGREJA.md)
- **Conteúdo:**
   - novos campos EBD na igreja com migration e backfill
   - resolucao church-first com fallback ministerial
   - auto-sync por sinais para mudancas de configuracao local
   - ajuste do wizard, agenda macro e atalho no dashboard

### 01/06/2026 - Escola Dominical: Roadmap Premium
- **Arquivo:** [sistema/ESCOLA_DOMINICAL_ROADMAP_PREMIUM.md](sistema/ESCOLA_DOMINICAL_ROADMAP_PREMIUM.md)
- **Conteúdo:**
   - diretriz de produto para operacao semanal
   - benchmark de fluxo (planejamento -> operacao -> engajamento -> governanca)
   - decisao de UX: classe como configuracao, nao foco operacional
   - plano de implementacao por sprints e metricas de sucesso

### 28/05/2026 - Escola Dominical: Governanca de Periodo e Automacao
- **Arquivo:** [sistema/ESCOLA_DOMINICAL_GOVERNANCA_PERIODO.md](sistema/ESCOLA_DOMINICAL_GOVERNANCA_PERIODO.md)
- **Conteúdo:**
   - fonte de verdade do periodo EBD por ministerio
   - auto-sync de periodos e licoes sem clique manual
   - validacoes estritas para licao, frequencia e oferta por periodo
   - constraint de unicidade de licoes por turma+data

### 13/05/2026 - Secretaria: Documentos, Certificados e Carta
- **Arquivo:** [sistema/ATUALIZACAO_v1.12.0.md](sistema/ATUALIZACAO_v1.12.0.md)
- **Conteúdo:**
   - reorganização do menu da secretaria com foco em documentos
   - evolução de certificados (apresentação e batismo) com impressão fiel por html2canvas
   - novo módulo de carta de recomendação (A5)
   - governança multi-ministério para modelos padrão/exclusivos
   - melhorias de admin para prévia embutida e prévia em nova aba

### 12/04/2026 - Consolidação do ciclo v1.8.x
- **Arquivo:** [MELHORIAS_SISTEMA_v1.8.0_a_v1.8.67.md](MELHORIAS_SISTEMA_v1.8.0_a_v1.8.67.md)
- **Conteúdo:**
   - consolidação técnica por blocos (segurança, transferências, auditoria, deploy e financeiro)
   - resumo executivo e inventário por fase do ciclo v1.8.x

- **Arquivo:** [MELHORIAS_USUARIOS_v1.8.0_a_v1.8.67.md](MELHORIAS_USUARIOS_v1.8.0_a_v1.8.67.md)
- **Conteúdo:**
   - visão para operação diária em linguagem de usuário
   - principais ganhos por módulo e orientações práticas

### 08/04/2026 - Modulo de Cargos
- **Arquivo:** [CARGOS_USUARIOS.md](CARGOS_USUARIOS.md)
- **Conteúdo:**
   - Fluxo operacional de criar/editar cargo
   - Vincular e encerrar ocupantes
   - Regras de exclusao e FAQ rapido para usuarios

- **Arquivo:** [CARGOS_SISTEMA.md](CARGOS_SISTEMA.md)
- **Conteúdo:**
   - Regra consolidada de grupos efetivos
   - Arquitetura de sincronizacao (servico central + signals)
   - Casos criticos, riscos e checklist tecnico pre-deploy

### 12/03/2026 - Sistema de Validações
- **Arquivo:** [VALIDACOES_CADASTRO_PESSOAS.md](VALIDACOES_CADASTRO_PESSOAS.md)
- **Conteúdo:**
  - ✅ Validação CPF (algoritmo dígito verificador)
  - ✅ Validação Email (regex + normalização)
  - ✅ Máscaras JavaScript (CPF, Telefone, CEP, RG)
  - ✅ Integração API ViaCEP (busca automática endereço)
  - ✅ Casos de teste completos
  - ✅ Troubleshooting

### 11/03/2026 - Análise de Melhorias
- **Arquivo:** [ANALISE_MELHORIAS_CADASTRO_PESSOAS.md](ANALISE_MELHORIAS_CADASTRO_PESSOAS.md)
- **Conteúdo:**
  - 23 melhorias propostas para cadastro de pessoas
  - Divididas em 5 categorias (Layout, Profissionalismo, Funcionalidades, Performance, Documentação)
  - Estimativas de esforço e priorização
  - Roadmap sugerido (4 sprints)

---

## 📌 Como Usar Este Índice

1. **Localizar Documentação:**
   - Use a tabela de conteúdo acima
   - Ou busque por palavra-chave (Ctrl+F)

2. **Adicionar Nova Documentação:**
   ```markdown
   1. Criar arquivo em docs/
   2. Adicionar entrada neste INDEX.md
   3. Atualizar data de "Última Atualização"
   ```

3. **Organização:**
   - Documentações técnicas → `docs/`
   - Notas temporárias → `notes/`
   - Release notes recentes → raiz
   - Release notes antigas → `docs/release-notes/`

---

## ✅ Boas Práticas

- ✅ Manter documentações na pasta `docs/`
- ✅ Nomear arquivos descritivamente (MAIUSCULAS_SEPARADAS.md)
- ✅ Atualizar este índice ao adicionar nova documentação
- ✅ Incluir data de criação/atualização nos documentos
- ✅ Usar Markdown para formatação
- ✅ Adicionar links internos entre documentações relacionadas

---

**Manutenção:** Atualizar este índice sempre que adicionar/remover documentação  
**Contato:** Ver README principal do projeto para informações de contato
