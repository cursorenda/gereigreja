# Release Notes - Versão 1.5.0

**Data de Lançamento:** 09/03/2026

## 🆕 Novas Funcionalidades

### LGPD - Conformidade com Lei Geral de Proteção de Dados

#### Exportação de Dados Pessoais
- **Exportação em JSON**: Usuários podem baixar todos os seus dados em formato JSON estruturado
- **Exportação em PDF**: Relatório completo formatado com dados pessoais, consentimentos e histórico
- **Dados incluídos**: 
  - Informações de usuário (nome, email, telefone)
  - Dados de membro (igreja, grupos, cargos)
  - Histórico de consentimentos LGPD
  - Metadados (datas de criação, modificação)

#### Histórico de Consentimentos
- Visualização completa de todos os consentimentos dados
- Informações de versão da política aceita
- Datas e horários dos consentimentos
- Endereço IP de origem de cada consentimento

#### Edição de Perfil Aprimorada
- Nova página "Meu Perfil" com interface LGPD-friendly
- **Sincronização opcional** entre dados de User e Membro:
  - Opção explícita para sincronizar Nome e Telefone
  - Modal de confirmação antes da sincronização
  - Campos podem ser editados independentemente se sincronização desabilitada
- Máscara de formatação para telefone brasileiro
- Validação de campos em tempo real

#### Política de Privacidade v1.1
- Política atualizada com detalhes LGPD
- Seções sobre direitos dos titulares
- Informações sobre tratamento de dados
- Prazo de retenção de dados especificado

### Context Processor para Ministério
- Logo do ministério agora aparece consistentemente em todas as páginas
- Nova função `ministerio_context()` injeta variável global automaticamente
- Elimina necessidade de passar `ministerio` manualmente em cada view

## 🔧 Melhorias

### Menu Dropdown de Usuário Reorganizado
Nova estrutura lógica do menu:

**Seção Admin Ministério:**
1. Meu Ministério
2. Gerenciar Igrejas
3. Gerenciar Assinatura *(movido para esta seção)*
4. Gerenciar Usuários
5. Notificações Enviadas

**Seção Todos os Usuários:**
1. Meu Perfil
2. Alterar Senha
3. **Meus Dados - LGPD** *(novo link)*
4. Sair

### Melhorias Visuais
- Logo do ministério com fundo uniforme (mesma cor do sidebar: #212529)
- Remoção de diferença visual entre área do logo e menu lateral
- Melhor consistência visual em toda a aplicação

### Templates
- Template `registrar.html` agora usa `base.html` (sem sidebar)
- Templates de autenticação padronizados e limpos
- Remoção de comentários desnecessários

## 🐛 Correções de Bugs

### Bug Crítico: Sidebar em Páginas Públicas
- **Problema**: Página de registro mostrava menu lateral para usuários não autenticados
- **Solução**: Template `registrar.html` alterado de `base_com_menu.html` para `base.html`
- **Impacto**: Páginas públicas agora têm layout apropriado

### Context Processors
- **Problema**: Função `unread_notifications` foi removida acidentalmente
- **Solução**: Função restaurada completamente
- **Impacto**: Sistema voltou a funcionar corretamente sem ImportError

### Template base.html
- **Problema**: Código HTML órfão após `</html>` causava link "Validar Imagens" no rodapé
- **Solução**: Removido fragmento de código solto
- **Impacto**: Rodapé de páginas públicas limpo

### Uniformização Visual
- **Problema**: Área do logo tinha cor de fundo levemente diferente do sidebar
- **Solução**: Removido `background:rgba(255,255,255,0.05)` da div do logo
- **Impacto**: Visual consistente e profissional

## 📚 Documentação

### Novos Arquivos de Documentação

#### ARQUITETURA_TEMPLATES.md (~600 linhas)
Guia completo da arquitetura de templates do sistema:
- **Matrix de Decisão**: Quando usar cada template base
- **Context Processors**: Documentação completa de todas as funções
- **Estrutura de Menus**: Análise detalhada de sidebar, topnav e dropdown
- **Componentes**: Explicação de cada componente do sistema
- **Checklist de Validação**: Para garantir uso correto dos templates
- **Problemas Comuns**: Soluções para erros frequentes

#### LGPD_IMPLEMENTACAO.md
Documentação técnica da implementação LGPD:
- Modelos de dados (ConsentimentoLGPD)
- Views e formulários
- Templates e interface
- Fluxos de exportação
- Conformidade legal

### README.md Atualizado
- Nova seção "Documentação Técnica"
- Links para toda documentação do projeto
- Organização melhorada

## 🔄 Migrações de Banco de Dados

### Novas Migrations

1. **contas/0004_add_nota_usuario.py**
   - Adiciona campo `nota` ao modelo User
   - Permite anotações sobre usuários

2. **contas/0005_add_consentimento_lgpd.py**
   - Cria modelo `ConsentimentoLGPD`
   - Campos: user, data_consentimento, versao_politica, ip_address
   - Tracking completo de consentimentos

3. **secretaria/10001_add_pessoa_timestamps.py**
   - Adiciona campos de timestamp ao modelo Pessoa
   - Campos: created_at, updated_at
   - Auto-gerenciamento de datas

## 🔒 Segurança e Conformidade

- ✅ Conformidade LGPD ~95% completa
- ✅ Direito de Acesso implementado (Art. 18, I)
- ✅ Direito de Portabilidade implementado (Art. 18, V)
- ✅ Consentimento registrado e rastreável (Art. 8º)
- ✅ Política de Privacidade transparente (Art. 9º)
- ✅ Histórico auditável de consentimentos

## 📊 Estatísticas do Release

- **Arquivos Modificados**: 32
- **Linhas Adicionadas**: 4.525
- **Linhas Removidas**: 177
- **Novos Arquivos**: 8 (3 migrations, 3 templates, 2 documentações)
- **Commits**: 1 principal

## 🚀 Instruções de Deploy

### Pré-requisitos
```bash
# Verificar migrations
python manage.py makemigrations --check
python manage.py migrate --plan
```

### Deploy
```bash
# Push para repositório
git push origin master

# No servidor (Render - automático):
# - Migrations executadas automaticamente
# - Collectstatic executado automaticamente
# - Servidor reiniciado automaticamente
```

### Verificações Pós-Deploy
1. ✅ Acessar página de registro (verificar layout sem sidebar)
2. ✅ Login e verificar menu dropdown reorganizado
3. ✅ Verificar logo do ministério em todas as páginas
4. ✅ Testar exportação de dados (JSON e PDF)
5. ✅ Verificar histórico de consentimentos
6. ✅ Testar edição de perfil com sincronização
7. ✅ Validar link "Meus Dados - LGPD" no menu

## ⚠️ Breaking Changes

**Nenhuma mudança incompatível com versões anteriores.**

Todas as alterações são retrocompatíveis:
- Migrations apenas adicionam campos/modelos
- Templates mantêm funcionalidade existente
- Context processors apenas adicionam variáveis

## 🎯 Próximos Passos (Roadmap)

### Futuras Melhorias LGPD
- [ ] Direito ao Esquecimento (remoção completa de dados)
- [ ] Notificação de vazamentos (se ocorrerem)
- [ ] Portabilidade para outros sistemas
- [ ] Dashboard de conformidade para admins

### Melhorias de UX
- [ ] Tutorial de primeiro acesso
- [ ] Tooltips explicativos em menus
- [ ] Modo escuro (dark mode)

## 🙏 Agradecimentos

Implementação realizada com foco em:
- Conformidade legal (LGPD)
- Experiência do usuário
- Documentação completa
- Manutenibilidade do código

---

**Versão Anterior**: v1.4.0 (06/03/2026)
**Versão Atual**: v1.5.0 (09/03/2026)
**Próxima Versão Planejada**: v1.6.0 (TBD)
