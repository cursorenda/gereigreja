# 🔐 Análise Completa de Grupos e Permissões do Sistema GereIgreja

**Data da Análise:** 09/02/2026  
**Versão do Sistema:** v1.2.0

---

## 📊 RESUMO EXECUTIVO

O sistema GereIgreja utiliza grupos (papéis/roles) para controle de acesso baseado em funções (RBAC - Role-Based Access Control). A análise do código identificou **8 grupos** mencionados, com uso variado entre módulos.

### Status Geral
- ✅ **Estrutura básica implementada** 
- ⚠️ **Falta padronização** entre módulos (nomes inconsistentes)
- ⚠️ **Documentação incompleta** sobre hierarquia de permissões
- ⚠️ **Alguns grupos sem implementação** completa

---

## 🏷️ GRUPOS IDENTIFICADOS NO CÓDIGO

### 1. **Admin Ministerio** 
**Status:** ✅ Amplamente implementado  
**Uso:** Administrador principal do ministério (cliente SaaS)  
**Localização no código:**
- `contas/views.py` (9 verificações)
- `configuracao/views.py` (3 verificações)
- `suporte/views.py` (2 verificações)
- `financeiro/utils.py` (função `is_admin_org`)
- `templates/base_com_menu.html` (menu de configuração)

**Permissões:**
- ✅ Gerenciar usuários
- ✅ Gerenciar igrejas
- ✅ Gerenciar ministério
- ✅ Editar papéis/grupos
- ✅ Visualizar dashboard de métricas (admin)
- ✅ Gerenciar assinatura
- ✅ Acesso ao módulo de suporte
- ✅ Todas as permissões (via comando `atribuir_permissoes_admin_ministerio.py`)

**Hierarquia:** 🔴 NÍVEL 1 (Máximo acesso - exceto superuser)

**Análise:**
- ✅ Bem implementado e consistente
- ✅ Comando de gerenciamento para atribuir permissões
- ✅ Usado como referência principal em toda aplicação
- ⚠️ Não tem separação entre Admin Sistema (gereigreja@gmail.com) e Admin Ministerio (cliente)

---

### 2. **Superintendentes**
**Status:** ✅ Implementado para EBD  
**Uso:** Administradores da Escola Bíblica Dominical  
**Localização no código:**
- `core/decorators.py` - `superintendente_required()`
- `escola_biblica/tests/test_flow.py`

**Permissões:**
- ✅ Gerenciar classes EBD
- ✅ Gerenciar alunos
- ✅ Gerenciar professores
- ✅ Acesso amplo ao módulo EBD

**Hierarquia:** 🟡 NÍVEL 2 (Acesso específico ao módulo EBD)

**Análise:**
- ✅ Bem implementado para o módulo específico
- ℹ️ Escopo limitado (apenas EBD)
- ⚠️ Nome no plural (inconsistente com outros grupos)

---

### 3. **Secretaria EBD**
**Status:** ✅ Implementado para EBD  
**Uso:** Secretariado da Escola Bíblica  
**Localização no código:**
- `core/decorators.py` - `secretaria_ebd_required()`
- `escola_biblica/tests/test_flow.py`

**Permissões:**
- ✅ Gerenciar presenças EBD
- ✅ Visualizar relatórios EBD
- ⚠️ Menos permissões que Superintendentes

**Hierarquia:** 🟡 NÍVEL 3 (Acesso limitado ao módulo EBD)

**Análise:**
- ✅ Implementado corretamente
- ⚠️ Hierarquia: permite Superintendentes OR Secretaria EBD (não é subordinado)

---

### 4. **Lideranca Financeira**
**Status:** ✅ Parcialmente implementado  
**Uso:** Líderes com acesso expandido ao financeiro  
**Localização no código:**
- `financeiro/utils.py` - `is_finance_leader()`

**Permissões:**
- ✅ Ver igrejas subordinadas recursivamente
- ✅ Expandir permissões de visualização
- ⚠️ Não está claro se pode editar ou apenas visualizar

**Hierarquia:** 🟡 NÍVEL 2 (Acesso específico ao módulo Financeiro)

**Análise:**
- ⚠️ Implementação incompleta
- ⚠️ Lógica confusa: `is_admin_org()` OR `Lideranca Financeira`
- ⚠️ Falta clareza sobre diferença entre este grupo e Tesoureiro

---

### 5. **Tesoureiro**
**Status:** ⚠️ Mencionado mas não implementado completamente  
**Uso:** Gerenciar finanças da igreja  
**Localização no código:**
- `financeiro/utils.py` - `is_tesoureiro()`
- `financeiro/utils.py` - `has_finance_edit_permission()`

**Permissões (esperadas):**
- ✅ Visualizar finanças
- ✅ Editar transações
- ✅ Adicionar/excluir lançamentos
- ❌ NÃO pode gerenciar categorias globais (Admin Ministerio only)

**Hierarquia:** 🟡 NÍVEL 2-3 (Acesso ao módulo Financeiro)

**Análise:**
- ⚠️ Grupo definido mas **pode não estar criado no banco**
- ⚠️ Comentário no código: "IMPORTANTE: Ajuste o nome do grupo se for diferente de 'Tesoureiro'"
- ⚠️ Não há verificações consistentes em views (apenas em utils.py)

---

### 6. **Lider Igreja**
**Status:** ⚠️ Mencionado mas implementação incompleta  
**Uso:** Líder/Pastor de igreja local  
**Localização no código:**
- `financeiro/utils.py` - `is_lider_igreja()`
- `financeiro/utils.py` - `has_finance_view_permission()`

**Permissões (esperadas):**
- ✅ Visualizar finanças da própria igreja
- ❌ NÃO pode editar finanças
- ⚠️ Não especificado o acesso a outros módulos

**Hierarquia:** 🟢 NÍVEL 3-4 (Visualização apenas)

**Análise:**
- ⚠️ Grupo mencionado mas **implementação duvidosa**
- ⚠️ Comentário no código: "IMPORTANTE: Ajuste o nome do grupo se for diferente de 'Lider Igreja'"
- ⚠️ Apenas para visualização, não tem permissões de edição

---

### 7. **Gestor**
**Status:** ❌ Apenas mencionado em template  
**Uso:** Não especificado  
**Localização no código:**
- `configuracao/templates/configuracao/perfil/meu_perfil.html` (linha 138, 212)

**Permissões (esperadas):**
- ⚠️ Não especificadas
- Aparentemente pode: ver configuração da ministério

**Hierarquia:** ❓ Indefinida

**Análise:**
- ❌ **Não implementado** - apenas mencionado em 1 template
- ❌ Sem definição clara de responsabilidades
- ❌ Não há verificações em views ou decorators
- **RECOMENDAÇÃO:** Remover do template ou implementar completamente

---

### 8. **Pastor**
**Status:** ❌ Apenas mencionado em template  
**Uso:** Não especificado  
**Localização no código:**
- `configuracao/templates/configuracao/perfil/meu_perfil.html` (linha 138)

**Permissões (esperadas):**
- ⚠️ Não especificadas
- Aparentemente pode: ver configuração da ministério

**Hierarquia:** ❓ Indefinida (deveria ser nível 2, abaixo de Admin)

**Análise:**
- ❌ **Não implementado** - apenas mencionado em 1 template
- ❌ Sem definição clara de responsabilidades
- ❌ Falta implementação em views/decorators
- **RECOMENDAÇÃO:** Implementar ou remover

---

## ⚠️ PROBLEMAS IDENTIFICADOS

### 1. **Inconsistência de Nomenclatura**
- ❌ "Admin Ministerio" (sem acento, mas em português)
- ❌ "Lideranca Financeira" (sem acento)
- ❌ "Superintendentes" (plural) vs outros no singular

**Impacto:** Médio - dificulta manutenção  
**Recomendação:** Padronizar para `snake_case` ou manter português sem acentos

---

### 2. **Grupos Fantasma (mencionados mas não criados)**
Grupos mencionados no código mas **podem não existir no banco de dados:**
- ❌ Tesoureiro
- ❌ Lider Igreja  
- ❌ Gestor
- ❌ Pastor

**Impacto:** Alto - código pode falhar silenciosamente  
**Recomendação:** Criar migration ou fixture para garantir existência

---

### 3. **Falta de Grupo "Membro" Básico**
**Problema:** Não há grupo para membros comuns (sem função administrativa)

**Impacto:** Alto - usuários sem grupo veem página "Aguardando Permissões"  
**Recomendação:** Criar grupo "Membro" com permissões básicas:
- Ver próprio perfil
- Ver eventos públicos
- Ver avisos/notificações

---

### 4. **Permissões Não Granulares**
**Problema:** `Admin Ministerio` tem TODAS as permissões (comando python)

**Impacto:** Médio - viola princípio de menor privilégio  
**Recomendação:**
- Admin Ministerio deve ter permissões específicas, não todas
- Permissões sensíveis (ex: deletar ministério) devem ser separadas

---

### 5. **Falta de Hierarquia Clara**
**Problema:** Não há herança de permissões (ex: Admin não herda permissões de Tesoureiro)

**Impacto:** Médio - pode exigir duplicação de código  
**Recomendação:** Implementar verificação hierárquica:
```python
HIERARQUIA_GRUPOS = {
    'Admin Ministerio': ['Tesoureiro', 'Lideranca Financeira', 'Membro'],
    'Pastor': ['Lideranca Financeira', 'Membro'],
    # ...
}
```

---

### 6. **Documentação Inexistente**
**Problema:** Nenhum arquivo documenta:
- Quais grupos existem
- Hierarquia entre eles
- Permissões específicas
- Como criar novos grupos

**Impacto:** Alto - dificulta onboarding e manutenção  
**Recomendação:** Criar `PERMISSIONS.md` documentando estrutura completa

---

## 💡 COMPARAÇÃO COM PADRÕES PROFISSIONAIS

### ✅ Pontos Positivos

1. **RBAC Implementado**
   - Sistema usa grupos para controle de acesso (padrão da indústria)
   
2. **Separação Admin Sistema vs Admin Ministerio**
   - Superuser (gereigreja@gmail.com) para manutenção do sistema
   - Admin Ministerio para administração do cliente

3. **Decorators de Permissão**
   - `superintendente_required()`, `secretaria_ebd_required()`
   - Facilita manutenção e auditoria

4. **Template Tag para Verificação**
   - `{% load grupo_tags %}` → `user|has_group:"Admin Ministerio"`
   - Facilita controle em templates

5. **Multi-tenant Validado**
   - Usuários vinculados a ministérios específicos
   - Isolamento entre clientes garantido

### ⚠️ Áreas de Melhoria

1. **Falta Grupo de Membro Básico**
   - Todo usuário deveria ter grupo "Membro" por padrão

2. **Implementação Parcial**
   - Grupos mencionados mas não usados (Gestor, Pastor)

3. **Permissões Muito Amplas**
   - Admin Ministerio com TODAS as permissões

4. **Falta Audit Trail**
   - Não há registro de mudanças de grupos/permissões

5. **Nomes Inconsistentes**
   - Mistura de singular/plural, com/sem acentos

---

## 📋 HIERARQUIA RECOMENDADA

```
┌─────────────────────────────────────────────────────────────┐
│                      SUPERUSER                              │
│              (gereigreja@gmail.com)                         │
│              Acesso TOTAL ao sistema                        │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴──────────────────┐
        │                                      │
┌───────▼──────────┐                  ┌───────▼──────────┐
│ Admin Ministerio │                  │ Pastor (Líder)   │
│  NÍVEL 1         │                  │  NÍVEL 2         │
│                  │                  │                  │
│ • Gerenciar      │                  │ • Ver dados      │
│   usuários       │                  │   sensíveis      │
│ • Configurar     │                  │ • Aprovar        │
│   ministério     │                  │   decisões       │
│ • Gerenciar      │                  │ • Visualizar     │
│   assinatura     │                  │   finanças       │
│ • Todas igrejas  │                  │                  │
└──────────────────┘                  └──────────────────┘
        │                                      │
        └──────────────┬───────────────────────┘
                       │
        ┌──────────────┴──────────────┬──────────────────┐
        │                             │                  │
┌───────▼──────────┐      ┌──────────▼──────────┐  ┌────▼────────┐
│ Tesoureiro       │      │ Superintendente EBD │  │ Secretaria  │
│  NÍVEL 3         │      │  NÍVEL 3            │  │  NÍVEL 3    │
│                  │      │                     │  │             │
│ • CRUD finanças  │      │ • CRUD EBD          │  │ • CRUD      │
│ • Ver relatórios │      │ • Gerenciar alunos  │  │   membros   │
│ • Própria igreja │      │ • Relatórios EBD    │  │ • CRUD      │
│                  │      │                     │  │   eventos   │
└──────────────────┘      └─────────────────────┘  └─────────────┘
        │                             │                  │
        └──────────────┬──────────────┴──────────────────┘
                       │
        ┌──────────────┴──────────────┬──────────────────┐
        │                             │                  │
┌───────▼──────────┐      ┌──────────▼──────────┐  ┌────▼────────┐
│ Líder Igreja     │      │ Líder Célula        │  │ Professor   │
│  NÍVEL 4         │      │  NÍVEL 4            │  │ EBD         │
│                  │      │                     │  │  NÍVEL 4    │
│ • Ver finanças   │      │ • CRUD grupo casa   │  │             │
│   própria igreja │      │ • Ver seu grupo     │  │ • Ver       │
│ • Ver membros    │      │                     │  │   próprias  │
│                  │      │                     │  │   turmas    │
└──────────────────┘      └─────────────────────┘  └─────────────┘
        │                             │                  │
        └──────────────┬──────────────┴──────────────────┘
                       │
               ┌───────▼──────────┐
               │ Membro           │
               │  NÍVEL 5 (Base)  │
               │                  │
               │ • Ver perfil     │
               │ • Ver eventos    │
               │ • Alterar senha  │
               │ • Receber avisos │
               └──────────────────┘
```

---

## ✅ RECOMENDAÇÕES PRIORITÁRIAS

### 1. **CRÍTICO - Criar Grupo "Membro"** 
**Prioridade:** 🔴 ALTA

**Ação:**
```python
# Migration ou fixture
Group.objects.get_or_create(name='Membro')
```

**Permissões:**
- `view_perfil_proprio`
- `change_perfil_proprio`
- `view_evento_publico`
- `view_notificacao_propria`

**Justificativa:** Todo usuário deve ter um grupo base. Evita página "Aguardando Permissões" para membros comuns.

---

### 2. **CRÍTICO - Documentar Grupos Existentes**
**Prioridade:** 🔴 ALTA

**Ação:** Criar `docs/PERMISSIONS.md` com:
- Lista de todos os grupos
- Hierarquia visual
- Permissões específicas de cada grupo
- Exemplos de uso

---

### 3. **IMPORTANTE - Implementar Grupos Fantasma**
**Prioridade:** 🟡 MÉDIA

**Ação:** Decidir para cada grupo mencionado:
- **Implementar completamente:** Criar grupo, atribuir permissões, adicionar verificações
- **Remover menções:** Limpar código que referencia grupos não usados

**Grupos afetados:** Tesoureiro, Lider Igreja, Gestor, Pastor

---

### 4. **IMPORTANTE - Padronizar Nomenclatura**
**Prioridade:** 🟡 MÉDIA

**Ação:** Escolher um padrão e aplicar:
- **Opção A:** Snake case em inglês: `admin_ministry`, `treasurer`, `pastor`
- **Opção B:** Português sem acentos, singular: `Admin Ministerio`, `Tesoureiro`, `Pastor`
- **Opção C (Recomendado):** Português sem acentos, consistente: `Admin Ministerio`, `Superintendente`, `Secretaria`

**Migração:** Criar data migration para renomear grupos existentes

---

### 5. **DESEJÁVEL - Refinar Permissões Admin Ministerio**
**Prioridade:** 🟢 BAIXA

**Ação:** Substituir "todas as permissões" por lista específica:
```python
PERMISSOES_ADMIN_MINISTERIO = [
    'secretaria.view_pessoa',
    'secretaria.add_pessoa',
    'secretaria.change_pessoa',
    'secretaria.delete_pessoa',
    'configuracao.change_ministerio',
    'contas.change_user_groups',
    # ... demais permissões necessárias
]
```

**Justificativa:** Segurança (menor privilégio), auditoria, compliance

---

### 6. **DESEJÁVEL - Audit Log de Mudanças**
**Prioridade:** 🟢 BAIXA

**Ação:** Implementar registro de:
- Quem adicionou/removeu usuário de grupo
- Quando ocorreu a mudança
- Justificativa (campo opcional)

**Ferramentas:** `django-auditlog`, `django-simple-history`

---

## 📦 PLANO DE AÇÃO SUGERIDO

### Fase 1: Correções Críticas (1-2 horas)
- [ ] Criar grupo "Membro" com permissões básicas
- [ ] Atribuir grupo "Membro" a todos usuários sem grupo
- [ ] Documentar grupos existentes em `docs/PERMISSIONS.md`

### Fase 2: Padronização (2-4 horas)
- [ ] Decidir padrão de nomenclatura
- [ ] Criar data migration para renomear grupos
- [ ] Atualizar código para usar nomes padronizados
- [ ] Testar em staging

### Fase 3: Implementação Completa (4-8 horas)
- [ ] Decidir destino dos grupos fantasma (implementar ou remover)
- [ ] Se implementar: criar grupos, permissões, decorators, testes
- [ ] Se remover: limpar menções do código
- [ ] Atualizar documentação

### Fase 4: Melhorias (8+ horas)
- [ ] Refinar permissões de Admin Ministerio
- [ ] Implementar audit log
- [ ] Criar hierarquia de permissões (herança)
- [ ] Adicionar testes automatizados de permissões

---

## 📚 REFERÊNCIAS E BOAS PRÁTICAS

### Sistemas de Igreja Similares
1. **Planning Center** (market leader)
   - Grupos: Administrator, Leader, Member, Viewer
   - Hierarquia clara com herança

2. **Elvanto** (Austrália)
   - 6 níveis de permissão
   - Granularidade por módulo

3. **Church Community Builder** (CCB)
   - Grupos customizáveis
   - Templates de permissões por função

### Princípios RBAC (NIST)
- ✅ **Separation of Duties:** Funções sensíveis em grupos separados
- ✅ **Least Privilege:** Mínimas permissões necessárias
- ⚠️ **Data Abstraction:** Permissões por função, não por usuário (melhorar)
- ⚠️ **Hierarchical RBAC:** Herança de permissões (não implementado)

### Django Best Practices
- ✅ Usar `Group` e `Permission` nativos do Django
- ✅ Usar decorators para views (`@login_required`, `@permission_required`)
- ✅ Template tags para controle de exibição
- ⚠️ Evitar hardcoded permission checks (usar constants)
- ⚠️ Documentar permissões customizadas

---

## 🎯 CONCLUSÃO

O sistema GereIgreja possui uma **estrutura RBAC funcional mas incompleta**:

### ✅ Está Funcionando
- Admin Ministerio bem implementado
- Módulos EBD com grupos específicos
- Separação básica entre superuser e admins de clientes

### ⚠️ Precisa Atenção
- Falta grupo "Membro" para usuários comuns
- Grupos mencionados mas não implementados (Pastor, Gestor, Tesoureiro, Lider Igreja)
- Nomenclatura inconsistente
- Documentação inexistente

### 🚀 Recomendação Final
**Executar Fase 1 imediatamente** (criar grupo Membro + documentar).  
**Planejar Fase 2 e 3** para próximo sprint (padronização + implementação completa).  
**Fase 4 como melhoria contínua** (audit log, hierarquia, refinamento).

**Risco de não fazer:** Usuários sem grupo ficam bloqueados, código mantém referências a grupos inexistentes, dificuldade de manutenção e onboarding.

**Benefício de fazer:** Sistema profissional, auditável, escalável e alinhado com padrões de mercado.

---

**Elaborado por:** GitHub Copilot (Claude Sonnet 4.5)  
**Data:** 09/02/2026  
**Versão do Documento:** 1.0
