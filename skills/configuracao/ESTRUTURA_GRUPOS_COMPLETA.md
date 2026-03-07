# 🏗️ Estrutura Completa de Grupos e Permissões - Sistema GereIgreja

**Data:** 10/02/2026  
**Versão:** 2.0 (Revisada com base em auditoria e análise de módulos)

---

## 📊 VISÃO GERAL DO SISTEMA

### Módulos Implementados
1. **Secretaria** - Cadastro de pessoas, famílias, histórico
2. **Financeiro** - Receitas, despesas, contas, relatórios
3. **Eventos** - Organização de eventos, inscrições, presença
4. **Comunicação** - E-mails, SMS, notificações
5. **Escola Bíblica (EBD)** - Turmas, alunos, professores, aulas
6. **Configuração** - Ministérios, igrejas, usuários, permissões
7. **Suporte** - Tickets de atendimento, base de conhecimento
8. **Agenda** - Compromissos e calendário

### Arquitetura Multi-Tenant
```
MINISTÉRIO (tenant)
├─ Igreja Sede
├─ Igrejas Regionais
└─ Congregações Locais
    └─ Escola Bíblica Dominical
```

---

## 🎯 ESTRUTURA DE GRUPOS PROPOSTA

### 📋 Nomenclatura Padronizada

**Princípios:**
- ✅ Singular (não plural)
- ✅ Português sem acentos
- ✅ Descritivo e intuitivo
- ✅ Diferencia claramente escopo (Ministerial vs Local)

**Mudanças propostas:**
| Nome Atual | Nome Proposto | Motivo |
|------------|---------------|--------|
| Superintendentes | Superintendente EBD | Singular + clareza |
| Lider Igreja | Pastor Regional | Mais descritivo |
| Secretario | Secretario Local | Diferencia de ministerial |

---

## 🏛️ HIERARQUIA COMPLETA

```
┌─────────────────────────────────────────────────────────────────┐
│                  NÍVEL 0: SISTEMA                               │
│                  SUPERUSER                                      │
│              (gereigreja@gmail.com)                             │
│         Acesso ao Django Admin e Infraestrutura                 │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────▼─────────────────────┐
        │        NÍVEL 1: ADMINISTRATIVO            │
        │        Admin Ministerio                   │
        │    (Administrador Geral do Cliente)       │
        │                                           │
        │  • Gerenciar TUDO do ministério           │
        │  • Todas as igrejas (sede + regionais)    │
        │  • Gerenciar usuários e permissões        │
        │  • Configurar assinatura                  │
        │  • Acessar dashboard de métricas          │
        └───────────────────┬───────────────────────┘
                            │
        ┌───────────────────┴─────────────────────────────┐
        │           NÍVEL 2: LIDERANÇA MINISTERIAL        │
        │     (Visão consolidada de todas as igrejas)     │
        │                                                 │
        │  ┌─────────────────────┐  ┌────────────────────┤
        │  │ Lideranca Secretaria │  │ Lideranca Financeira│
        │  │ (Secretário Geral)   │  │ (Tesoureiro Geral) │
        │  │                      │  │                    │
        │  │ • Todas igrejas      │  │ • Todas igrejas    │
        │  │ • Relatórios         │  │ • Consolidação     │
        │  │   consolidados       │  │   financeira       │
        │  │ • Gerenciar cargos   │  │ • Aprovações       │
        │  └──────────────────────┘  └────────────────────┘
        └───────────────────┬─────────────────────────────┘
                            │
        ┌───────────────────▼─────────────────────────────┐
        │          NÍVEL 3: LIDERANÇA REGIONAL            │
        │      (Supervisiona várias congregações)         │
        │                                                 │
        │         ┌─────────────────────┐                │
        │         │  Pastor Regional    │                │
        │         │                     │                │
        │         │ • Igrejas regionais │                │
        │         │ • Supervisão geral  │                │
        │         │ • Relatórios        │                │
        │         │   agregados         │                │
        │         └─────────────────────┘                │
        └───────────────────┬─────────────────────────────┘
                            │
        ┌───────────────────▼─────────────────────────────┐
        │         NÍVEL 4: OPERACIONAL LOCAL              │
        │          (Uma igreja específica)                │
        │                                                 │
        │  ┌──────────────┐  ┌──────────────┐  ┌────────┤
        │  │ Secretario   │  │ Tesoureiro   │  │ Super- │
        │  │ Local        │  │ Local        │  │ intend.│
        │  │              │  │              │  │ EBD    │
        │  │ • CRUD       │  │ • Finanças   │  │        │
        │  │   membros    │  │   da igreja  │  │ • CRUD │
        │  │ • Relatórios │  │ • Caixa      │  │   EBD  │
        │  │   locais     │  │ • Relatórios │  │ • Aulas│
        │  └──────────────┘  └──────────────┘  └────────┘
        └───────────────────┬─────────────────────────────┘
                            │
        ┌───────────────────▼─────────────────────────────┐
        │        NÍVEL 5: EQUIPES E AUXILIARES            │
        │            (Funções específicas)                │
        │                                                 │
        │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┤
        │  │ Equipe  │ │ Equipe  │ │ Equipe  │ │Profes-│
        │  │ Eventos │ │ Mídia   │ │Recepção │ │sor EBD│
        │  │         │ │         │ │         │ │       │
        │  │ • Criar │ │• Produ- │ │• Aten-  │ │• Dar  │
        │  │   event.│ │  ção AV │ │  dimen- │ │  aulas│
        │  │ • Inscr │ │• Grav-  │ │  to     │ │• Freq.│
        │  └─────────┘ └─────────┘ └─────────┘ └───────┘
        │                                                 │
        │         ┌─────────────────────┐                │
        │         │  Secretaria EBD     │                │
        │         │                     │                │
        │         │ • Auxiliar EBD      │                │
        │         │ • Presença          │                │
        │         │ • Relatórios        │                │
        │         └─────────────────────┘                │
        └───────────────────┬─────────────────────────────┘
                            │
        ┌───────────────────▼─────────────────────────────┐
        │             NÍVEL 6: BASE                       │
        │             Membro Comum                        │
        │                                                 │
        │  • Ver próprio perfil                           │
        │  • Editar dados pessoais                        │
        │  • Inscrever-se em eventos                      │
        │  • Ver notificações                             │
        │  • Ver eventos públicos                         │
        └─────────────────────────────────────────────────┘
```

---

## 📝 GRUPOS DETALHADOS

### 1️⃣ Admin Ministerio
**Escopo:** Ministerial (todas as igrejas)  
**Descrição:** Administrador geral do cliente (SaaS tenant)

**Responsabilidades:**
- Gerenciar todas as igrejas do ministério
- Adicionar/remover usuários
- Atribuir grupos e permissões
- Gerenciar assinatura e pagamento
- Configurar integrações (Cloudinary, e-mail)
- Acessar dashboard de métricas do admin
- Ver relatórios consolidados de TODOS os módulos

**Permissões (Módulos):**
- ✅ Secretaria: `view/add/change/delete` pessoa, cargo, familia
- ✅ Financeiro: `view/add/change/delete` transacao, categoria, conta
- ✅ Eventos: `view/add/change/delete` evento, inscricao
- ✅ Comunicação: `view/add/change/delete` mensagem, notificacao
- ✅ EBD: `view/add/change/delete` turma, aluno, aula
- ✅ Configuração: `change` ministerio, `view/add/change/delete` igreja, usuario
- ✅ Suporte: `view/add/change` ticket
- ✅ Agenda: `view/add/change/delete` compromisso

**Não pode:**
- ❌ Acessar Django Admin (apenas superuser)
- ❌ Ver dados de outros ministérios (isolamento multi-tenant)

---

### 2️⃣ Lideranca Secretaria
**Escopo:** Ministerial (todas as igrejas)  
**Descrição:** Secretário geral do ministério

**Responsabilidades:**
- Coordenar secretarias de todas as igrejas
- **Visualizar e alterar cadastros de membros de todas as igrejas**
- Aprovar transferências de membros entre igrejas
- Gerar relatórios consolidados de membros
- Padronizar processos de secretaria
- **Futuramente: Painel ministerial para visão consolidada**

**Permissões (Módulos):**
- ✅ Secretaria: `view/add/change/delete` pessoa, familia, tag
  - Filtro: TODAS as igrejas do ministério
  - `view` cargo (não cria/edita - cargos são locais)
- ✅ Eventos: `view` evento (para saber participação de membros)
- ✅ Comunicação: `view/add` notificacao, `add` mensagem (avisos gerais)
- ✅ EBD: `view` turma, aluno (visão geral)
- ✅ Agenda: `view` compromisso

**Não pode:**
- ❌ Gerenciar finanças
- ❌ Gerenciar usuários/permissões
- ❌ Alterar configurações do ministério
- ❌ Criar/editar cargos (são gerenciados localmente pelo Pastor/Secretário Local)
- ❌ Inserir transações financeiras em igrejas locais

---

### 3️⃣ Lideranca Financeira
**Escopo:** Ministerial (todas as igrejas)  
**Descrição:** Tesoureiro geral do ministério

**Responsabilidades:**
- Consolidação financeira de todas as igrejas (visualizar relatórios)
- Aprovar grandes despesas
- Criar categorias financeiras globais
- Gerar relatórios financeiros consolidados
- Auditar lançamentos de tesoureiros locais
- **Futuramente: Painel ministerial financeiro para visão consolidada**

**Permissões (Módulos):**
- ✅ Financeiro: 
  - `view` transacao, conta (TODAS as igrejas - apenas visualização)
  - `add/change/delete` categoria (criar categorias globais)
  - Filtro: TODAS as igrejas do ministério
- ✅ Secretaria: `view` pessoa (para ver dzimos por membro)
- ✅ Eventos: `view` evento (custos de eventos)
- ✅ Comunicação: `view/add` notificacao

**Não pode:**
- ❌ Gerenciar membros
- ❌ Gerenciar usuários
- ❌ **Inserir dízimos/ofertas em igrejas locais** (tesoureiro local faz isso)
- ❌ **Lançar receitas/despesas de igrejas locais** (apenas visualizar e auditar)
- ❌ Deletar categorias globais criadas por Admin

**Nota:** O Tesoureiro Geral **NÃO lança transações**, apenas:
- Cria categorias que todos usam
- Visualiza e audita lançamentos
- Gera relatórios consolidados

---

### 4️⃣ Pastor Regional
**Escopo:** Regional (várias igrejas subordinadas)  
**Descrição:** Líder que supervisiona grupo de igrejas

**Responsabilidades:**
- Supervisionar pastores locais
- Ver estatísticas agregadas das igrejas da região
- Aprovar eventos regionais
- Acompanhar crescimento das congregações

**Permissões (Módulos):**
- ✅ Secretaria: `view/add/change` pessoa
  - `view` cargo (apenas visualização)
  - Filtro: Igrejas da sua região
- ✅ Financeiro: `view` transacao, categoria, conta
  - Filtro: Igrejas da sua região (somente visualização)
- ✅ Eventos: `view/add/change` evento
- ✅ Comunicação: `view/add` mensagem, notificacao
- ✅ EBD: `view` turma, aluno, aula
- ✅ Agenda: `view/add/change` compromisso

**Não pode:**
- ❌ Gerenciar cargos (são gerenciados pelo Pastor ou Secretário Local de cada igreja)
- ❌ Lançar transações financeiras
- ❌ Gerenciar usuários

**Diferença para Liderança:**
- Supervisiona REGIÃO, não ministério inteiro
- Não cria categorias globais financeiras
- Não gerencia cargos (responsabilidade local)
- Não gerencia usuários

---

### 5️⃣ Secretario Local
**Escopo:** Local (uma igreja)  
**Descrição:** Secretário de uma congregação específica

**Responsabilidades:**
- Cadastrar e editar membros da igreja
- **Gerenciar cargos locais da igreja** (Diácono, Presbítero, Líder de Louvor, etc.)
- Gerenciar famílias
- Registrar visitas e acompanhamentos
- Atualizar status de membros (ativo/inativo)
- Gerar relatórios locais

**Permissões (Módulos):**
- ✅ Secretaria: `view/add/change/delete` pessoa, familia, tag, cargo
  - Filtro: APENAS sua igreja (igreja_ativa)
- ✅ Eventos: `view` evento
- ✅ Comunicação: `view` notificacao, `add` mensagem (avisos da igreja)
- ✅ EBD: `view` turma, aluno
- ✅ Agenda: `view/add/change` compromisso

**Não pode:**
- ❌ Ver/editar membros de outras igrejas
- ❌ Gerenciar finanças
- ❌ Gerenciar usuários
- ❌ Ver cargos de outras igrejas (isolamento local)

**Nota:** Cargos são **locais** (cada igreja gerencia os seus). Futuramente pode haver cargos ministeriais separados.
- ❌ Gerenciar finanças
- ❌ Gerenciar usuários
- ❌ Criar cargos (apenas admin pode)

---

### 6️⃣ Tesoureiro Local
**Escopo:** Local (uma igreja)  
**Descrição:** Tesoureiro de uma congregação específica

**Responsabilidades:**
- Lançar receitas e despesas da igreja
- Gerenciar contas bancárias locais
- Fazer fechamento de caixa
- Gerar relatórios financeiros locais

**Permissões (Módulos):**
- ✅ Financeiro: `view/add/change/delete` transacao, conta
  - `view` categoria (usa categorias globais, não cria)
  - Filtro: APENAS sua igreja
-✅ Secretaria: `view` pessoa (para vincular dízimos)
- ✅ Comunicação: `view` notificacao
- ✅ Agenda: `view` compromisso

**Não pode:**
- ❌ Ver finanças de outras igrejas
- ❌ Criar categorias financeiras
- ❌ Aprovar transações acima de limite (precisa de Liderança)

---

### 7️⃣ Superintendente EBD
**Escopo:** Local (EBD de uma igreja)  
**Descrição:** Responsável pela Escola Bíblica

**Responsabilidades:**
- Gerenciar turmas e professores
- Planejar aulas e conteúdo
- Gerenciar matrículas de alunos
- Gerar relatórios de frequência
- Coordenar professores

**Permissões (Módulos):**
- ✅ EBD: `view/add/change/delete` turma, aluno, aula, frequencia, professor
  - Filtro: APENAS EBD da sua igreja
- ✅ Secretaria: `view` pessoa (para matricular alunos)
- ✅ Comunicação: `view/add` mensagem (avisos da EBD)
- ✅ Agenda: `view/add/change` compromisso

**Não pode:**
- ❌ Gerenciar turmas de outras igrejas
- ❌ Acessar finanças
- ❌ Alterar dados de membros

---

### 8️⃣ Equipe de Eventos
**Escopo:** Local (uma igreja)  
**Descrição:** Organiza eventos da congregação

**Responsabilidades:**
- Criar e editar eventos
- Gerenciar inscrições
- Controlar presença
- Planejar logística de eventos

**Permissões (Módulos):**
- ✅ Eventos: `view/add/change` evento, inscricao
  - Filtro: Eventos da sua igreja
  - Não pode: `delete` evento (somente admin)
- ✅ Secretaria: `view` pessoa (para inscrições)
- ✅ Comunicação: `add` mensagem (divulgar eventos)
- ✅ Agenda: `view/add` compromisso

**Não pode:**
- ❌ Gerenciar eventos de outras igrejas
- ❌ Deletar eventos (segurança histórico)

---

### 9️⃣ Equipe de Mídia
**Escopo:** Local (uma igreja)  
**Descrição:** Produção audiovisual e comunicação

**Responsabilidades:**
- Gravar e transmitir cultos
- Produzir conteúdo para redes sociais
- Gerenciar arquivos de mídia
- Apoio técnico em eventos

**Permissões (Módulos):**
- ✅ Comunicação: `view/add/change` midia (upload de vídeos/fotos)
  - `view` mensagem
- ✅ Eventos: `view` evento (saber programação)
- ✅ Agenda: `view` compromisso

**Não pode:**
- ❌ Acessar dados de membros
- ❌ Acessar finanças
- ❌ Enviar mensagens em massa (apenas admin)

---

### 🔟 Equipe de Recepção
**Escopo:** Local (uma igreja)  
**Descrição:** Atendimento e recepção de visitantes

**Responsabilidades:**
- Cadastrar visitantes
- Registrar presença em cultos
- Fazer acompanhamento inicial
- Direcionar dúvidas

**Permissões (Módulos):**
- ✅ Secretaria: `view/add` pessoa (tipo: visitante)
  - `view` lista de membros (para identificar)
  - Filtro: Apenas visitantes e congregados
- ✅ Eventos: `view/add` inscricao (inscrever visitantes)
- ✅ Comunicação: `view` notificacao

**Não pode:**
- ❌ Editar dados de membros batizados
- ❌ Alterar status de pessoas
- ❌ Acessar finanças

---

### 1️⃣1️⃣ Professor EBD
**Escopo:** Local (turma específica da EBD)  
**Descrição:** Professor de turma da Escola Bíblica

**Responsabilidades:**
- Dar aulas da sua turma
- Registrar frequência
- Planejar conteúdo de aulas
- Acompanhar alunos

**Permissões (Módulos):**
- ✅ EBD: `view/add/change` aula, frequencia
  - Filtro: APENAS turmas que leciona
  - `view` aluno (da sua turma)
- ✅ Secretaria: `view` pessoa (dados dos alunos)
- ✅ Comunicação: `view` notificacao

**Não pode:**
- ❌ Gerenciar turmas
- ❌ Matricular alunos
- ❌ Ver outras turmas

---

### 1️⃣2️⃣ Secretaria EBD
**Escopo:** Local (EBD de uma igreja)  
**Descrição:** Auxiliar administrativo da EBD

**Responsabilidades:**
- Registrar presença de alunos
- Gerar relatórios de frequência
- Apoiar superintendente
- Organizar materiais

**Permissões (Módulos):**
- ✅ EBD: `view/add` frequencia
  - `view` turma, aluno, aula
  - Filtro: EBD da sua igreja
- ✅ Secretaria: `view` pessoa
- ✅ Comunicação: `view` notificacao

**Não pode:**
- ❌ Gerenciar turmas
- ❌ Planejar aulas
- ❌ Matricular alunos

---

### 1️⃣3️⃣ Membro Comum
**Escopo:** Sistema (próprios dados)  
**Descrição:** Membro regular da igreja

**Responsabilidades:**
- Ver e editar próprio perfil
- Inscrever-se em eventos
- Ver comunicados
- Alterar senha

**Permissões (Módulos):**
- ✅ Secretaria: `view/change` própria pessoa
  - Não pode alterar: status, cargo, familia (pede ao secretário)
- ✅ Eventos: `view` evento, `add` inscricao (própria)
- ✅ Comunicação: `view` notificacao própria
- ✅ Agenda: `view` compromisso público
- ✅ Contas: `change` própria senha

**Não pode:**
- ❌ Ver dados de outros membros
- ❌ Acessar finanças
- ❌ Acessar administrativo

---

## 🔧 IMPLEMENTAÇÃO

### Passo 1: Renomear Grupos Existentes

**Script de renomeação (migration):**

```python
# contas/migrations/XXXX_renomear_grupos.py

from django.db import migrations

def renomear_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    
    renomeacoes = {
        'Superintendentes': 'Superintendente EBD',
        'Lider Igreja': 'Pastor Regional',
        'Secretario': 'Secretario Local',
    }
    
    for antigo, novo in renomeacoes.items():
        try:
            grupo = Group.objects.get(name=antigo)
            grupo.name = novo
            grupo.save()
            print(f"✅ Renomeado: {antigo} → {novo}")
        except Group.DoesNotExist:
            print(f"⚠️  {antigo} não existe, criando {novo}")
            Group.objects.create(name=novo)

def reverter(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    
    reverter_nomes = {
        'Superintendente EBD': 'Superintendentes',
        'Pastor Regional': 'Lider Igreja',
        'Secretario Local': 'Secretario',
    }
    
    for atual, original in reverter_nomes.items():
        try:
            grupo = Group.objects.get(name=atual)
            grupo.name = original
            grupo.save()
        except Group.DoesNotExist:
            pass

class Migration(migrations.Migration):
    dependencies = [
        ('contas', 'XXXX_ultima_migration'),
    ]
    
    operations = [
        migrations.RunPython(renomear_grupos, reverter),
    ]
```

---

### Passo 2: Criar Arquivo de Constantes

**Arquivo: `contas/constants.py`**

```python
\"\"\"
Constantes de grupos e permissões do sistema GereIgreja.
Centraliza nomes de grupos para evitar strings hardcoded.
\"\"\"

# ===================================
# GRUPOS DO SISTEMA
# ===================================

# Nível 1: Administrativo
ADMIN_MINISTERIO = 'Admin Ministerio'

# Nível 2: Liderança Ministerial
LIDERANCA_SECRETARIA = 'Lideranca Secretaria'
LIDERANCA_FINANCEIRA = 'Lideranca Financeira'

# Nível 3: Liderança Regional
PASTOR_REGIONAL = 'Pastor Regional'

# Nível 4: Operacional Local
SECRETARIO_LOCAL = 'Secretario Local'
TESOUREIRO_LOCAL = 'Tesoureiro'
SUPERINTENDENTE_EBD = 'Superintendente EBD'

# Nível 5: Equipes e Auxiliares
EQUIPE_EVENTOS = 'Equipe de Eventos'
EQUIPE_MIDIA = 'Equipe de Mídia'
EQUIPE_RECEPCAO = 'Equipe de Recepção'
PROFESSOR_EBD = 'Professores EBD'
SECRETARIA_EBD = 'Secretaria EBD'

# Nível 6: Base
MEMBRO_COMUM = 'Membro Comum'

# ===================================
# HIERARQUIAS (para verificações)
# ===================================

GRUPOS_ADMIN = [ADMIN_MINISTERIO]

GRUPOS_LIDERANCA_MINISTERIAL = GRUPOS_ADMIN + [
    LIDERANCA_SECRETARIA,
    LIDERANCA_FINANCEIRA,
]

GRUPOS_LIDERANCA = GRUPOS_LIDERANCA_MINISTERIAL + [
    PASTOR_REGIONAL,
]

GRUPOS_OPERACIONAL = GRUPOS_LIDERANCA + [
    SECRETARIO_LOCAL,
    TESOUREIRO_LOCAL,
    SUPERINTENDENTE_EBD,
]

GRUPOS_TODOS = GRUPOS_OPERACIONAL + [
    EQUIPE_EVENTOS,
    EQUIPE_MIDIA,
    EQUIPE_RECEPCAO,
    PROFESSOR_EBD,
    SECRETARIA_EBD,
    MEMBRO_COMUM,
]

# ===================================
# HELPER FUNCTIONS
# ===================================

def user_tem_grupo(user, nome_grupo):
    \"\"\"Verifica se usuário pertence a um grupo específico.\"\"\"
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=nome_grupo).exists()

def user_tem_qualquer_grupo(user, lista_grupos):
    \"\"\"Verifica se usuário pertence a qualquer grupo da lista.\"\"\"
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=lista_grupos).exists()

def user_is_admin(user):
    \"\"\"Verifica se é Admin Ministerio.\"\"\"
    return user.is_superuser or user_tem_grupo(user, ADMIN_MINISTERIO)

def user_is_lideranca(user):
    \"\"\"Verifica se é qualquer nível de liderança.\"\"\"
    return user_tem_qualquer_grupo(user, GRUPOS_LIDERANCA)

def user_is_lideranca_secretaria(user):
    \"\"\"Verifica se é Liderança Secretaria ou superior.\"\"\"
    return user_tem_qualquer_grupo(user, [ADMIN_MINISTERIO, LIDERANCA_SECRETARIA])

def user_is_lideranca_financeira(user):
    \"\"\"Verifica se é Liderança Financeira ou superior.\"\"\"
    return user_tem_qualquer_grupo(user, [ADMIN_MINISTERIO, LIDERANCA_FINANCEIRA])

def user_pode_gerenciar_secretaria(user):
    \"\"\"Verifica se pode gerenciar secretaria (ministerial ou local).\"\"\"
    return user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        LIDERANCA_SECRETARIA,
        SECRETARIO_LOCAL,
    ])

def user_pode_gerenciar_financeiro(user):
    \"\"\"Verifica se pode gerenciar financeiro (ministerial ou local).\"\"\"
    return user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        LIDERANCA_FINANCEIRA,
        TESOUREIRO_LOCAL,
    ])

def user_pode_gerenciar_ebd(user):
    \"\"\"Verifica se pode gerenciar EBD.\"\"\"
    return user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        LIDERANCA_SECRETARIA,
        SUPERINTENDENTE_EBD,
    ])

def user_pode_ver_financeiro(user):
    \"\"\"Verifica se pode VER finanças (inclui Pastor Regional).\"\"\"
    return user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        LIDERANCA_FINANCEIRA,
        PASTOR_REGIONAL,
        TESOUREIRO_LOCAL,
    ])

def user_escopo_ministerial(user):
    \"\"\"
    Retorna True se usuário tem escopo ministerial (todas as igrejas).
    False se é local (precisa filtrar por igreja_ativa).
    \"\"\"
    return user_tem_qualquer_grupo(user, GRUPOS_LIDERANCA_MINISTERIAL)
```

---

### Passo 3: Atualizar Código Existente

**Substituir verificações hardcoded:**

```python
# ANTES (em vários arquivos)
if request.user.groups.filter(name='Admin Ministerio').exists():
    # ...

# DEPOIS
from contas.constants import user_is_admin

if user_is_admin(request.user):
    # ...
```

**Atualizar decorators:**

```python
# core/decorators.py

from contas.constants import SUPERINTENDENTE_EBD, SECRETARIA_EBD

def superintendente_required(view_func):
    \"\"\"Permite Admin ou Superintendente EBD.\"\"\"
    return user_passes_test(
        lambda u: u.is_superuser or u.groups.filter(name=SUPERINTENDENTE_EBD).exists()
    )(view_func)

def secretaria_ebd_required(view_func):
    \"\"\"Permite Admin, Superintendente ou Secretaria EBD.\"\"\"
    return user_passes_test(
        lambda u: u.is_superuser or u.groups.filter(
            name__in=[SUPERINTENDENTE_EBD, SECRETARIA_EBD]
        ).exists()
    )(view_func)
```

---

### Passo 4: Configurar Permissões dos Grupos

**Comando: `contas/management/commands/configurar_permissoes_grupos.py`**

```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from contas.constants import *

class Command(BaseCommand):
    help = 'Configura permissões de todos os grupos do sistema'

    def handle(self, *args, **options):
        self.stdout.write("Configurando permissões dos grupos...")
        
        # Admin Ministerio - TODAS as permissões exceto django.admin
        self.configurar_admin_ministerio()
        
        # Liderança Ministerial
        self.configurar_lideranca_secretaria()
        self.configurar_lideranca_financeira()
        
        # Regional
        self.configurar_pastor_regional()
        
        # Operacional Local
        self.configurar_secretario_local()
        self.configurar_tesoureiro_local()
        self.configurar_superintendente_ebd()
        
        # Equipes
        self.configurar_equipe_eventos()
        self.configurar_equipe_midia()
        self.configurar_equipe_recepcao()
        self.configurar_professor_ebd()
        self.configurar_secretaria_ebd()
        
        # Base
        self.configurar_membro_comum()
        
        self.stdout.write(self.style.SUCCESS('✅ Permissões configuradas com sucesso!'))
    
    def configurar_admin_ministerio(self):
        grupo, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        
        # Todas exceto admin
        todas = Permission.objects.exclude(
            content_type__app_label__in=['admin', 'contenttypes', 'sessions']
        )
        grupo.permissions.set(todas)
        
        self.stdout.write(f"  ✅ {ADMIN_MINISTERIO}: {grupo.permissions.count()} permissões")
    
    def configurar_lideranca_secretaria(self):
        grupo, _ = Group.objects.get_or_create(name=LIDERANCA_SECRETARIA)
        
        permissoes = self.get_permissions([
            # Secretaria
            'secretaria.view_pessoa',
            'secretaria.add_pessoa',
            'secretaria.change_pessoa',
            'secretaria.delete_pessoa',
            'secretaria.view_cargo',
            'secretaria.add_cargo',
            'secretaria.change_cargo',
            'secretaria.view_familia',
            'secretaria.add_familia',
            'secretaria.change_familia',
            'secretaria.delete_familia',
            'secretaria.view_tag',
            'secretaria.add_tag',
            # Eventos (visualização)
            'eventos.view_evento',
            'eventos.view_inscricao',
            # Comunicação
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
            'comunicacao.add_mensagem',
            # EBD (visualização)
            'escola_biblica.view_turma',
            'escola_biblica.view_aluno',
        ])
        
        grupo.permissions.set(permissoes)
        self.stdout.write(f"  ✅ {LIDERANCA_SECRETARIA}: {len(permissoes)} permissões")
    
    def configurar_lideranca_financeira(self):
        grupo, _ = Group.objects.get_or_create(name=LIDERANCA_FINANCEIRA)
        
        permissoes = self.get_permissions([
            # Financeiro (completo)
            'financeiro.view_transacao',
            'financeiro.add_transacao',
            'financeiro.change_transacao',
            'financeiro.delete_transacao',
            'financeiro.view_categoria',
            'financeiro.add_categoria',
            'financeiro.change_categoria',
            'financeiro.view_conta',
            'financeiro.add_conta',
            'financeiro.change_conta',
            # Secretaria (visualização para dízimos)
            'secretaria.view_pessoa',
            # Eventos (custos)
            'eventos.view_evento',
            # Comunicação
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
        ])
        
        grupo.permissions.set(permissoes)
        self.stdout.write(f"  ✅ {LIDERANCA_FINANCEIRA}: {len(permissoes)} permissões")
    
    # ... [implementar métodos para os demais grupos]
    
    def get_permissions(self, codename_list):
        \"\"\"Helper para buscar permissões por codename.\"\"\"
        permissions = []
        for codename_full in codename_list:
            app_label, codename = codename_full.split('.')
            try:
                perm = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename
                )
                permissions.append(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠️  Permissão não encontrada: {codename_full}")
                )
        return permissions
```

**Executar:**
```bash
python manage.py configurar_permissoes_grupos
```

---

## 📚 DOCUMENTAÇÃO PARA USUÁRIOS

### Como atribuir grupos?

1. Admin Ministerio acessa: **Contas → Gerenciar Usuários**
2. Clica em **"Editar Papéis"** do usuário
3. Seleciona os grupos apropriados
4. Considera hierarquia (não precisa dar Admin + Secretário, Admin já inclui)
5. Salva

### Qual grupo atribuir?

**Para líderes do ministério inteiro:**
- Admin Ministerio (dono/administrador)
- Liderança Secretaria (secretário geral)
- Liderança Financeira (tesoureiro geral)

**Para líderes regionais:**
- Pastor Regional (supervisiona várias igrejas)

**Para equipe de uma igreja:**
- Secretario Local (secretariado da igreja)
- Tesoureiro (finanças da igreja)
- Superintendente EBD (coordena escola bíblica)

**Para voluntários e equipes:**
- Equipe de Eventos
- Equipe de Mídia
- Equipe de Recepção
- Professor EBD (professor de turma)
- Secretaria EBD (auxiliar da EBD)

**Para membros comuns:**
- Membro Comum (todos os membros devem ter pelo menos este)

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Preparação (2-3 horas)
- [ ] Ler e entender este documento
- [ ] Fazer backup do banco de dados
- [ ] Testar em ambiente de desenvolvimento primeiro

### Fase 2: Código (3-4 horas)
- [ ] Criar `contas/constants.py`
- [ ] Criar migration de renomeação de grupos
- [ ] Executar migration
- [ ] Criar comando `configurar_permissoes_grupos.py`
- [ ] Executar comando
- [ ] Atualizar imports no código (substituir strings por constants)

### Fase 3: Validação (2 horas)
- [ ] Testar login com cada tipo de grupo
- [ ] Verificar filtros (ministerial vs local)
- [ ] Testar permissões negadas
- [ ] Verificar URLs permitidas para usuários sem grupo

### Fase 4: Documentação (1 hora)
- [ ] Criar `docs/GRUPOS_PERMISSOES.md` (versão usuário final)
- [ ] Atualizar README do projeto
- [ ] Adicionar ao changelog

### Fase 5: Deploy (1 hora)
- [ ] Testar em staging
- [ ] Comunicar mudanças aos admins
- [ ] Deploy em produção
- [ ] Monitorar erros

---

## 🎯 RESULTADO ESPERADO

**Antes:**
- ❌ Grupos com nomes inconsistentes
- ❌ Grupos sem permissões configuradas
- ❌ Strings hardcoded no código
- ❌ Hierarquia confusa
- ❌ Falta documentação

**Depois:**
- ✅ 13 grupos bem definidos e nomeados
- ✅ Hierarquia clara (6 níveis)
- ✅ Permissões configuradas por módulo
- ✅ Código usa constantes
- ✅ Documentação completa
- ✅ Sistema profissional e escalável

---

**Elaborado por:** GitHub Copilot  
**Baseado em:** Análise de módulos (skills), feedback do usuário, e melhores práticas RBAC
