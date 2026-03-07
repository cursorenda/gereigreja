# 🔐 Release Notes - Versão 1.3.0

**Data de Lançamento:** 12 de Fevereiro de 2026  
**Tema:** Sistema de Grupos e Permissões Refatorado + Pastor Local

---

## 🎯 Visão Geral

A versão 1.3.0 traz uma **refatoração completa do sistema de grupos e permissões** com a adição do grupo **Pastor Local**, implementando a hierarquia eclesiástica real: **Pastor Presidente → Pastor Regional → Pastor Local → Equipe Administrativa**. Centraliza toda a lógica de permissões, melhora a experiência em casos de acesso negado e reflete com precisão a estrutura de liderança pastoral.

---

## ✨ Novidades Principais

### 🆕 Grupo Pastor Local
**Novo nível hierárquico entre Pastor Regional e equipe administrativa**

- **Pastor Local**: Líder espiritual de UMA igreja específica
  - Gestão completa de membros da congregação
  - Aprova cargos ministeriais (Diácono, Presbítero)
  - Supervisiona finanças (visualização apenas)
  - Gerencia eventos e ministérios da igreja
  - 50+ permissões configuradas

**Diferença dos outros níveis pastorais:**
- **Pastor Presidente (Admin Ministerio)**: TODO o ministério
- **Pastor Regional**: VÁRIAS igrejas de uma região
- **Pastor Local**: UMA igreja específica ⭐ NOVO

### Sistema de Grupos Centralizado
- Módulo `contas/constants.py` expandido (322 linhas)
- **14 grupos** definidos em constantes (anteriormente 13)
- 15+ funções helper para verificações de permissões
- Hierarquia em 7 níveis refletindo estrutura eclesiástica real

### Template 403 Profissional
- Nova página "Acesso Negado" com design melhorado
- Mostra grupos do usuário e igreja ativa
- Instruções claras sobre como obter acesso
- Evita confusão ao mostrar que usuário já está logado

### Middleware de Permissões
- Novo `PermissionDeniedMiddleware` 
- Captura exceções e renderiza 403.html personalizado
- **Antes**: redirecionava para login (confuso)
- **Agora**: mostra que usuário está logado mas sem permissão

---

## 🔄 Alterações Importantes

### Renomeação de Grupos (Breaking Changes)

Para melhor refletir a estrutura eclesiástica, três grupos foram renomeados:

| Antes | Depois |
|-------|--------|
| `Superintendentes` | `Superintendente EBD` |
| `Lider Igreja` | `Pastor Regional` |
| `Secretario` | `Secretario Local` |

**Impacto:** A migração automática renomeia os grupos e mantém todos os usuários vinculados corretamente.

### Código Refatorado

**11 arquivos atualizados** para usar constantes, com permissões expandidas para Pastor Local:

- `contas/constants.py` - Adicionado `PASTOR_LOCAL` e `user_is_pastor_local()`
- `contas/management/commands/configurar_permissoes_grupos.py` - Nova função `configurar_pastor_local()`

- `secretaria/views.py`
- `configuracao/views.py`
- `contas/views.py`
- `core/views.py`
- `core/decorators.py`
- `financeiro/utils.py`
- `secretaria/utils.py`
- `comunicacao/utils.py`
- `configuracao/utils.py`
- `suporte/views.py`

**Benefício:** Futuras mudanças em nomes de grupos requerem alteração em apenas um local.

---

## 🛠️ Melhorias Técnicas

### Funções Helper Disponíveis

```python
from contas.constants import (
    user_is_admin,
    user_tem_grupo,
    user_escopo_ministerial,
    is_admin_org,
    is_secretario,
    is_lider_igreja,
    is_tesoureiro,
    # ... e mais
)
```

**Exemplos de uso:**

```python
# Verificar se usuário é admin
if user_is_admin(request.user):
    # Acesso total

# Verificar grupo específico
if user_tem_grupo(request.user, PASTOR_LOCAL):
    # Acesso de pastor

# Obter escopo (ministerial vs local)
escopo = user_escopo_ministerial(request.user)
if escopo == 'ministerio':
    # Acesso a todas as igrejas
```

### Hierarquias Definidas

```python
GRUPOS_MINISTERIAIS = [ADMIN_MINISTERIO, PASTOR_REGIONAL, TESOUREIRO]
GRUPOS_LOCAIS = [ADMIN_ORG, PASTOR_LOCAL, SECRETARIO_LOCAL, ...]
GRUPOS_EBD = [SUPERINTENDENTE_EBD, SECRETARIA_EBD, PROFESSOR]
GRUPOS_MEMBROS = [MEMBRO_COMUM]
GRUPOS_TODOS = [...todos os grupos...]
```

---

## 📦 Migrações e Deploy

### 1. Backup (Obrigatório)
```bash
python manage.py backup_postgres
```

### 2. Aplicar Migrações
```bash
python manage.py migrate
# Executa automaticamente: 
#   - contas/0003_rename_grupos_v1_2_0 (renomeia 3 grupos)
#   - contas/0004_add_pastor_local_group (cria grupo Pastor Local)
```

### 3. Reconfigurar Permissões
```bash
python manage.py configurar_permissoes_grupos --reset
```
Este comando agora:
- Configura **14 grupos** (anteriormente 13)
- Atribui 50+ permissões ao Pastor Local
- Total de 520+ permissões no sistema
- `--reset`: Remove e recria todos os grupos
- `--dry-run`: Simula sem fazer mudanças

### 4. Validar Sistema
```bash
# Usar script de testes
Get-Content test_shell.py | python manage.py shell
```

---

## ⚠️ Atenção: Breaking Changes

### Para Desenvolvedores

Se seu código referencia diretamente os nomes antigos dos grupos:
```python
# ❌ ANTES (não funciona mais)
if user.groups.filter(name='Superintendentes').exists():

# ✅ AGORA
from contas.constants import SUPERINTENDENTE_EBD, user_tem_grupo
if user_tem_grupo(user, SUPERINTENDENTE_EBD):
```

### Para Administradores

- Usuários permanecem nos mesmos grupos (renomeados automaticamente)
- **Novo grupo Pastor Local** disponível para atribuição
- Permissões mantidas intactas
- Recomendado testar acesso de cada tipo de usuário após deploy
- **Atribuir Pastor Local** aos pastores de igrejas locais via Admin → Usuários

---

## 🧪 Testes e Validação

### Testes Automatizados
- Script `test_shell.py` atualizado para verificar 14 grupos
- Todos os testes passaram ✅
- Validado em ambiente de produção com 18 usuários ativos

### Resultados
- ✅ **14 grupos** criados corretamente (incluindo Pastor Local)
- ✅ **520+ permissões** configuradas
- ✅ Admin Ministerio: 364 permissões
- ✅ **Pastor Local**: 50+ permissões
- ✅ Renomeação bem-sucedida
- ✅ Funções helper funcionando
- ✅ Hierarquias corretas

---

## 👨‍💻 Nota para Desenvolvedores

### Superusuários vs Staff

**Superusuários (`is_superuser=True`):**
- ✅ Acesso TOTAL ao Django Admin
- ✅ TODAS as permissões automaticamente
- ✅ Não precisam de grupos atribuídos
- ✅ Usados para desenvolvimento e suporte técnico

**Staff (`is_staff=True`):**
- ✅ Pode acessar o Django Admin
- ⚠️ Respeitam permissões dos grupos atribuídos
- ⚠️ Precisam de grupos para acessar módulos

**Usuários Normais:**
- ❌ Não acessam Django Admin (mesmo com grupos)
- ✅ Acessam interface web do sistema conforme seus grupos

### Como Funciona

O Django verifica permissões nesta ordem:
1. Se `is_superuser=True` → **acesso total** (ignora grupos)
2. Se `is_staff=True` → verifica permissões dos grupos
3. Se não tem `is_staff` → não acessa admin

---

## 📚 Documentação

### Novos Documentos
- [`docs/GRUPOS_PERMISSOES.md`](../GRUPOS_PERMISSOES.md) - Guia completo do sistema

### Atualizados
- [`README.md`](../../README.md) - Nova seção "Sistema de Grupos e Permissões"
- [`CHANGELOG.md`](../../CHANGELOG.md) - Histórico atualizado

---

## 🎓 Exemplos Práticos

### Criar Usuário Desenvolvedor
```python
from django.contrib.auth import get_user_model
User = get_user_model()

dev = User.objects.create_user(
    username='dev@igreja.com',
    email='dev@igreja.com',
    password='senha_segura',
    is_staff=True,      # Pode acessar admin
    is_superuser=True   # Acesso total
)
# Não precisa de grupos!
```

### Criar Usuário Pastor Local
```python
from contas.constants import PASTOR_LOCAL
from django.contrib.auth.models import Group

pastor = User.objects.create_user(
    username='pastor@igreja.com',
    email='pastor@igreja.com',
    password='senha_segura',
    is_staff=True       # Pode acessar admin
    # is_superuser=False (padrão)
)

# Atribuir grupo Pastor Local
grupo = Group.objects.get(name=PASTOR_LOCAL)
pastor.groups.add(grupo)

# Definir igreja (importante!)
pastor.perfil.igreja_ativa = igreja_sede
pastor.perfil.save()
```

### Verificar Permissão de Pastor Local em View
```python
from contas.constants import ADMIN_MINISTERIO

admin = User.objects.create_user(
    username='admin@igreja.com',
    email='admin@igreja.com',
    password='senha_segura',
    is_staff=True       # Pode acessar admin
    # is_superuser=False (padrão)
)

# Atribuir grupo
from django.contrib.auth.models import Group
grupo = Group.objects.get(name=ADMIN_MINISTERIO)
admin.groups.add(grupo)
```

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from contas.constants import PASTOR_LOCAL, user_is_pastor_local

@login_required
def aprovar_cargo(request, cargo_id):
    # Apenas Pastor Local e superiores podem aprovar cargos
    if not (request.user.is_superuser or user_is_pastor_local(request.user)):
        return render(request, '403.html', status=403)
    
    # ... resto da lógica
```

---

## 🚀 Próximos Passos

Após atualizar para v1.3.0:

1. ✅ Execute as migrações
2. ✅ Reconfigure permissões com `--reset`
3. ✅ **Atribua grupo "Pastor Local"** aos pastores de igrejas
4. ✅ Verifique logs de erro: `logs/django_errors.log`
5. ✅ Teste login de cada tipo de usuário
6. ✅ Valide que template 403 aparece corretamente quando sem permissão
7. ✅ Confirme que pastores locais podem aprovar cargos
8. ✅ Teste que Pastor Local vê mas não lança finanças

---

## 📞 Suporte

Para dúvidas ou problemas relacionados a esta versão:
- Consulte [`docs/GRUPOS_PERMISSOES.md`](../GRUPOS_PERMISSOES.md)
- Revise o FAQ na documentação (11 perguntas incluindo diferenças entre níveis pastorais)
- Execute script de testes para diagnosticar

---

**Desenvolvido com ❤️ para gestão eclesiástica eficiente**
