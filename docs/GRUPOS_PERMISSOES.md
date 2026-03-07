# Grupos e Permissões do Sistema GereIgreja

**Versão:** 1.3.0  
**Última atualização:** 12/02/2026

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura Hierárquica](#estrutura-hierárquica)
3. [Grupos Disponíveis](#grupos-disponíveis)
4. [Como Atribuir Grupos](#como-atribuir-grupos)
5. [Perguntas Frequentes](#perguntas-frequentes)

---

## 🎯 Visão Geral

O GereIgreja utiliza um sistema de **14 grupos de usuários** organizados em **7 níveis hierárquicos** para controlar o acesso e as permissões no sistema. Cada grupo tem responsabilidades específicas e acesso limitado às funcionalidades necessárias para suas atividades.

**Hierarquia Eclesiástica:** Pastor Presidente → Pastor Regional → Pastor Local → Equipe Administrativa

### Conceitos Importantes

- **Escopo Ministerial:** Usuários que podem acessar dados de **todas as igrejas** do ministério
- **Escopo Regional:** Usuários que podem acessar dados de **várias igrejas** de uma região
- **Escopo Local:** Usuários que podem acessar dados de **apenas uma igreja** específica

### 👨‍💻 Superusuários e Desenvolvedores

**IMPORTANTE:** O Django diferencia três tipos de usuários quanto ao acesso ao sistema administrativo:

#### Superusuários (`is_superuser=True`)
- ✅ **Acesso TOTAL** ao Django Admin
- ✅ **Todas as permissões** automaticamente (ignora grupos)
- ✅ Não precisam de grupos atribuídos
- 🎯 Uso recomendado: Desenvolvedores e suporte técnico
- ⚠️ Use com cautela: poder total sobre o sistema

#### Staff (`is_staff=True`)
- ✅ Pode acessar o Django Admin
- ⚠️ **Respeita permissões** dos grupos atribuídos
- ⚠️ Precisa de grupos para acessar módulos
- 🎯 Uso recomendado: Administradores e gestores

#### Usuários Normais (sem flags especiais)
- ❌ Não acessam Django Admin (mesmo com grupos)
- ✅ Acessam interface web do sistema conforme seus grupos
- 🎯 Uso recomendado: Membros, secretários, tesoureiros

**Como o Django verifica permissões:**
1. Se `is_superuser=True` → acesso total (fim da verificação)
2. Se `is_staff=True` → verifica permissões dos grupos
3. Se não tem `is_staff` → não acessa admin

**Exemplo prático:**
```python
# Criar desenvolvedor (acesso total)
dev = User.objects.create_user(
    username='dev@igreja.com',
    is_staff=True,
    is_superuser=True  # ← Acesso total
)
# Não precisa de grupos!

# Criar admin ministerial (com grupos)
admin = User.objects.create_user(
    username='admin@igreja.com',
    is_staff=True,  # ← Pode acessar admin
    # is_superuser=False (padrão)
)
admin.groups.add(grupo_admin_ministerio)  # ← Precisa de grupo
```

---

## 🏗️ Estrutura Hierárquica

```
┌─────────────────────────────────────────────────────────┐
│  NÍVEL 1: Administrativo                                │
│  • Admin Ministerio (Acesso Total)                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  NÍVEL 2: Liderança Ministerial (Todas as igrejas)     │
│  • Liderança Secretaria                                 │
│  • Liderança Financeira                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  NÍVEL 3: Liderança Regional (Várias igrejas)          │
│  • Pastor Regional                                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  NÍVEL 4: Liderança Local (Uma igreja)                 │
│  • Pastor Local                                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  NÍVEL 5: Operacional Local (Uma igreja)               │
│  • Secretário Local                                     │
│  • Tesoureiro                                           │
│  • Superintendente EBD                                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  NÍVEL 6: Equipes e Auxiliares                         │
│  • Equipe de Eventos                                    │
│  • Equipe de Mídia                                      │
│  • Equipe de Recepção                                   │
│  • Professores EBD                                      │
│  • Secretaria EBD                                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  NÍVEL 7: Membros                                       │
│  • Membro Comum                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 👥 Grupos Disponíveis

### 1️⃣ Admin Ministerio
**Escopo:** Ministerial (todas as igrejas)  
**Responsabilidades:**
- Gerenciamento completo do sistema
- Criar e gerenciar usuários
- Configurar igrejas e ministério
- Acesso a todos os módulos

**Permissões:**
- ✅ Todas as funcionalidades do sistema
- ✅ Gerenciar usuários e grupos
- ✅ Configurações do ministério
- ✅ Backup e manutenção

**Quem deve ter:** Administrador principal do ministério

---

### 2️⃣ Liderança Secretaria
**Escopo:** Ministerial (todas as igrejas)  
**Responsabilidades:**
- Coordenar secretarias de todas as igrejas
- Visualizar e editar cadastros de membros
- Aprovar transferências entre igrejas
- Gerar relatórios consolidados

**Permissões:**
- ✅ Ver e editar membros de todas as igrejas
- ✅ Ver cargos (não gerencia - cargos são locais)
- ✅ Gerenciar famílias e tags
- ✅ Ver eventos e comunicações
- ❌ NÃO pode gerenciar finanças
- ❌ NÃO pode criar/editar cargos

**Quem deve ter:** Secretário geral do ministério

---

### 3️⃣ Liderança Financeira
**Escopo:** Ministerial (todas as igrejas)  
**Responsabilidades:**
- Consolidação financeira do ministério
- Auditar lançamentos das igrejas
- Criar categorias financeiras globais
- Gerar relatórios consolidados

**Permissões:**
- ✅ **Visualizar** transações de todas as igrejas
- ✅ Criar e gerenciar categorias financeiras globais
- ✅ Gerar relatórios financeiros
- ❌ NÃO lança transações (apenas visualiza e audita)
- ❌ NÃO insere dízimos/ofertas locais

**Quem deve ter:** Tesoureiro geral do ministério

**Importante:** Este grupo é para **auditoria e consolidação**, não para operação local.

---

### 4️⃣ Pastor Regional
**Escopo:** Regional (várias igrejas)  
**Responsabilidades:**
- Supervisionar pastores locais da região
- Acompanhar crescimento das congregações
- Aprovar eventos regionais
- Ver estatísticas agregadas

**Permissões:**
- ✅ Ver membros das igrejas da região
- ✅ Ver cargos (não gerencia)
- ✅ Ver finanças das igrejas (não lança)
- ✅ Criar eventos regionais
- ✅ Enviar comunicações
- ❌ NÃO gerencia cargos (responsabilidade local)
- ❌ NÃO lança transações financeiras

**Quem deve ter:** Pastor de região que supervisiona várias igrejas

---

### 5️⃣ Pastor Local
**Escopo:** Local (UMA igreja específica)  
**Responsabilidades:**
- **Líder espiritual da igreja local**
- Pastor principal da congregação
- Gestão completa de membros e ministérios
- Aprovar cargos ministeriais (Diácono, Presbítero)
- Supervisionar finanças (não lança - tem tesoureiro)
- Coordenar eventos e ministérios da igreja

**Permissões:**
- ✅ Gerenciar membros completamente (CRUD)
- ✅ **Aprovar cargos** (add/change - importante para ordenações)
- ✅ Gerenciar famílias e visitas
- ✅ **Ver finanças** (visualização para supervisão pastoral)
- ✅ Gerenciar eventos da igreja
- ✅ Enviar avisos e comunicações
- ✅ Ver turmas e alunos da EBD
- ✅ Gerenciar agenda pastoral
- ❌ NÃO lança transações financeiras (tem tesoureiro)
- ❌ NÃO gerencia turmas EBD (tem superintendente)

**Quem deve ter:** Pastor principal de cada igreja local

**Diferença do Pastor Regional:**
- **Pastor Regional:** supervisiona VÁRIAS igrejas
- **Pastor Local:** pastoreia UMA igreja específica

---

### 6️⃣ Secretário Local
**Escopo:** Local (uma igreja)  
**Responsabilidades:**
- Cadastrar e editar membros da igreja
- **Gerenciar cargos locais** (Diácono, Presbítero, etc.)
- Gerenciar famílias
- Registrar visitas e acompanhamentos

**Permissões:**
- ✅ Criar, editar e deletar membros da sua igreja
- ✅ **Gerenciar cargos locais** (completo)
- ✅ Gerenciar famílias e tags
- ✅ Ver eventos e EBD
- ❌ NÃO pode ver outras igrejas
- ❌ NÃO pode gerenciar finanças

**Quem deve ter:** Secretário de uma congregação específica

---

### 7️⃣ Tesoureiro
**Escopo:** Local (uma igreja)  
**Responsabilidades:**
- Lançar receitas e despesas da igreja
- Gerenciar contas bancárias locais
- Fazer fechamento de caixa
- Gerar relatórios financeiros

**Permissões:**
- ✅ Lançar dízimos, ofertas, receitas e despesas
- ✅ Gerenciar contas bancárias da igreja
- ✅ Ver membros (para vincular dízimos)
- ✅ Usar categorias globais criadas pela liderança
- ❌ NÃO pode criar categorias (usa as globais)
- ❌ NÃO pode ver finanças de outras igrejas

**Quem deve ter:** Tesoureiro de uma congregação específica

---

### 8️⃣ Superintendente EBD
**Escopo:** Local (EBD de uma igreja)  
**Responsabilidades:**
- Gerenciar turmas e professores
- Planejar aulas e conteúdo
- Gerenciar matrículas de alunos
- Coordenar a Escola Bíblica

**Permissões:**
- ✅ Criar, editar e deletar turmas
- ✅ Gerenciar matrículas de alunos
- ✅ Planejar aulas e frequência
- ✅ Ver membros (para matricular)
- ❌ NÃO pode gerenciar turmas de outras igrejas

**Quem deve ter:** Responsável pela EBD da igreja

---

### 9️⃣ Equipe de Eventos
**Escopo:** Local (uma igreja)  
**Responsabilidades:**
- Criar e editar eventos
- Gerenciar inscrições
- Controlar presença
- Planejar logística

**Permissões:**
- ✅ Criar e editar eventos da igreja
- ✅ Gerenciar inscrições
- ✅ Ver membros (para inscrições)
- ✅ Enviar comunicações sobre eventos
- ❌ NÃO pode deletar eventos (histórico)
- ❌ NÃO pode gerenciar eventos de outras igrejas

**Quem deve ter:** Membros da equipe de eventos

---

### 🔟 Equipe de Mídia
**Escopo:** Local (uma igreja)  
**Responsabilidades:**
- Produção audiovisual
- Transmissão de cultos
- Conteúdo para redes sociais
- Gerenciar arquivos de mídia

**Permissões:**
- ✅ Upload de vídeos e fotos
- ✅ Ver eventos (programação)
- ✅ Ver comunicações
- ❌ NÃO pode acessar dados de membros
- ❌ NÃO pode enviar mensagens em massa

**Quem deve ter:** Membros da equipe de comunicação/mídia

---

### 1️⃣1️⃣ Equipe de Recepção
**Escopo:** Local (uma igreja)  
**Responsabilidades:**
- Cadastrar visitantes
- Registrar presença em cultos
- Fazer acompanhamento inicial
- Atendimento

**Permissões:**
- ✅ Cadastrar novos visitantes
- ✅ Ver lista de membros (identificação)
- ✅ Inscrever visitantes em eventos
- ❌ NÃO pode editar dados de membros batizados
- ❌ NÃO pode alterar status de pessoas

**Quem deve ter:** Membros da equipe de recepção

---

### 1️⃣2️⃣ Professores EBD
**Escopo:** Local (turma específica)  
**Responsabilidades:**
- Dar aulas da sua turma
- Registrar frequência
- Planejar conteúdo de aulas
- Acompanhar alunos

**Permissões:**
- ✅ Planejar e editar aulas da sua turma
- ✅ Registrar frequência dos alunos
- ✅ Ver lista de alunos da turma
- ❌ NÃO pode gerenciar turmas
- ❌ NÃO pode matricular alunos
- ❌ NÃO pode ver outras turmas

**Quem deve ter:** Professores da Escola Bíblica

---

### 1️⃣3️⃣ Secretaria EBD
**Escopo:** Local (EBD de uma igreja)  
**Responsabilidades:**
- Registrar presença de alunos
- Gerar relatórios de frequência
- Apoiar superintendente
- Organizar materiais

**Permissões:**
- ✅ Registrar frequência de todas as turmas
- ✅ Ver turmas, alunos e aulas
- ✅ Ver membros
- ❌ NÃO pode gerenciar turmas
- ❌ NÃO pode planejar aulas
- ❌ NÃO pode matricular alunos

**Quem deve ter:** Auxiliar administrativo da EBD

---

### 1️⃣4️⃣ Membro Comum
**Escopo:** Sistema (próprios dados)  
**Responsabilidades:**
- Ver e editar próprio perfil
- Inscrever-se em eventos
- Ver comunicados
- Acessar informações da igreja

**Permissões:**
- ✅ Ver e editar próprio perfil (limitado)
- ✅ Inscrever-se em eventos
- ✅ Ver comunicações e notificações
- ✅ Ver agenda pública
- ✅ Alterar própria senha
- ❌ NÃO pode ver dados de outros membros
- ❌ NÃO pode acessar módulos administrativos

**Quem deve ter:** Todos os membros regulares da igreja

---

## 🔧 Como Atribuir Grupos

### Passo 1: Acessar Gerenciamento de Usuários
1. Faça login como **Admin Ministerio**
2. Acesse o menu **Configurações** → **Usuários**

### Passo 2: Selecionar Usuário
1. Encontre o usuário na lista
2. Clique em **Editar Papéis/Grupos**

### Passo 3: Atribuir Grupos
1. Marque os grupos desejados
2. **Importante:** Um usuário pode ter **múltiplos grupos**
3. Clique em **Salvar**

### Passo 4: Definir Igreja Ativa (Para grupos locais)
1. Para grupos com escopo **Local** (Secretário, Tesoureiro, etc.)
2. Defina a **Igreja Ativa** do usuário
3. Isso determina qual igreja ele gerencia

---

## ❓ Perguntas Frequentes

### 1. Um usuário pode ter múltiplos grupos?
**Sim!** Por exemplo, uma pessoa pode ser:
- Secretário Local + Superintendente EBD
- Tesoureiro + Equipe de Eventos

### 2. Qual a diferença entre Liderança Secretaria e Secretário Local?
- **Liderança Secretaria:** Vê **todas as igrejas**, coordena secretarias, não gerencia cargos
- **Secretário Local:** Vê **apenas uma igreja**, gerencia membros e cargos locais

### 3. Qual a diferença entre os 3 níveis de pastores?
- **Admin Ministerio (Pastor Presidente):**
  - Acesso total ao sistema
  - Administra TODO o ministério
  - Gerencia TODAS as igrejas
  
- **Pastor Regional:**
  - Supervisiona VÁRIAS igrejas de uma região
  - Não lança transações, não gerencia cargos
  - Foco em supervisão e coordenação
  
- **Pastor Local:**
  - Pastor de UMA igreja específica
  - Gestão completa da congregação
  - Aprova cargos ministeriais
  - Supervisiona (não lança) finanças

### 4. Quem pode aprovar cargos ministeriais (Diácono, Presbítero)?
- **Pastor Local:** Pode aprovar cargos da sua igreja
- **Secretário Local:** Gerencia cargos administrativamente (CRUD completo)
  
Cargos são **locais** - cada igreja gerencia os seus próprios.

### 5. Por que o Tesoureiro Geral (Liderança Financeira) não lança transações?
O Tesoureiro Geral é responsável pela **consolidação e auditoria**. As transações devem ser lançadas pelos **Tesoureiros Locais** de cada igreja. Isso mantém a descentralização e o controle local.

### 6. O que acontece se um usuário não tiver nenhum grupo?
O usuário verá uma página "Aguardando Permissões" e não poderá acessar o sistema até que um Admin atribua um grupo.

### 7. Posso criar novos grupos personalizados?
Tecnicamente sim, mas **não é recomendado**. Os 14 grupos foram cuidadosamente planejados para cobrir todas as necessidades. Consulte o suporte antes de criar grupos customizados.

### 8. Qual a diferença entre Superusuário e Admin Ministerio?
- **Superusuário (`is_superuser=True`):**
  - Acesso TOTAL ao sistema e Django Admin
  - Ignora verificações de grupos e permissões
  - Usado por desenvolvedores e suporte técnico
  - Não precisa de grupos atribuídos
  
- **Admin Ministerio (grupo):**
  - Acesso completo às funcionalidades do sistema
  - Respeita as permissões configuradas
  - Usado por administradores da igreja
  - É um grupo como qualquer outro

**Quando usar cada um?**
- Use **Superusuário** apenas para equipe técnica e emergências
- Use **Admin Ministerio** para administradores regulares da igreja

### 9. Um desenvolvedor precisa de grupos?
**Não!** Se o usuário tem `is_superuser=True`, ele já tem acesso total e não precisa de grupos. Os grupos só são necessários para usuários com `is_staff=True` e `is_superuser=False`.

### 10. Como remover um usuário do sistema?
1. Acesse como Admin
2. Vá em Configurações → Usuários
3. Encontre o usuário
4. Clique em **Desativar** (recomendado) ou **Remover**

**Importante:** Desativar é preferível a remover, pois mantém o histórico.

### 11. O que é "Igreja Ativa"?
É a igreja padrão que o usuário está gerenciando. Para grupos com escopo Local, define qual igreja ele pode acessar. O usuário pode ter acesso a múltiplas igrejas dependendo do grupo.

---

## 📞 Suporte

Dúvidas sobre grupos e permissões? Entre em contato:
- **Documentação técnica:** `skills/configuracao/ESTRUTURA_GRUPOS_COMPLETA.md`
- **Suporte:** Abra um ticket no módulo de Suporte do sistema
- **Email:** suporte@gereigreja.com.br

---

**Última atualização:** 12/02/2026  
**Versão do documento:** 1.2  
**Versão do sistema:** 1.3.0
