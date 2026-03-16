# 📚 Documentação Técnica - Gereigreja

Esta pasta contém toda a documentação técnica do sistema Gereigreja.

## 🗂️ Organização

A documentação está organizada em categorias temáticas. Veja o **[INDEX.md](INDEX.md)** para uma lista completa e navegável de todos os documentos.

## 📖 Acesso Rápido

### Documentações Mais Acessadas

1. **[VALIDACOES_CADASTRO_PESSOAS.md](VALIDACOES_CADASTRO_PESSOAS.md)**  
   Sistema completo de validações (CPF, Email, Máscaras, ViaCEP) - **NOVO 12/03/2026**

2. **[ANALISE_MELHORIAS_CADASTRO_PESSOAS.md](ANALISE_MELHORIAS_CADASTRO_PESSOAS.md)**  
   23 melhorias propostas para o cadastro de pessoas

3. **[GRUPOS_PERMISSOES.md](GRUPOS_PERMISSOES.md)**  
   Sistema de grupos e permissões do sistema

4. **[ARQUITETURA_TEMPLATES.md](ARQUITETURA_TEMPLATES.md)**  
   Estrutura de templates e componentes reutilizáveis

5. **[LGPD_IMPLEMENTACAO.md](LGPD_IMPLEMENTACAO.md)**  
   Conformidade com LGPD

## 🔍 Encontrar Documentação

**Método 1: Usar o Índice**
- Abra [INDEX.md](INDEX.md)
- Navegue pelas categorias
- Clique no link do documento desejado

**Método 2: Busca por Palavra-Chave**
- Use a busca do editor (Ctrl+Shift+F)
- Busque na pasta `docs/`

**Método 3: Listar Arquivos**
```bash
# PowerShell
Get-ChildItem -Path docs/ -Filter *.md | Select-Object Name

# Git Bash / Linux
ls docs/*.md
```

## 📝 Adicionar Nova Documentação

1. **Criar arquivo nesta pasta:**
   ```bash
   # Padrão de nome: MAIUSCULAS_SEPARADAS_POR_UNDERLINE.md
   touch docs/NOME_DA_DOCUMENTACAO.md
   ```

2. **Usar template padrão:**
   ```markdown
   # Título da Documentação
   
   **Data de Criação:** DD/MM/YYYY
   **Última Atualização:** DD/MM/YYYY
   **Autor:** Nome/Sistema
   
   ---
   
   ## Visão Geral
   
   [Descrição breve do que documenta]
   
   ## Conteúdo
   
   [Estrutura do documento]
   ```

3. **Atualizar o índice:**
   - Abra [INDEX.md](INDEX.md)
   - Adicione entrada na categoria apropriada
   - Atualize data de "Última Atualização"

4. **Commit com mensagem descritiva:**
   ```bash
   git add docs/NOME_DA_DOCUMENTACAO.md docs/INDEX.md
   git commit -m "docs: adiciona documentação sobre [assunto]"
   ```

## 📂 Estrutura de Pastas

```
docs/
├── README.md                  # Este arquivo (introdução)
├── INDEX.md                   # Índice navegável completo
├── release-notes/             # Release notes de versões antigas
│   ├── RELEASE_NOTES_v1.0.0.md
│   ├── ...
│   └── RELEASE_NOTES_v1.3.1.md
└── [documentações técnicas]   # Arquivos .md organizados tematicamente
```

## 🎯 Tipos de Documentação

### 1. Análises Técnicas
Prefixo: `ANALISE_`  
Exemplo: `ANALISE_MENUS_BASEADOS_PERMISSOES.md`

### 2. Implementações
Prefixo: `IMPLEMENTACAO_`  
Exemplo: `IMPLEMENTACAO_DECORATOR_DASHBOARD.md`

### 3. Auditorias
Prefixo: `AUDITORIA_`  
Exemplo: `AUDITORIA_PERMISSOES_SISTEMA_COMPLETO.md`

### 4. Regras de Negócio
Prefixo: `REGRAS_`  
Exemplo: `REGRAS_TIPOS_PESSOA_STATUS.md`

### 5. Sistemas/Módulos
Sem prefixo específico  
Exemplo: `VALIDACOES_CADASTRO_PESSOAS.md`

## ✅ Boas Práticas

### Nomenclatura
- ✅ Usar MAIÚSCULAS
- ✅ Separar palavras com underline (_)
- ✅ Nome descritivo e específico
- ❌ Abreviações excessivas
- ❌ Espaços ou caracteres especiais

### Conteúdo
- ✅ Incluir data de criação/atualização
- ✅ Usar Markdown com formatação consistente
- ✅ Incluir exemplos de código quando relevante
- ✅ Adicionar tabelas de resumo
- ✅ Criar índice interno para docs longos
- ✅ Incluir links para arquivos relacionados

### Manutenção
- ✅ Atualizar INDEX.md ao adicionar documentação
- ✅ Revisar e atualizar periodicamente
- ✅ Arquivar documentações obsoletas (pasta archive/)
- ✅ Manter versionamento via Git

## 🔗 Links Úteis

- **[README Principal](../README.md)** - Visão geral do projeto
- **[CHANGELOG](../CHANGELOG.md)** - Histórico de mudanças
- **[Release Notes Recentes](../RELEASE_NOTES_v1.6.0.md)** - Última versão

## 📞 Suporte

Para dúvidas sobre documentação ou sugestões de melhorias, consulte o README principal do projeto.

---

**Última Atualização:** 12/03/2026  
**Mantenedor:** Sistema Gereigreja
