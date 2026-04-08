"""
EXEMPLO DE REFATORAÇÃO: secretaria/views.py - dashboard()

Este arquivo mostra ANTES e DEPOIS da aplicação do decorator @inject_igrejas_permitidas.

NÃO substitua a view original ainda - use este arquivo como referência/comparação.
"""

# ========================================
# ANTES - Código Original (linhas 2312-2450)
# ========================================

def dashboard_ANTES(request):
    from datetime import date, timedelta
    hoje_data = date.today()

    if request.user.is_superuser:
        return redirect('admin:index')

    from contas.constants import user_has_permission_level_or_higher, MEMBRO_COMUM
    if user_has_permission_level_or_higher(request.user, MEMBRO_COMUM) and not request.user.is_staff:
        return redirect('secretaria:portal_membro')

    ministerio = get_ministerio_or_error(request)
    allowed_churches_secretaria = get_allowed_churches_for_membros(request.user, ministerio)
    titulo_contextual = f"Visão Geral - {ministerio.nome_fantasia}"
    membros_para_relatorios = Membro.objects.none()
    
    total_pessoas_igreja = 0

    # ❌ PROBLEMA: Lógica if/elif/else repetida múltiplas vezes
    if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria:
        total_pessoas_igreja = Membro.objects.filter(igreja=request.igreja_ativa).count()
        membros_para_relatorios = Membro.objects.filter(
            igreja=request.igreja_ativa,
            tipo_pessoa__nome__iexact="Membro",
            status_pessoa__nome__iexact="Ativo"
        )
        titulo_contextual = f"Visão Geral - Igreja: {request.igreja_ativa.nome_igreja}"
    elif allowed_churches_secretaria.exists():
        total_pessoas_igreja = Membro.objects.filter(igreja__in=allowed_churches_secretaria).count()
        membros_para_relatorios = Membro.objects.filter(
            igreja__in=allowed_churches_secretaria,
            tipo_pessoa__nome__iexact="Membro",
            status_pessoa__nome__iexact="Ativo"
        )
        titulo_contextual += " (Consolidado)"
    elif is_admin_org(request.user):
        total_pessoas_igreja = Membro.objects.filter(igreja__ministerio=ministerio).count()
        membros_para_relatorios = Membro.objects.filter(
            igreja__ministerio=ministerio,
            tipo_pessoa__nome__iexact="Membro",
            status_pessoa__nome__iexact="Ativo"
        )
        titulo_contextual += " (Ministério)"

    # ❌ PROBLEMA: Mesma lógica repetida NOVAMENTE para gráficos
    membros_base_para_grafico_status = (
        Membro.objects.filter(igreja=request.igreja_ativa) if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria
        else Membro.objects.filter(igreja__in=allowed_churches_secretaria) if allowed_churches_secretaria.exists()
        else Membro.objects.filter(igreja__ministerio=ministerio) if is_admin_org(request.user)
        else Membro.objects.none()
    )

    # ... resto do código ...

# ========================================
# DEPOIS - Código Refatorado
# ========================================

from core.decorators import inject_igrejas_permitidas

@inject_igrejas_permitidas  # ✅ Decorator injeta request.igrejas_permitidas
def dashboard_DEPOIS(request):
    from datetime import date, timedelta
    hoje_data = date.today()

    if request.user.is_superuser:
        return redirect('admin:index')

    from contas.constants import user_has_permission_level_or_higher, MEMBRO_COMUM
    if user_has_permission_level_or_higher(request.user, MEMBRO_COMUM) and not request.user.is_staff:
        return redirect('secretaria:portal_membro')

    ministerio = get_ministerio_or_error(request)
    
    # ✅ SOLUÇÃO: Uma única linha substitui todo o if/elif/else
    # request.igrejas_permitidas já está disponível pelo decorator!
    total_pessoas_igreja = Membro.objects.filter(igreja__in=request.igrejas_permitidas).count()
    
    membros_para_relatorios = Membro.objects.filter(
        igreja__in=request.igrejas_permitidas,
        tipo_pessoa__nome__iexact="Membro",
        status_pessoa__nome__iexact="Ativo"
    )
    
    # ✅ Simplificado: Título contextual baseado no escopo
    if request.igreja_ativa:
        titulo_contextual = f"Visão Geral - Igreja: {request.igreja_ativa.nome_igreja}"
    else:
        titulo_total = request.igrejas_permitidas.count()
        titulo_contextual = f"Visão Geral - {ministerio.nome_fantasia} ({titulo_total} igrejas)"
    
    # ✅ SOLUÇÃO: Mesma variável para gráficos - sem duplicação
    membros_base_para_grafico_status = Membro.objects.filter(igreja__in=request.igrejas_permitidas)

    # ... resto do código permanece igual ...
    
    # Os gráficos e estatísticas seguem normalmente
    status_data_qs = membros_base_para_grafico_status.values('status_pessoa__nome').annotate(total=Count('chave')).order_by('status_pessoa__nome')
    # ... etc ...


# ========================================
# COMPARAÇÃO DE MÉTRICAS
# ========================================

"""
ANTES:
- 23 linhas de código de escopo
- Lógica if/elif/else repetida 2x
- Difícil de manter
- Alto risco de bugs

DEPOIS:
- 1 decorator
- 3 linhas de queries simplificadas
- Fácil de manter
- Baixo risco de bugs

REDUÇÃO: 23 linhas → 4 linhas (reduction: 82%)
"""


# ========================================
# OUTROS EXEMPLOS DE REFATORAÇÃO NESTA MESMA VIEW
# ========================================

# Linha ~2536 (gráfico de tipos) - ANTES:
membros_para_grafico_tipo_ANTES = (
    Membro.objects.filter(igreja=request.igreja_ativa)
    if request.igreja_ativa
    else Membro.objects.filter(igreja__in=allowed_churches_secretaria)
    if allowed_churches_secretaria.exists()
    else Membro.objects.filter(igreja__ministerio=ministerio)
)


# Linha ~2536 (gráfico de tipos) - DEPOIS:
membros_para_grafico_tipo_DEPOIS = Membro.objects.filter(igreja__in=request.igrejas_permitidas)
# Redução: 7 linhas → 1 linha


# Linha ~2587 (estatísticas extras) - ANTES:
if request.igreja_ativa:
    total_cargos = Cargo.objects.filter(membrocargo__membro__igreja=request.igreja_ativa).distinct().count()
    total_grupos_casa = GrupoCasa.objects.filter(igreja=request.igreja_ativa).count()
elif allowed_churches_secretaria.exists():
    total_cargos = Cargo.objects.filter(membrocargo__membro__igreja__in=allowed_churches_secretaria).distinct().count()
    total_grupos_casa = GrupoCasa.objects.filter(igreja__in=allowed_churches_secretaria).count()
else:
    total_cargos = Cargo.objects.filter(membrocargo__membro__igreja__ministerio=ministerio).distinct().count()
    total_grupos_casa = GrupoCasa.objects.filter(igreja__ministerio=ministerio).count()


# Linha ~2587 (estatísticas extras) - DEPOIS:
total_cargos = Cargo.objects.filter(membrocargo__membro__igreja__in=request.igrejas_permitidas).distinct().count()
total_grupos_casa = GrupoCasa.objects.filter(igreja__in=request.igrejas_permitidas).count()
# Redução: 8 linhas → 2 linhas


# ========================================
# TOTAL NA VIEW DASHBOARD
# ========================================

"""
IMPACTO TOTAL NA VIEW dashboard():

ANTES:
- ~60 linhas de código de escopo
- Lógica repetida 5-6 vezes
- Complexidade: ALTA
- Manutenibilidade: BAIXA

DEPOIS:
- ~12 linhas de queries simples
- 1 decorator reutilizável
- Complexidade: BAIXA
- Manutenibilidade: ALTA

REDUÇÃO TOTAL: ~60 linhas → ~12 linhas (reduction: 80%)
TEMPO DE REFATORAÇÃO: ~10 minutos
TEMPO ECONOMIZADO EM FUTURAS MUDANÇAS: Horas
"""
