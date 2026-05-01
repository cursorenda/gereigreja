# Guia de Decorators de Segurança - GereIgreja

**Versão:** 1.8.80  
**Última atualização:** 01/05/2026

---

## 📚 Índice

1. [Visão Geral](#visão-geral)
2. [Decorators Disponíveis](#decorators-disponíveis)
3. [Padrões de Uso](#padrões-de-uso)
4. [Exemplos Práticos](#exemplos-práticos)
5. [Migrando Código Antigo](#migrando-código-antigo)
6. [Checklist de Segurança](#checklist-de-segurança)

---

## 🎯 Visão Geral

Este documento descreve os decorators de segurança disponíveis no GereIgreja e como usá-los corretamente para proteger views.

### Princípios de Segurança

1. **Autenticação primeiro:** Sempre use `@login_required` como primeira camada
2. **Permissão explícita:** Use decorators específicos, não verificações manuais
3. **Falha segura:** Sempre lance `PermissionDenied`, nunca redirecione para login
4. **Mensagens claras:** Usuário deve entender por que não tem acesso

### Localização dos Decorators

Todos os decorators customizados estão em: **`core/decorators.py`**

### Padrão Vigente (2026)

Para views de modulo/pagina, o padrão principal do projeto e:

1. `@login_required`
2. `@page_access_required('<chave>')`
3. Regra centralizada em `contas/page_permissions.py` (`PAGE_ACCESS_RULES`)

**Exemplo recomendado:**
```python
from django.contrib.auth.decorators import login_required
from core.decorators import page_access_required

@login_required
@page_access_required('financeiro')
def listar_transacoes(request):
    return render(request, 'financeiro/lista.html')
```

Decorators como `@user_passes_test_or_403` e `@check_permission` permanecem para casos legados ou regras muito especificas.

---

## 🔧 Decorators Disponíveis

### 1. `@login_required` (Django Built-in)

**Propósito:** Requer que o usuário esteja autenticado.

**Quando usar:** 
- ✅ Primeira linha de defesa em TODAS as views não-públicas
- ✅ APIs, AJAX endpoints, dashboards

**Comportamento:**
- Se não autenticado → redireciona para `settings.LOGIN_URL`
- Se autenticado → passa para o próximo decorator/view

**Exemplo:**
```python
from django.contrib.auth.decorators import login_required

@login_required
def minha_view(request):
    return render(request, 'template.html')
```

---

### 2. `@user_passes_test_or_403(test_func)`

**Propósito:** Verifica se usuário passa em um teste customizado. **Lança 403** em vez de redirecionar.

**Quando usar:**
- ✅ Verificações de grupo específicas
- ✅ Lógica customizada de permissão
- ✅ Sempre que `@user_passes_test` do Django for insuficiente

**Comportamento:**
- Aplica `@login_required` automaticamente
- Executa `test_func(request.user)`
- Se `False` → lança `PermissionDenied` (mostra 403.html)
- Se `True` → executa a view normalmente

**Assinatura:**
```python
def user_passes_test_or_403(test_func):
    """
    Versão do user_passes_test que lança PermissionDenied em vez de redirecionar.
    
    Args:
        test_func: Função que recebe user e retorna bool
        
    Returns:
        Decorator que aplica @login_required + test_func
        
    Raises:
        PermissionDenied: Se test_func retorna False
    """
```

**Exemplo:**
```python
from core.decorators import user_passes_test_or_403

from contas.constants import user_tem_qualquer_grupo, PASTOR_LOCAL, ADMIN_MINISTERIO
def is_pastor_or_admin(user):
    return user_tem_qualquer_grupo(user, [PASTOR_LOCAL, ADMIN_MINISTERIO])

@user_passes_test_or_403(is_pastor_or_admin)
def view_restrita(request):
    return render(request, 'restrita.html')
```

---

### 3. `@admin_ministerio_required`

**Propósito:** Requer que usuário seja Admin Ministerio ou superuser.

**Quando usar:**
- ✅ Gestão de usuários e convites
- ✅ Configurações ministeriais (criar/editar/excluir igrejas)
- ✅ Operações que afetam todo o ministério

**Comportamento:**
- Aplica `@user_passes_test_or_403(user_is_admin)` automaticamente
- Superusers sempre passam
- Usuários no grupo "Admin Ministerio" passam
- Outros → `PermissionDenied` (403)

**Assinatura:**
```python
def admin_ministerio_required(view_func):
    """
    Requer Admin Ministerio ou superuser para acessar a view.
    
    Usa user_is_admin() de contas.constants para verificar.
    """
```

**Exemplo:**
```python
from core.decorators import admin_ministerio_required

@admin_ministerio_required
def editar_ministerio(request):
    # Apenas Admin Ministerio ou superuser
    ministerio = get_ministerio_or_error(request)
    # ...
```

---

### 4. `@secretaria_ebd_required`

**Propósito:** Requer que usuário seja Superintendente EBD ou Secretaria EBD.

**Quando usar:**
- ✅ Chamada de presença
- ✅ Gestão de turmas e alunos  
- ✅ Geração de cronogramas
- ✅ Relatórios administrativos EBD

**Comportamento:**
- Aplica `@login_required` + verifica grupos EBD
- Superusers sempre passam
- Usuários nos grupos "Superintendente EBD" ou "Secretaria EBD" passam
- Outros → `PermissionDenied` (403)

**Exemplo:**
```python
from core.decorators import secretaria_ebd_required

@secretaria_ebd_required
def chamada_presenca(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    # ...
```

---

### 5. ~~`@secretaria_dashboard_required`~~ (DEPRECIADO)

> **Depreciado em v1.9.0.** Este decorator foi substituído por `@page_access_required('dashboard_secretaria')` centralizado em `PAGE_ACCESS_RULES`. O decorator ainda existe em `core/decorators.py` por compatibilidade mas **não deve ser usado em código novo**.
>
> **Substituto:** `@page_access_required('dashboard_secretaria')`

**Propósito original:** Requer que usuário seja parte da liderança operacional ou ministerial para acessar dashboard analítico da secretaria.

**Quando usar:**
- ~~✅ Dashboard analítico da secretaria (`/secretaria/dashboard/`)~~
- ✅ Relatórios estratégicos com dados sensíveis
- ✅ Análise de tendências e métricas gerenciais
- ✅ Visualizações que não são necessárias para operações do dia a dia

**Comportamento:**
- Aplica `@login_required` + verifica se usuário está em `GRUPOS_OPERACIONAL`
- Superusers sempre passam
- Usuários em grupos operacionais passam (Secretário Local, Tesoureiro, Superintendente EBD, Pastores, Admin)
- Equipes (Eventos, Mídia, Recepção) e Professores EBD → `PermissionDenied` (403)

**Grupos permitidos (GRUPOS_OPERACIONAL):**
- Secretário Local
- Tesoureiro
- Superintendente EBD
- Pastor Local
- Pastor Regional
- Admin Ministerio
- Secretaria Ministerial
- Tesouraria Ministerial

**Grupos bloqueados (GRUPOS_EQUIPES):**
- Equipe de Eventos
- Equipe de Mídia
- Equipe de Recepção
- Professor EBD
- Secretaria EBD (operacional, não precisa de análise estratégica)

**Exemplo:**
```python
from core.decorators import secretaria_dashboard_required

@secretaria_dashboard_required
def dashboard(request):
    # Dashboard analítico com gráficos de evolução, 
    # tendências e dados sensíveis
    # Apenas liderança/secretaria acessam
    ministerio = get_ministerio_or_error(request)
    # ... métricas estratégicas
    return render(request, 'secretaria/dashboard.html', context)
```

**Diferença com página inicial:**
```python
# /secretaria/ (index) - Acesso amplo (todos staff)
@login_required  # Qualquer staff acessa
def index(request):
    # Ações rápidas do dia a dia
    # Botões: cadastrar pessoa, ver agenda, etc.
    ...

# /secretaria/dashboard/ - Acesso restrito (só liderança)
@secretaria_dashboard_required  # Só GRUPOS_OPERACIONAL
def dashboard(request):
    # Análise estratégica com dados sensíveis
    # Gráficos de crescimento, declínio, tendências
    ...
```

---

### 6. `@check_permission(permission_func)`

**Propósito:** Verifica permissão usando função customizada. Usado principalmente no app **financeiro**.

**Quando usar:**
- ✅ Módulo financeiro (receitas, despesas, contas)
- ✅ Permissões que dependem de escopo (ministerial vs local)
- ✅ Lógica complexa envolvendo igrejas permitidas

**Comportamento:**
- Aplica `@login_required` automaticamente
- Executa `permission_func(request.user)`
- Se `False` → lança `PermissionDenied`
- Se `True` → executa view

**Funções de Permissão Financeiras:**
```python
# financeiro/utils.py
has_finance_view_permission(user)    # Visualizar dados financeiros
has_finance_edit_permission(user)    # Editar/criar/excluir
is_finance_leader(user)              # Tesouraria ministerial
```

**Exemplo:**
```python
from core.decorators import check_permission
from financeiro.utils import has_finance_edit_permission

@check_permission(has_finance_edit_permission)
def excluir_receita(request, pk):
    # Apenas quem pode editar pode excluir
    ministerio = get_ministerio_or_error(request)
    # ...
```

---

### 7. `@verificar_assinatura_valida`

**Propósito:** Verifica se assinatura do ministério está ativa.

**Quando usar:**
- ✅ Funcionalidades premium
- ✅ Módulos que requerem assinatura ativa
- ✅ Após `@login_required`, antes de outros decorators

**Comportamento:**
- Verifica se `ministerio.assinatura_ativa == True`
- Se inativa → redireciona para página de assinatura
- Se ativa → continua execução

**Exemplo:**
```python
from core.decorators import verificar_assinatura_valida

@login_required
@verificar_assinatura_valida
def funcionalidade_premium(request):
    # Requer assinatura ativa
    return render(request, 'premium.html')
```

---

## 📖 Padrões de Uso

### Padrão 0: Permissões Granulares (Customizadas por View)

```python
from django.core.exceptions import PermissionDenied

# Função helper que verifica permissão específica
def pode_acessar_recurso(user, recurso):
    """Verifica se usuário pode acessar recurso específico."""
    # Superuser sempre pode
    if user.is_superuser:
        return True
    
    # Administradores gerais podem
    from contas.constants import user_tem_grupo, ADMIN_MINISTERIO
    if user_tem_grupo(user, ADMIN_MINISTERIO):
        return True
    
    # Lógica customizada: usuário é "dono" do recurso
    try:
        return recurso.criado_por == user.perfil.membro
    except Exception:
        return False

@login_required
def acessar_recurso(request, recurso_id):
    """View com verificação de permissão customizada."""
    recurso = get_object_or_404(Recurso, pk=recurso_id)
    
    # Verifica permissão inline
    if not pode_acessar_recurso(request.user, recurso):
        raise PermissionDenied(
            "Você não tem permissão para acessar este recurso. "
            "Apenas administradores ou o criador podem acessar."
        )
    
    # Resto da lógica da view
    return render(request, 'recurso.html', {'recurso': recurso})
```

**Quando usar:**
- ✅ Permissões dependem do objeto específico (não apenas do grupo do usuário)
- ✅ Lógica complexa: "professor DA turma", "criador DO evento", etc.
- ✅ Múltiplas condições que variam por contexto

**Exemplo real: Escola Bíblica - Professor pode acessar chamada da própria turma**
```python
# escola_biblica/views.py
from secretaria.models import MembroCargo

def pode_acessar_chamada_turma(user, turma):
    """Professor pode acessar apenas chamada de SUA turma."""
    if user.is_superuser:
        return True
    
    # Secretaria EBD acessa todas as turmas
    if user.groups.filter(name__in=['Secretaria EBD', 'Superintendente EBD']).exists():
        return True
    
    # Verifica se é professor DESTA turma específica
    try:
        perfil = user.perfil
        if hasattr(perfil, 'membro') and perfil.membro:
            membro = perfil.membro
            # Está nos membros da turma?
            if membro in turma.membros.all():
                # Tem cargo de professor EBD ativo?
                cargo_ativo = MembroCargo.objects.filter(
                    membro=membro,
                    cargo__is_ebd=True,
                    cargo__nome__icontains='professor',
                    data_fim__isnull=True
                ).exists()
                return cargo_ativo
    except Exception:
        pass
    
    return False

@login_required
def chamada_presenca(request, turma_id):
    """Chamada: secretaria EBD OU professor da turma."""
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Verificação granular por objeto
    if not pode_acessar_chamada_turma(request.user, turma):
        raise PermissionDenied(
            "Você não tem permissão para acessar a chamada desta turma."
        )
    
    # ... resto da lógica
```

### Padrão 1: View Pública

```python
def landing_page(request):
    """Sem decorators - acessível por qualquer um"""
    return render(request, 'landing.html')
```

### Padrão 2: View Autenticada (qualquer usuário logado)

```python
@login_required
def meu_perfil(request):
    """Qualquer usuário autenticado pode acessar"""
    return render(request, 'perfil.html')
```

### Padrão 3: View com Grupo Específico

```python
from core.decorators import user_passes_test_or_403

def is_secretario(user):
    return user.groups.filter(name='Secretario Local').exists()

@user_passes_test_or_403(is_secretario)
def gestao_membros(request):
    """Apenas secretários"""
    return render(request, 'gestao.html')
```

### Padrão 4: View Administrativa

```python
from core.decorators import admin_ministerio_required

@admin_ministerio_required
def gerenciar_usuarios(request):
    """Apenas Admin Ministerio"""
    usuarios = User.objects.filter(perfil__ministerio=request.user.perfil.ministerio)
    return render(request, 'usuarios.html', {'usuarios': usuarios})
```

### Padrão 5: Múltiplos Decorators (ordem importa!)

```python
from core.decorators import verificar_assinatura_valida, user_passes_test_or_403

def is_tesoureiro(user):
    return user.groups.filter(name='Tesoureiro').exists()

@login_required                      # 1º: Autentica
@verificar_assinatura_valida         # 2º: Verifica assinatura
@user_passes_test_or_403(is_tesoureiro)  # 3º: Verifica grupo
def relatorio_financeiro(request):
    """Ordem: autenticação → assinatura → permissão"""
    return render(request, 'relatorio.html')
```

**⚠️ IMPORTANTE:** Ordem dos decorators:
1. `@login_required` (sempre primeiro)
2. `@verificar_assinatura_valida` (se aplicável)
3. `@user_passes_test_or_403` ou `@admin_ministerio_required` (verificação de grupo)

---

## 💡 Exemplos Práticos

### Exemplo 1: API AJAX

```python
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@login_required
@require_GET
def autocomplete_membros(request):
    """API para autocomplete - requer login"""
    termo = request.GET.get('q', '')
    membros = Membro.objects.filter(nome__icontains=termo)[:10]
    results = [{'id': m.id, 'nome': m.nome} for m in membros]
    return JsonResponse({'results': results})
```

### Exemplo 2: View de Exclusão

```python
from core.decorators import user_passes_test_or_403

def pode_excluir_eventos(user):
    """Apenas admin e líderes de eventos"""
    return user.groups.filter(
        name__in=['Admin Ministerio', 'Lider Eventos']
    ).exists()

@user_passes_test_or_403(pode_excluir_eventos)
def excluir_evento(request, pk):
    """Apenas usuários autorizados podem excluir"""
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento excluído!')
        return redirect('eventos:lista')
    return render(request, 'confirmar_exclusao.html', {'evento': evento})
```

### Exemplo 3: View com Lógica de Igreja

```python
from core.decorators import user_passes_test_or_403
from core.utils import get_ministerio_or_error
from secretaria.utils import get_allowed_churches_for_membros

def pode_ver_relatorio(user):
    """Secretários e pastores podem ver relatórios"""
    return user.groups.filter(
        name__in=['Secretario Local', 'Pastor Local', 'Admin Ministerio']
    ).exists()

@user_passes_test_or_403(pode_ver_relatorio)
def relatorio_membros(request):
    """Relatório filtrado por igrejas do usuário"""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    
    membros = Membro.objects.filter(igreja__in=allowed_churches)
    
    return render(request, 'relatorio.html', {
        'membros': membros,
        'igrejas': allowed_churches
    })
```

---

## 🔄 Migrando Código Antigo

### Padrão Antigo (❌ Inseguro)

```python
@login_required
def minha_view(request):
    # ❌ Verificação manual
    if not user_is_admin(request.user):
        messages.error(request, "Sem permissão")
        return redirect('login')  # ❌ Confuso!
    
    # Resto do código...
    return render(request, 'template.html')
```

**Problemas:**
1. Usuário já está logado, mas vê tela de login
2. Fácil esquecer a verificação
3. Código duplicado em várias views
4. Difícil auditar segurança

### Padrão Novo (✅ Seguro)

```python
from core.decorators import admin_ministerio_required

@admin_ministerio_required  # ✅ Declarativo e seguro
def minha_view(request):
    # ✅ Sem verificações manuais
    # ✅ Lança PermissionDenied automaticamente
    # ✅ Mostra página 403.html customizada
    
    # Resto do código...
    return render(request, 'template.html')
```

**Benefícios:**
1. ✅ Página 403 clara explicando o problema
2. ✅ Impossível esquecer (decorador no topo)
3. ✅ Código limpo, sem validações
4. ✅ Fácil auditar (grep por decorators)

### Script de Migração

Para encontrar views antigas:

```bash
# Buscar padrão antigo
grep -r "return redirect('login')" --include="*.py" .

# Buscar verificações manuais
grep -r "if not user_is_admin" --include="*.py" .

# Verificar todas views com @login_required sem outros decorators
grep -B2 "@login_required" --include="*.py" . | grep "def "
```

---

## ✅ Checklist de Segurança

Ao criar ou revisar uma view, use este checklist:

### Views Públicas
- [ ] Confirmar que view DEVE ser pública
- [ ] Documentar no docstring: `"""View pública - sem autenticação""""`
- [ ] Não expor dados sensíveis

### Views Autenticadas
- [ ] Adicionar `@login_required`
- [ ] Se tem operações CRUD, adicionar verificação de permissão
- [ ] Se é AJAX/API, adicionar `@require_GET` ou `@require_POST`

### Views com Permissões
- [ ] Existe chave de acesso para a funcionalidade em `PAGE_ACCESS_RULES`?
- [ ] Usar `@page_access_required('<chave>')` quando houver chave equivalente
- [ ] Se nao houver chave, justificar uso de decorator legado (`@user_passes_test_or_403`/`@check_permission`)
- [ ] **NUNCA** usar `return redirect('login')` em verificações
- [ ] Documentar grupos permitidos no docstring

### Views Administrativas
- [ ] Usar `@admin_ministerio_required` ou similar
- [ ] Verificar escopo (ministerial vs local)
- [ ] Adicionar logs para operações sensíveis

### Views Financeiras
- [ ] Preferir `@page_access_required('financeiro')`
- [ ] Usar `@check_permission` apenas em trechos ainda nao migrados
- [ ] Verificar escopo de igrejas permitidas
- [ ] Validar dados antes de salvar

### Testes
- [ ] Testar como usuário sem permissão (deve ver 403)
- [ ] Testar como usuário com permissão (deve funcionar)
- [ ] Testar logout → login para refresh de permissões
- [ ] Verificar mensagens de erro na página 403

---

## 🐛 Troubleshooting

### Problema: View redireciona para login mesmo com @login_required

**Causa:** Provavelmente há verificação manual com `redirect('login')` no código.

**Solução:**
```python
# Remover:
if not tem_permissao(request.user):
    return redirect('login')

# Adicionar decorator padrão:
@page_access_required('chave_da_pagina')

# Ou, se não houver chave equivalente ainda:
@user_passes_test_or_403(tem_permissao)
```

### Problema: Página 403 não aparece customizada

**Causa:** Template 403.html não existe ou erro nele.

**Verificar:**
1. Arquivo existe em `templates/403.html`
2. Extends base corretamente
3. Variável `user` está disponível no contexto

### Problema: ImportError ao usar decorators

**Causa:** Import circular ou caminho errado.

**Solução:**
```python
# ✅ Correto
from core.decorators import user_passes_test_or_403, admin_ministerio_required

# ❌ Errado
from decorators import user_passes_test_or_403
```

### Problema: Superuser não passa em verificações

**Causa:** Função de teste não verifica `is_superuser`.

**Solução:**
```python
def minha_permissao(user):
    # ✅ Sempre verificar superuser primeiro
    return user.is_superuser or user.groups.filter(...).exists()
```

---

## 📚 Referências

- **Django Docs:** [User authentication](https://docs.djangoproject.com/en/5.0/topics/auth/)
- **Projeto:** `core/decorators.py` - código fonte dos decorators
- **Projeto:** `contas/constants.py` - funções helper de grupos
- **Projeto:** `templates/403.html` - template de erro customizado

---

**Última atualização:** 13/02/2026  
**Mantido por:** Equipe GereIgreja
