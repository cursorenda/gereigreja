# 🤖 AI Context: Seletor Global de Igreja

> **Para:** Agentes de IA trabalhando no código Gereigreja  
> **Atualizado:** 13/02/2026  
> **Versão:** v1.2.2

## 🎯 TL;DR

Sistema de **isolamento multi-tenant por igreja** onde cada usuário vê apenas dados da(s) igreja(s) que tem permissão.

**Função central:** `financeiro/utils.py::get_allowed_churches_for_user(user) -> QuerySet[Igreja]`

**Hierarquia:** Admin Org → Finanças → Membros → Outros

**Regra:** Pessoa = 1 igreja (onde é membro). Cargos = da igreja do membro.

---

## 📊 Modelo Mental Rápido

```
User
  └─ perfil (PerfilUsuario)
      └─ ministerio (Ministerio)
          └─ igrejas (Igreja)  [1..N]

User
  └─ membro_secretaria (Pessoa)
      └─ igreja (Igreja)  [1 apenas]
```

**Fluxo:**
1. Request → Middleware chama `get_allowed_churches_for_user()`
2. Retorna QuerySet de igrejas permitidas
3. Define `request.igreja_ativa` baseado na sessão
4. Views filtram dados por `request.igreja_ativa`

---

## 🔑 Pontos-Chave para IA

### 1. Não confundir "igreja permitida" com "igreja ativa"

```python
# PERMITIDAS: todas que o usuário PODE acessar
allowed = get_allowed_churches_for_user(user)  # QuerySet[Igreja]

# ATIVA: a que está SELECIONADA no momento
request.igreja_ativa  # Igreja | None
```

### 2. Sempre verificar hasattr antes de usar

```python
# ✅ CORRETO
if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
    filtrar_por_igreja()

# ❌ ERRADO (quebra em testes sem middleware)
if request.igreja_ativa:
    filtrar_por_igreja()
```

### 3. Usar related_names corretos

```python
user.perfil               # PerfilUsuario
user.membro_secretaria    # Pessoa (not user.pessoa!)
igreja.ministerio         # Ministerio
ministerio.assinatura     # AssinaturaMinisterio
```

### 4. Igreja em subordinadas é RECURSIVO

```python
# Pode ser caro! Considerar cache
def get_subordinadas_recursivamente(igreja_obj):
    # Percorre árvore de igrejas (Sede → Regional → Congregação)
    # Pode ter loops se hierarquia circular
```

---

## 🧩 Quando Usar vs Não Usar

### ✅ USE `request.igreja_ativa` quando:

- View mostra dados de UMA igreja (relatório local)
- Listagem de membros/turmas/eventos de uma igreja
- CRUD que pertence a uma igreja específica

```python
@login_required
def membro_list(request):
    membros = Membro.objects.all()
    if request.igreja_ativa:
        membros = membros.filter(igreja=request.igreja_ativa)
    return render(request, 'membros.html', {'membros': membros})
```

### ❌ NÃO USE quando:

- View mostra dados CONSOLIDADOS (múltiplas igrejas)
- Relatório comparativo entre igrejas
- Admin vendo dados globais

```python
@login_required
def relatorio_consolidado(request):
    # Itera por TODAS as permitidas, não usa igreja_ativa
    igrejas = get_allowed_churches_for_user(request.user)
    
    dados = []
    for igreja in igrejas:
        dados.append({
            'igreja': igreja.nome_igreja,
            'total_membros': Membro.objects.filter(igreja=igreja).count()
        })
    return render(request, 'consolidado.html', {'dados': dados})
```

---

## 🔧 Padrões de Código

### Padrão 1: View com filtro de igreja

```python
@login_required
@verificar_assinatura_valida
def minha_view(request):
    # 1. Query base
    objetos = MinhaModel.objects.all()
    
    # 2. Filtro de permissão (se necessário)
    if not user_is_admin(request.user):
        objetos = objetos.filter(responsavel=request.user)
    
    # 3. Filtro de igreja
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        objetos = objetos.filter(igreja=request.igreja_ativa)
    
    return render(request, 'template.html', {'objetos': objetos})
```

### Padrão 2: View EBD com permissões granulares

```python
@login_required
@verificar_assinatura_valida
def turma_list(request):
    turmas = Turma.objects.filter(ano_letivo=ano_atual)
    
    # Permissão granular primeiro
    is_secretaria = request.user.groups.filter(
        name__in=['Secretaria EBD', 'Superintendente EBD']
    ).exists()
    
    if not is_secretaria:
        # Professor: apenas suas turmas
        turmas = turmas.filter(id__in=get_turmas_professor(request.user))
    else:
        # Secretaria: filtra por igreja ativa
        if request.igreja_ativa:
            turmas = turmas.filter(membros__igreja=request.igreja_ativa).distinct()
    
    return render(request, 'turmas.html', {'turmas': turmas})
```

### Padrão 3: Testes sem middleware

```python
from django.test import TestCase, override_settings

@override_settings(
    MIDDLEWARE=[
        # Lista SEM ActiveChurchMiddleware
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]
)
class MyTestCase(TestCase):
    def test_view_sem_middleware(self):
        response = self.client.get('/url/')
        # request.igreja_ativa será None
        self.assertEqual(response.status_code, 200)
```

---

## 🚨 Armadilhas Comuns

### Armadilha 1: N+1 Queries

```python
# ❌ RUIM (1 query por turma)
for turma in turmas:
    print(turma.membros.first().igreja.nome_igreja)

# ✅ BOM (1 query total)
turmas = Turma.objects.prefetch_related('membros__igreja')
for turma in turmas:
    print(turma.membros.first().igreja.nome_igreja)
```

### Armadilha 2: Assumir que igreja_ativa sempre existe

```python
# ❌ QUEBRA se middleware desabilitado
membros = Membro.objects.filter(igreja=request.igreja_ativa)

# ✅ SEGURO
if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
    membros = Membro.objects.filter(igreja=request.igreja_ativa)
else:
    membros = Membro.objects.none()  # ou all() se admin
```

### Armadilha 3: Esquecer distinct() em ManyToMany

```python
# ❌ DUPLICATAS se turma tem múltiplos membros da mesma igreja
turmas = Turma.objects.filter(membros__igreja=igreja)

# ✅ SEM DUPLICATAS
turmas = Turma.objects.filter(membros__igreja=igreja).distinct()
```

### Armadilha 4: Confundir Pessoa.igreja com MembroCargo.igreja

```python
# ❌ CAMPO NÃO EXISTE (ainda)
cargo.igreja  # AttributeError!

# ✅ CORRETO (inferido da pessoa)
cargo.membro.igreja
```

---

## 🎭 Casos de Uso por Persona

### Persona 1: Admin do Ministério

```python
# Vê TODAS as igrejas
igrejas = get_allowed_churches_for_user(admin_user)
# → QuerySet([Igreja Sede, AD Serafim, AD Itamacuri, ...])

# Pode selecionar qualquer uma
request.igreja_ativa = qualquer_uma_da_lista
```

### Persona 2: Tesoureiro de 2 Igrejas

```python
# Vê apenas as configuradas
perfil.igrejas_permitidas.add(sede, serafim)
igrejas = get_allowed_churches_for_user(tesoureiro)
# → QuerySet([Sede, Serafim])

# Alterna entre elas via seletor
```

### Persona 3: Professor EBD

```python
# Vê apenas onde é membro
professor.membro_secretaria.igreja = serafim
igrejas = get_allowed_churches_for_user(professor)
# → QuerySet([Serafim])

# Seletor aparece mas é read-only (1 opção)
```

---

## 🔮 Evolução Futura

### Se precisar de múltiplas igrejas:

```python
# 1. Migration: adicionar campo
class MembroCargo(models.Model):
    igreja = models.ForeignKey(Igreja, null=True)

# 2. Data migration: popular
for mc in MembroCargo.objects.filter(igreja__isnull=True):
    mc.igreja = mc.membro.igreja
    mc.save()

# 3. Ajustar get_allowed_churches_for_user:
cargos = MembroCargo.objects.filter(
    membro=membro, 
    data_fim__isnull=True
).values_list('igreja_id', flat=True)

return Igreja.objects.filter(pk__in=cargos)
```

### Se precisar de cache:

```python
from django.core.cache import cache

def get_allowed_churches_for_user(user):
    cache_key = f'allowed_churches_{user.pk}'
    cached = cache.get(cache_key)
    
    if cached is not None:
        return cached
    
    # ... lógica original
    
    cache.set(cache_key, result, timeout=300)  # 5 minutos
    return result
```

---

## 📝 Checklist para Modificações

Ao modificar código relacionado ao seletor de igreja:

- [ ] Docstring atualizada?
- [ ] Testes passando (com e sem middleware)?
- [ ] Verificou N+1 queries?
- [ ] Usou `.distinct()` se ManyToMany?
- [ ] Usou `hasattr(request, 'igreja_ativa')`?
- [ ] Documentação atualizada (docs/SELETOR_IGREJA.md)?
- [ ] CHANGELOG.md atualizado?

---

## 🔗 Links Importantes

**Código:**
- `financeiro/utils.py::get_allowed_churches_for_user()` (linha 59)
- `core/middleware.py::ActiveChurchMiddleware` (linha 8)
- `escola_biblica/views.py` (exemplos de uso)

**Documentação:**
- `docs/SELETOR_IGREJA.md` - Completa (para humanos)
- `CHANGELOG.md` - Histórico de mudanças
- `README_TESTS.md` - Como testar

**Modelos:**
- `configuracao/models.py` - Ministerio, Igreja, PerfilUsuario
- `secretaria/models.py` - Pessoa, MembroCargo

**Testes:**
- `escola_biblica/tests/test_professor_permissions.py` - Exemplo completo

---

## 💡 Decisões de Design (Histórico)

**Por que igreja em financeiro/utils.py?**
- Histórico: função criada para módulo financeiro
- Evoluiu para uso global
- Mantido lá para retrocompatibilidade
- Considerar mover para `core/` no futuro

**Por que Pessoa tem 1 igreja apenas?**
- Regra de negócio: pessoa é membro de uma igreja
- Pode atuar em múltiplas, mas registro é único
- Decisão do usuário: "cargo apenas na congregação que ela atua"
- Se mudar: adicionar campo igreja em MembroCargo

**Por que seletor aparece mesmo com 1 opção?**
- UX: usuário sempre sabe onde está
- Orientação visual clara
- Escalável: interface pronta se ganhar mais igrejas
- Não é intrusivo: apenas informativo quando read-only

---

## 🎓 Para IA: Como Abordar Tasks

**Se task é...**

→ **"Adicionar filtro por igreja na view X"**
1. Verificar se view já usa `request.igreja_ativa`
2. Adicionar filtro: `queryset.filter(igreja=request.igreja_ativa)`
3. Usar `.distinct()` se ManyToMany
4. Adicionar `hasattr` check para segurança
5. Testar com e sem middleware

→ **"Usuário não vê dados de sua igreja"**
1. Verificar `get_allowed_churches_for_user(user)`
2. Confirmar `user.membro_secretaria.igreja` existe
3. Verificar middleware está ativo
4. Checar se view usa filtro correto
5. Ver logs do middleware (igreja_ativa definida?)

→ **"Permitir múltiplas igrejas por usuário"**
1. PARE: confirmar se é necessário (regra de negócio)
2. Se sim: adicionar campo `igreja` em MembroCargo
3. Migration + data migration
4. Ajustar `get_allowed_churches_for_user()`
5. Testes extensivos
6. Documentar mudança

→ **"Melhorar performance"**
1. Adicionar cache em `get_allowed_churches_for_user()`
2. Usar `select_related` / `prefetch_related`
3. Otimizar recursão de subordinadas
4. Considerar denormalization se necessário

---

**Última atualização:** 13/02/2026 por v1.2.2  
**Próxima revisão:** Quando adicionar múltiplas igrejas por pessoa
