# 🏛️ Seletor Global de Igreja - Documentação Técnica

## 📋 Índice
- [Visão Geral](#visão-geral)
- [Para Usuários](#para-usuários)
- [Para Desenvolvedores](#para-desenvolvedores)
- [Para IA](#para-ia-contexto-técnico)
- [Casos de Uso](#casos-de-uso)
- [Troubleshooting](#troubleshooting)

---

## Visão Geral

O **Seletor Global de Igreja** é um componente que aparece no topo do sistema e define qual igreja/congregação o usuário está gerenciando no momento. Ele controla o **escopo dos dados** exibidos em todas as telas do sistema.

### Conceito Central

```
┌──────────────────────────────────────┐
│  Igreja Ativa: [AD Serafim]    ▼    │ ← Seletor Global
└──────────────────────────────────────┘
         ↓
    Define o escopo
         ↓
┌──────────────────────────────────────┐
│  Todas as views filtram por esta    │
│  igreja automaticamente              │
│  - Membros                           │
│  - Turmas EBD                        │
│  - Relatórios                        │
│  - Etc.                              │
└──────────────────────────────────────┘
```

---

## Para Usuários

### 🤔 O que é o Seletor de Igreja?

É o **menu no topo da tela** que mostra qual igreja você está gerenciando. Pense nele como um "filtro automático" que garante que você veja apenas os dados da igreja selecionada.

### 👀 Como funciona para você?

**Se você gerencia MÚLTIPLAS igrejas (admin, tesoureiro):**
```
┌──────────────────────────────────────┐
│  Igreja: [Sede Central    ▼]        │ ← Clique para trocar
│           • AD Serafim               │
│           • AD Itamacuri             │
└──────────────────────────────────────┘
```
- Você pode **clicar e escolher** qual igreja quer gerenciar
- Ao trocar, todas as telas atualizam automaticamente
- Finanças, membros, turmas - tudo filtra pela igreja escolhida

**Se você trabalha em UMA igreja (professor, pastor local):**
```
┌──────────────────────────────────────┐
│  Igreja: AD Serafim                  │ ← Informativo (fixo)
└──────────────────────────────────────┘
```
- O seletor **mostra sua igreja** mas não é clicável
- Você sempre verá apenas dados da sua congregação
- Isso garante organização e evita confusão

### 📍 Onde encontro?

**Desktop:** Canto superior direito, ao lado do seu nome
**Mobile:** Menu hambúrguer → "Igreja Ativa"

### ✅ O que posso fazer?

| Seu Papel | O que você vê | Pode trocar? |
|-----------|---------------|--------------|
| **Admin do Ministério** | Todas as igrejas | ✅ Sim |
| **Tesoureiro** | Igrejas configuradas | ✅ Sim |
| **Pastor/Professor** | Sua igreja | ❌ Não |
| **Membro comum** | Sua igreja | ❌ Não |

---

## Para Desenvolvedores

### 🏗️ Arquitetura

#### 1. Funcao principal de escopo: `get_igrejas_permitidas()`

**Localizacao:** `core/utils.py`

**Responsabilidade:** Determina quais igrejas um usuario pode acessar com base na hierarquia e no escopo.

**Hierarquia de Permissões:**

```python
def get_igrejas_permitidas(user, ministerio=None):
    """
    Hierarquia de permissões (ordem de verificação):
    
    1. Admin Org (is_admin_org)
       → Retorna: TODAS as igrejas do ministério
    
    2. Permissões Financeiras (has_finance_view_permission)
       a. Líder Financeiro (is_finance_leader)
          → Retorna: Igrejas configuradas + subordinadas (recursivo)
       b. Outros papéis financeiros
          → Retorna: Igrejas explicitamente permitidas (perfil.igrejas_permitidas)
    
    3. Membros sem permissão financeira (Pessoa.usuario = user)
       → Retorna: Igreja onde é cadastrado (Pessoa.igreja)
    
    4. Sem vínculo
       → Retorna: QuerySet vazio
    """
```

#### 2. Middleware: `ActiveChurchMiddleware`

**Localização:** `core/middleware.py`

**Fluxo de execução:**

```python
# 1. Request chega
request → ActiveChurchMiddleware

# 2. Verifica sessão
igreja_ativa_id = request.session.get('igreja_ativa_id')

# 3. Obtem igrejas permitidas
allowed = get_igrejas_permitidas(request.user, ministerio)

# 4. Injeta automaticamente no request
request.igrejas_permitidas = allowed

# 5. Valida e define igreja ativa
if igreja_ativa_id in allowed:
    request.igreja_ativa = Igreja.objects.get(pk=igreja_ativa_id)
elif allowed.count() == 1:
    request.igreja_ativa = allowed.first()
    request.session['igreja_ativa_id'] = allowed.first().pk
else:
    request.igreja_ativa = None

# 6. View executa com request.igreja_ativa e request.igrejas_permitidas
```

#### 3. Como Usar nas Views

**Padrão recomendado:**

```python
from core.decorators import inject_igrejas_permitidas

@login_required
@inject_igrejas_permitidas
def minha_view(request):
    # request.igrejas_permitidas vem do middleware (ou fallback do decorator)
    membros = Membro.objects.filter(igreja__in=request.igrejas_permitidas)
    return render(request, 'template.html', {'membros': membros})
```

**Para views EBD com permissões granulares:**

```python
@login_required
def turma_list(request):
    turmas = Turma.objects.filter(ano_letivo=ano_letivo_atual)
    
    # Verifica se é secretaria ou professor
    is_secretaria = (
        request.user.is_superuser or 
        request.user.groups.filter(name__in=['Secretaria EBD']).exists()
    )
    
    if not is_secretaria:
        # Professor: filtra por suas turmas (já limitado à sua igreja)
        turmas = turmas.filter(id__in=get_turmas_professor(request.user))
    else:
        # Secretaria: aplica filtro de igreja ativa
        if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
            turmas = turmas.filter(membros__igreja=request.igreja_ativa).distinct()
    
    return render(request, 'turma_list.html', {'turmas': turmas})
```

#### 4. Relacionamento entre Modelos

```
User (auth.User)
  ↓ OneToOne
PerfilUsuario (configuracao.PerfilUsuario)
  ↓ ForeignKey
Ministerio (configuracao.Ministerio)
  ↓ OneToMany
Igreja (configuracao.Igreja)
  ↓ ForeignKey
Pessoa (secretaria.Pessoa)
  ↓ OneToOne
User (via usuario field)

Fluxo de descoberta:
User → Pessoa (via membro_secretaria) → Igreja
```

#### 5. Casos Especiais

**Caso 1: Usuário com múltiplas igrejas (futuro)**

Atualmente, `Pessoa.igreja` é **único** (um membro pertence a uma igreja). Se no futuro precisar de múltiplas igrejas:

```python
# Opção A: Adicionar campo em MembroCargo (RECOMENDADO)
class MembroCargo(models.Model):
    membro = models.ForeignKey(Pessoa)
    cargo = models.ForeignKey(Cargo)
    igreja = models.ForeignKey(Igreja)  # ← Adicionar isto

# Então ajustar get_allowed_churches_for_user:
cargos_ativos = MembroCargo.objects.filter(
    membro=membro, 
    data_fim__isnull=True
).values_list('igreja_id', flat=True).distinct()

return Igreja.objects.filter(pk__in=cargos_ativos)
```

**Caso 2: Turmas de múltiplas igrejas**

Atualmente, turma não tem campo `igreja` explícito. Descobrimos via:
```python
turma.membros.all()[0].igreja  # Igreja do primeiro professor
```

Se precisar de campo explícito:
```python
class Turma(models.Model):
    igreja = models.ForeignKey(Igreja, null=True)  # ← Adicionar
```

**Caso 3: Relatórios consolidados**

Para relatórios que precisam ver múltiplas igrejas (admin):

```python
@login_required
def relatorio_consolidado(request):
    # Não usa request.igreja_ativa
    todas = get_allowed_churches_for_user(request.user)
    
    dados = []
    for igreja in todas:
        dados.append({
            'igreja': igreja.nome_igreja,
            'membros': Membro.objects.filter(igreja=igreja).count(),
            'turmas': Turma.objects.filter(membros__igreja=igreja).distinct().count(),
        })
    
    return render(request, 'consolidado.html', {'dados': dados})
```

#### 6. Testes

**Como testar get_allowed_churches_for_user:**

```python
from django.test import TestCase
from configuracao.models import PerfilUsuario, Ministerio, Igreja
from secretaria.models import Pessoa
from financeiro.utils import get_allowed_churches_for_user

class ChurchSelectorTest(TestCase):
    def setUp(self):
        self.ministerio = Ministerio.objects.create(nome_fantasia='Teste')
        self.igreja_a = Igreja.objects.create(nome_igreja='A', ministerio=self.ministerio)
        self.igreja_b = Igreja.objects.create(nome_igreja='B', ministerio=self.ministerio)
        
        self.user = User.objects.create_user(username='test')
        self.perfil = PerfilUsuario.objects.create(
            user=self.user, 
            ministerio=self.ministerio
        )
        self.membro = Pessoa.objects.create(
            nome='Test',
            igreja=self.igreja_a,
            usuario=self.user
        )
    
    def test_membro_ve_sua_igreja(self):
        """Membro comum vê apenas sua igreja."""
        igrejas = get_allowed_churches_for_user(self.user)
        self.assertEqual(igrejas.count(), 1)
        self.assertEqual(igrejas.first(), self.igreja_a)
    
    def test_admin_ve_todas(self):
        """Admin vê todas as igrejas do ministério."""
        self.user.is_superuser = True
        self.user.save()
        
        igrejas = get_allowed_churches_for_user(self.user)
        self.assertEqual(igrejas.count(), 2)
```

**Mock do middleware em testes:**

```python
from django.test import TestCase, override_settings

@override_settings(
    MIDDLEWARE=[
        # Lista SEM ActiveChurchMiddleware
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        # ... outros
    ]
)
class MyTestCase(TestCase):
    def test_view_sem_middleware(self):
        # request.igreja_ativa não será definido
        # Teste deve lidar com isso gracefully
        pass
```

---

## Para IA (Contexto Técnico)

### 🤖 Objetivo deste Documento

Fornecer contexto completo para agentes de IA (como eu) que trabalharão neste código no futuro. Este documento explica **decisões de design**, **trade-offs** e **contexto histórico**.

### 📜 Histórico de Mudanças

**v1.0 (inicial):**
- `get_allowed_churches_for_user()` retornava igrejas apenas para usuários com `has_finance_view_permission()`
- Professores EBD **não viam** o seletor de igreja
- Problema: Sem orientação sobre qual igreja estão gerenciando

**v1.2.2 (13/02/2026):**
- Expandido para incluir **membros sem permissão financeira**
- Professores/pastores agora **veem sua igreja** no seletor
- Decisão: Pessoa tem cargo apenas na igreja onde é membro (não múltiplas)

### 🎯 Decisões de Design

#### Decisão 1: Por que `get_allowed_churches_for_user()` está em `financeiro/utils.py`?

**Histórico:**
- Função criada originalmente para módulo financeiro
- Expandida para uso global (secretaria, EBD, eventos)

**Trade-off:**
- ✅ **Mantido em financeiro:** Evita breaking changes, imports continuam funcionando
- ❌ **Contra:** Nome "financeiro" não reflete uso global
- 💡 **Futuro:** Considerar mover para `core/permissions.py` ou `core/church_access.py`

**Se mover no futuro:**
```python
# Criar core/church_access.py
from financeiro.utils import get_allowed_churches_for_user as _original

# Manter compatibilidade
def get_allowed_churches_for_user(user):
    """Wrapper para retrocompatibilidade."""
    return _original(user)

# Deprecation notice
import warnings
warnings.warn(
    "financeiro.utils.get_allowed_churches_for_user está deprecated. "
    "Use core.church_access.get_allowed_churches_for_user",
    DeprecationWarning
)
```

#### Decisão 2: Por que Pessoa tem UMA igreja, não múltiplas?

**Regra de negócio definida pelo usuário:**
> "acho melhor que a pessoa tenha cargo apenas na congregação que ela atua"

**Contexto:**
- Gereigreja é sistema de gestão eclesiástica
- Pessoa é **membro** de uma igreja (registro legal/eclesiástico)
- Pode **atuar** em múltiplas igrejas, mas é **membro** de uma

**Modelo atual:**
```python
class Pessoa(models.Model):
    igreja = models.ForeignKey(Igreja)  # Único (onde é membro)

class MembroCargo(models.Model):
    membro = models.ForeignKey(Pessoa)
    cargo = models.ForeignKey(Cargo)
    # SEM: igreja = models.ForeignKey(Igreja)
    # Inferido: cargo é da igreja do membro
```

**Se precisar de múltiplas igrejas no futuro:**

O usuário considerou mas decidiu contra. Se contexto mudar:

```python
# Adicionar migration
class MembroCargo(models.Model):
    igreja = models.ForeignKey(Igreja)  # Qual igreja tem este cargo

# Ajustar get_allowed_churches_for_user
cargos_ativos = MembroCargo.objects.filter(
    membro=membro,
    data_fim__isnull=True
)
igrejas_ids = set(cargos_ativos.values_list('igreja_id', flat=True))
```

#### Decisão 3: Seletor aparece mesmo com 1 igreja?

**Sim, sempre aparece (mesmo informativo).**

**Razões:**
1. **UX consistente:** Usuário sempre sabe qual igreja está gerenciando
2. **Orientação:** "Você está em: AD Serafim"
3. **Escalabilidade:** Se ganhar acesso a mais igrejas, interface já existe
4. **Visual:** Não é intrusivo, apenas informativo quando read-only

**Implementação no template:**
```django
{% if allowed_churches.count == 1 %}
    <div class="church-selector readonly">
        <span>Igreja: {{ igreja_ativa.nome_igreja }}</span>
    </div>
{% else %}
    <select name="igreja_ativa_id">
        {% for igreja in allowed_churches %}
            <option value="{{ igreja.pk }}" {% if igreja == igreja_ativa %}selected{% endif %}>
                {{ igreja.nome_igreja }}
            </option>
        {% endfor %}
    </select>
{% endif %}
```

### 🔍 Fluxo de Dados Completo

```
1. User faz login
   ↓
2. Middleware: ActiveChurchMiddleware.__call__()
   ↓
3. Chama: get_allowed_churches_for_user(user)
   ↓
4. Verifica hierarquia:
   ├─ Superuser? → Todas
   ├─ Admin Org? → Todas
   ├─ Finanças? → Configuradas + subordinadas
   ├─ Membro? → user.membro_secretaria.igreja
   └─ Outros → None
   ↓
5. Retorna QuerySet[Igreja]
   ↓
6. Middleware verifica session['igreja_ativa_id']
   ↓
7. Se válido e em allowed → define request.igreja_ativa
   Se allowed.count() == 1 → auto-seleciona
   Se allowed.count() > 1 → espera seleção do usuário
   ↓
8. View executa com request.igreja_ativa disponível
   ↓
9. View filtra dados pela igreja ativa
   ↓
10. Template renderiza dados filtrados
```

### ⚠️ Pontos de Atenção para IA

**1. Queries podem ser caras:**

```python
# EVITE (N+1 queries):
for turma in turmas:
    igreja = turma.membros.first().igreja  # Query por turma

# PREFIRA (eager loading):
turmas = Turma.objects.prefetch_related('membros__igreja')
for turma in turmas:
    igreja = turma.membros.first().igreja  # Sem query adicional
```

**2. Middleware pode ser desabilitado em testes:**

```python
# Sempre verifique hasattr antes de usar
if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
    # usa request.igreja_ativa
else:
    # fallback apropriado
```

**3. Permissões granulares vs seletor global:**

Escola Bíblica usa **permissões granulares** (professor vê suas turmas) E **seletor global** (filtra por igreja). Ambos devem coexistir:

```python
# CORRETO (combina ambos):
turmas = Turma.objects.all()

# 1. Filtro de permissão (quem pode ver)
if not is_secretaria:
    turmas = turmas.filter(id__in=get_turmas_professor(user))

# 2. Filtro de igreja (isolamento de dados)
if request.igreja_ativa:
    turmas = turmas.filter(membros__igreja=request.igreja_ativa)

# INCORRETO (usa apenas um):
turmas = Turma.objects.filter(membros__igreja=request.igreja_ativa)  # ← Falta permissão
```

**4. Recursão em igrejas subordinadas:**

Cuidado com loops infinitos se houver hierarquia circular:

```python
def get_subordinadas_recursivamente(igreja_obj, visited=None):
    if visited is None:
        visited = set()
    
    if igreja_obj.pk in visited:
        return set()  # Evita loop
    
    visited.add(igreja_obj.pk)
    sub_ids = {igreja_obj.pk}
    
    for sub in igreja_obj.igrejas_subordinadas.all():
        sub_ids.update(get_subordinadas_recursivamente(sub, visited))
    
    return sub_ids
```

### 📚 Referências para IA

**Arquivos relacionados:**
- `financeiro/utils.py` → Função principal
- `core/middleware.py` → ActiveChurchMiddleware
- `escola_biblica/views.py` → Exemplo de uso com permissões granulares
- `configuracao/models.py` → Models (Ministerio, Igreja, PerfilUsuario)
- `secretaria/models.py` → Model Pessoa (relacionamento User↔Igreja)

**Constantes importantes:**
- `related_name='membro_secretaria'` em `Pessoa.usuario` (acesso via `user.membro_secretaria`)
- `related_name='perfil'` em `PerfilUsuario.user` (acesso via `user.perfil`)
- `related_name='assinatura'` em `AssinaturaMinisterio.ministerio`

**Grupos de permissão:**
- `'Admin Ministerio'` → is_admin_org(user)
- `'Tesoureiro'`, `'Lider Igreja'` → permissões financeiras
- `'Secretaria EBD'`, `'Superintendente EBD'` → permissões EBD totais
- `'Professores EBD'` → permissões granulares via funções helper

---

## Casos de Uso

### Caso 1: Professor visualizando suas turmas

**Usuário:** Pastor Júlio (Professor EBD na AD Serafim)

**Fluxo:**
```
1. Login → get_allowed_churches_for_user() retorna [AD Serafim]
2. Middleware define request.igreja_ativa = AD Serafim
3. Seletor mostra: "Igreja: AD Serafim" (read-only)
4. Acessa /escola_biblica/turmas/
5. View verifica: não é secretaria → filtra por get_turmas_professor()
6. get_turmas_professor() retorna turmas onde é membro
7. Turmas já são da AD Serafim (seu membro.igreja)
8. View renderiza apenas suas turmas
```

### Caso 2: Tesoureiro gerenciando múltiplas igrejas

**Usuário:** Irmão João (Tesoureiro de Sede + AD Serafim)

**Fluxo:**
```
1. Login → get_allowed_churches_for_user() retorna [Sede, AD Serafim]
2. Middleware busca session['igreja_ativa_id']
3. Se não existe ou inválido → request.igreja_ativa = None
4. Seletor mostra dropdown: [Sede, AD Serafim]
5. Usuário seleciona "AD Serafim"
6. POST para /configuracao/selecionar-igreja/ com igreja_id
7. Session salva: igreja_ativa_id = 2
8. Redirect → middleware define request.igreja_ativa = AD Serafim
9. Views de financeiro filtram por AD Serafim
```

### Caso 3: Admin vendo dados consolidados

**Usuário:** Admin do Ministério

**Fluxo:**
```
1. Login → get_allowed_churches_for_user() retorna TODAS
2. Acessa relatório consolidado
3. View NÃO usa request.igreja_ativa (intencional)
4. Loop por todas as igrejas permitidas
5. Renderiza tabela comparativa
```

---

## Troubleshooting

### Problema 1: Seletor não aparece para professor

**Sintoma:** Professor faz login mas não vê seletor de igreja

**Diagnóstico:**
```python
# No Django shell
user = User.objects.get(username='professor')

# 1. Verifica se tem perfil
print(hasattr(user, 'perfil'))  # Deve ser True
print(user.perfil.ministerio)   # Deve retornar Ministerio

# 2. Verifica se é membro
print(hasattr(user, 'membro_secretaria'))  # Deve ser True
print(user.membro_secretaria.igreja)       # Deve retornar Igreja

# 3. Testa função
from financeiro.utils import get_allowed_churches_for_user
igrejas = get_allowed_churches_for_user(user)
print(igrejas)  # Deve retornar QuerySet com 1 igreja
```

**Soluções:**
- Se perfil não existe: Criar PerfilUsuario
- Se membro_secretaria não existe: Vincular `Pessoa.usuario = user`
- Se igreja é None: Definir `Pessoa.igreja`

### Problema 2: Middleware não define request.igreja_ativa

**Sintoma:** `request.igreja_ativa` é None mesmo com seletor visível

**Diagnóstico:**
```python
# Na view, adicione debug temporário
print(f"Igreja ativa ID na sessão: {request.session.get('igreja_ativa_id')}")
print(f"Igreja ativa no request: {getattr(request, 'igreja_ativa', 'NÃO DEFINIDO')}")

from financeiro.utils import get_allowed_churches_for_user
allowed = get_allowed_churches_for_user(request.user)
print(f"Igrejas permitidas: {list(allowed.values_list('id', 'nome_igreja'))}")
```

**Soluções:**
- Se sessão tem ID mas request.igreja_ativa é None: Igreja não está em allowed
- Se sessão vazia: Middleware deve auto-selecionar se allowed.count() == 1
- Verificar se middleware está na lista MIDDLEWARE do settings.py

### Problema 3: Usuário vê dados de outra igreja

**Sintoma:** Professor da AD Serafim vê turmas da AD Itamacuri

**Diagnóstico:**
```python
# Verificar lógica da view
# A view está usando request.igreja_ativa corretamente?

# Exemplo ERRADO:
turmas = Turma.objects.all()  # ← Sem filtro!

# Exemplo CORRETO:
turmas = Turma.objects.all()
if not is_secretaria:
    turmas = turmas.filter(id__in=get_turmas_professor(request.user))
```

**Soluções:**
- Adicionar filtro por `request.igreja_ativa` em views de secretaria
- OU usar permissões granulares em views EBD (get_turmas_professor)

### Problema 4: Migration falha ao adicionar igreja em MembroCargo

**Sintoma:** Se tentar adicionar campo `igreja` em MembroCargo no futuro

**Solução:**
```python
# 1. Adicione campo null=True, blank=True
class MembroCargo(models.Model):
    igreja = models.ForeignKey(Igreja, null=True, blank=True)

# 2. Makemigrations
# 3. Crie data migration para popular

from django.db import migrations

def populate_igreja(apps, schema_editor):
    MembroCargo = apps.get_model('secretaria', 'MembroCargo')
    for mc in MembroCargo.objects.filter(igreja__isnull=True):
        mc.igreja = mc.membro.igreja
        mc.save()

class Migration(migrations.Migration):
    dependencies = [('secretaria', '0XXX_add_igreja_field')]
    operations = [migrations.RunPython(populate_igreja)]

# 4. Depois, remova null=True se quiser tornar obrigatório
```

---

## 🎓 Sumário para IA

**O que este sistema faz:**
- Define quais igrejas um usuário pode acessar baseado em seu papel
- Permite trocar entre igrejas (se tiver acesso a múltiplas)
- Filtra automaticamente dados pela igreja selecionada

**Hierarquia de permissões:**
Admin Org > Finanças > Membros > Outros

**Decisões importantes:**
- Pessoa tem UMA igreja (onde é membro)
- Cargos são da igreja do membro (sem campo igreja em MembroCargo)
- Seletor sempre aparece (mesmo com 1 opção)
- Permissões granulares (EBD) coexistem com seletor global

**Próximos passos (se necessário):**
- Adicionar campo `igreja` em MembroCargo (múltiplas igrejas)
- Mover função para `core/` (melhor organização)
- Adicionar cache (performance)

**Para modificar no futuro:**
Sempre mantenha retrocompatibilidade. Use deprecation warnings antes de remover código antigo.
