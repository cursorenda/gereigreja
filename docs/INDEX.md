# 📚 Índice de Documentação - Sistema Gereigreja

**Última Atualização:** 12/03/2026

---

## 🎯 Documentação Principal

| Documento | Descrição | Última Atualização |
|-----------|-----------|-------------------|
| [../README.md](../README.md) | README principal do projeto | — |
| [../CHANGELOG.md](../CHANGELOG.md) | Histórico de mudanças (todas as versões) | 12/03/2026 |

---

## 🏗️ Arquitetura & Estrutura

| Documento | Descrição |
|-----------|-----------|
| [ARQUITETURA_TEMPLATES.md](ARQUITETURA_TEMPLATES.md) | Estrutura de templates do sistema |
| [DECORATORS_SEGURANCA.md](DECORATORS_SEGURANCA.md) | Decorators de segurança e autenticação |
| [IMPLEMENTACAO_DECORATOR_DASHBOARD.md](IMPLEMENTACAO_DECORATOR_DASHBOARD.md) | Implementação de decorators no dashboard |
| [ANALISE_DECORATORS_SISTEMA.md](ANALISE_DECORATORS_SISTEMA.md) | Análise completa dos decorators |

---

## 🔐 Segurança & Permissões

| Documento | Descrição |
|-----------|-----------|
| [GRUPOS_PERMISSOES.md](GRUPOS_PERMISSOES.md) | Sistema de grupos e permissões |
| [AUDITORIA_PERMISSOES_SISTEMA_COMPLETO.md](AUDITORIA_PERMISSOES_SISTEMA_COMPLETO.md) | Auditoria completa de permissões |
| [AUDITORIA_PERMISSOES_PROFESSOR_EBD.md](AUDITORIA_PERMISSOES_PROFESSOR_EBD.md) | Permissões específicas Escola Bíblica |
| [ANALISE_MENUS_BASEADOS_PERMISSOES.md](ANALISE_MENUS_BASEADOS_PERMISSOES.md) | Sistema de menus baseado em permissões |
| [LGPD_IMPLEMENTACAO.md](LGPD_IMPLEMENTACAO.md) | Implementação de conformidade LGPD |

---

## ⚙️ Funcionalidades & Módulos

### Cadastro de Pessoas
| Documento | Descrição |
|-----------|-----------|
| [VALIDACOES_CADASTRO_PESSOAS.md](VALIDACOES_CADASTRO_PESSOAS.md) | **NOVO:** Sistema de validações (CPF, Email, Máscaras, ViaCEP) |
| [ANALISE_MELHORIAS_CADASTRO_PESSOAS.md](ANALISE_MELHORIAS_CADASTRO_PESSOAS.md) | Análise completa: 23 melhorias propostas |
| [REGRAS_TIPOS_PESSOA_STATUS.md](REGRAS_TIPOS_PESSOA_STATUS.md) | Regras de negócio: Tipos e Status de Pessoas |

### Participantes & Eventos
| Documento | Descrição |
|-----------|-----------|
| [SISTEMA_HIBRIDO_PARTICIPANTES.md](SISTEMA_HIBRIDO_PARTICIPANTES.md) | Sistema híbrido de participantes (visitantes/membros) |

### Seletor de Igreja
| Documento | Descrição |
|-----------|-----------|
| [SELETOR_IGREJA.md](SELETOR_IGREJA.md) | Funcionalidade de seleção de igreja ativa |
| [AI_CONTEXT_CHURCH_SELECTOR.md](AI_CONTEXT_CHURCH_SELECTOR.md) | Contexto AI: seletor de igreja |

---

## 🚀 Deploy & Infraestrutura

| Documento | Descrição |
|-----------|-----------|
| [ANALISE_SISTEMA_DEPLOY.md](ANALISE_SISTEMA_DEPLOY.md) | Análise completa do sistema de deploy |

---

## 🐛 Troubleshooting & UX

| Documento | Descrição |
|-----------|-----------|
| [PROBLEMA_UX_PAGINA_VAZIA.md](PROBLEMA_UX_PAGINA_VAZIA.md) | Solução: problema de páginas vazias |

---

## 📝 Release Notes

### Versões Recentes (Raiz)
- [../RELEASE_NOTES_v1.6.0.md](../RELEASE_NOTES_v1.6.0.md) - Última versão estável
- [../RELEASE_NOTES_v1.5.0.md](../RELEASE_NOTES_v1.5.0.md)

### Versões Antigas
Ver pasta [release-notes/](release-notes/) para histórico completo (v1.0.0 até v1.3.1)

---

## 📂 Estrutura de Diretórios

```
Gereigreja/
├── docs/                          # 📚 Documentação técnica (VOCÊ ESTÁ AQUI)
│   ├── INDEX.md                   # Este índice
│   ├── release-notes/             # Release notes antigas
│   │   ├── RELEASE_NOTES_v1.0.0.md
│   │   ├── ...
│   │   └── RELEASE_NOTES_v1.3.1.md
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
└── RELEASE_NOTES_v1.x.x.md        # 🚀 Release notes recentes
```

---

## 🆕 Documentações Recentes (Março 2026)

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
