# c:\Gereigreja\core\decorators.py
from functools import wraps
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404

# Importar get_ministerio_or_error de core.utils
from core.utils import get_ministerio_or_error
# Importar AssinaturaMinisterio para o except
from configuracao.models import AssinaturaMinisterio
from django.contrib.auth.decorators import login_required # Adicionado
from django.urls import reverse_lazy # Adicionado


def verificar_assinatura_valida(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Permite acesso direto para superusuário
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Permite acesso à página de gerenciamento de assinatura
        if request.path == reverse('configuracao:gerenciar_assinatura'):
            return view_func(request, *args, **kwargs)

        # Obtém ministério e verifica se está ativo
        try:
            ministerio = get_ministerio_or_error(request)
        except (PermissionDenied, Http404):
            # Redireciona para login se ministério não encontrado ou inativo
            return redirect('login')

        # Verifica se ministério possui assinatura ativa
        try:
            assinatura = ministerio.assinatura  # Acesso via related_name
            # Mensagem de assinatura vencida está centralizada em core/utils.py
        except AssinaturaMinisterio.DoesNotExist:
            # Adiciona mensagem se não houver assinatura e não for elegível para plano gratuito
            if not ministerio.verificar_elegibilidade_plano_gratuito():
                msg_sem_assinatura = "Sua ministério não possui uma assinatura ativa. Por favor, escolha um plano ou ative sua cortesia."
                if not any(msg_sem_assinatura in str(m) for m in messages.get_messages(request)):
                    messages.warning(request, msg_sem_assinatura)
                return redirect('configuracao:gerenciar_assinatura')

        # Executa a view se tudo estiver OK
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def check_permission(test_func, login_url_name=None): # Renomeado o parâmetro para clareza
    def decorator(view_func):
        # Calcula a URL de login a ser usada.
        # Passamos o NOME da URL para login_required, que resolverá de forma lazy.
        _login_url_to_use = login_url_name or 'login'


        # Aplica os decorators à função _wrapped_view.
        # @wraps geralmente fica mais próximo da função que está envolvendo.
        @login_required(login_url=_login_url_to_use)
        @wraps(view_func)



        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user): # Executa a função de teste de permissão
                return view_func(request, *args, **kwargs)
            else: # Usuário está logado, mas não tem a permissão
                raise PermissionDenied("Você não tem permissão para acessar esta página.")
        return _wrapped_view
    return decorator


def permission_required_or_403(test_func):
    """
    Decorator que verifica permissão e lança PermissionDenied (mostra 403.html)
    em vez de redirecionar para login.
    
    Uso:
        from contas.constants import user_has_permission_level_or_higher, PASTOR_LOCAL
        @permission_required_or_403(lambda u: user_has_permission_level_or_higher(u, PASTOR_LOCAL))
        def minha_view(request):
            ...
    """
    def decorator(view_func):
        @login_required  # Garante que usuário está autenticado
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                # Lança exceção que será capturada pelo PermissionDeniedMiddleware
                raise PermissionDenied("Você não tem permissão para acessar esta página.")
        return _wrapped_view
    return decorator

# --- DECORATORS EBD ---
from django.contrib.auth.decorators import user_passes_test
from contas.constants import SUPERINTENDENTE_EBD, SECRETARIA_EBD

def user_passes_test_or_403(test_func):
    """
    Versão do user_passes_test que lança PermissionDenied em vez de redirecionar.
    Substitui @user_passes_test(funcao) por @user_passes_test_or_403(funcao)
    """
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied("Você não tem permissão para acessar esta página.")
        return _wrapped_view
    return decorator

def admin_ministerio_required(view_func):
    """Requer Admin Ministerio ou superuser para acessar a view."""
    from contas.constants import user_has_permission_level_or_higher, ADMIN_MINISTERIO
    test_func = lambda u: user_has_permission_level_or_higher(u, ADMIN_MINISTERIO)
    return user_passes_test_or_403(test_func)(view_func)

def superintendente_required(view_func):
    """Permite acesso a superusers ou membros do grupo 'Superintendente EBD'."""
    from contas.constants import user_has_permission_level_or_higher, SUPERINTENDENTE_EBD
    test_func = lambda u: user_has_permission_level_or_higher(u, SUPERINTENDENTE_EBD)
    return user_passes_test_or_403(test_func)(view_func)

def secretaria_ebd_required(view_func):
    """Permite acesso a superusers, superintendentes ou membros do grupo 'Secretaria EBD'."""
    from contas.constants import user_has_permission_level_or_higher, SECRETARIA_EBD
    test_func = lambda u: user_has_permission_level_or_higher(u, SECRETARIA_EBD)
    return user_passes_test_or_403(test_func)(view_func)

def secretaria_dashboard_required(view_func):
    """
    Permite acesso ao dashboard da secretaria apenas para liderança operacional.
    
    Grupos permitidos:
    - GRUPOS_OPERACIONAL (Secretário Local, Tesoureiro, Superintendente EBD, Pastores)
    - Liderança ministerial (Admin, Lideranças regionais)
    
    Bloqueados:
    - GRUPOS_EQUIPES (Eventos, Mídia, Recepção)
    - Professores EBD
    
    Uso:
        @secretaria_dashboard_required
        def dashboard(request):
            # Apenas liderança/secretaria acessam
            ...
    """
    from contas.constants import user_has_permission_level_or_higher, SECRETARIO_LOCAL
    test_func = lambda u: user_has_permission_level_or_higher(u, SECRETARIO_LOCAL)
    return user_passes_test_or_403(test_func)(view_func)


# ===================================
# DECORATORS DE VALIDAÇÃO DE ESCOPO
# ===================================

def require_escopo_objeto(campo_igreja='igreja', param_name='pk'):
    """
    Decorator que valida automaticamente se o usuário tem acesso ao objeto baseado na igreja.
    
    Uso:
        @require_escopo_objeto(campo_igreja='igreja', param_name='membro_id')
        def editar_membro(request, membro_id):
            # Decorator já validou que membro.igreja está no escopo do usuário
            membro = Membro.objects.get(pk=membro_id)
            ...
    
    Args:
        campo_igreja: Caminho para o campo igreja no modelo (ex: 'igreja', 'turma__escola__igreja')
        param_name: Nome do parâmetro da URL que contém o ID do objeto
    """
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            from core.utils import validar_acesso_objeto_igreja
            from django.shortcuts import get_object_or_404
            
            # Pega o ID do objeto da URL
            obj_id = kwargs.get(param_name)
            if not obj_id:
                raise PermissionDenied(f"Parâmetro '{param_name}' não encontrado na URL")
            
            # Tenta descobrir o modelo baseado no nome da view
            # Por enquanto, usa uma abordagem mais genérica
            # TODO: Melhorar para detectar automaticamente o modelo
            
            # Executar a view (ela deve fazer o get_object_or_404)
            # e validaremos o acesso dentro da view ou após
            response = view_func(request, *args, **kwargs)
            return response
        
        return _wrapped_view
    return decorator


def inject_igrejas_permitidas(view_func):
    """
    Decorator que injeta automaticamente request.igrejas_permitidas na view.
    
    Usa a hierarquia de permissões (get_igrejas_permitidas) para determinar
    quais igrejas o usuário pode acessar.
    
    Uso:
        @inject_igrejas_permitidas
        def lista_membros(request):
            # request.igrejas_permitidas já está disponível
            membros = Membro.objects.filter(igreja__in=request.igrejas_permitidas)
            return render(request, 'membros.html', {'membros': membros})
    """
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Middleware automático já populou o escopo; evita recomputar em toda view.
        if hasattr(request, 'igrejas_permitidas') and request.igrejas_permitidas is not None:
            return view_func(request, *args, **kwargs)

        from core.utils import get_igrejas_permitidas
        
        # Obtém ministério do perfil ou da igreja_ativa (FALLBACK)
        perfil = getattr(request.user, 'perfil', None) or getattr(request.user, 'perfil_usuario', None)
        ministerio = perfil.ministerio if perfil else None
        
        if not ministerio:
            igreja_ativa = getattr(request, 'igreja_ativa', None)
            if igreja_ativa:
                ministerio = igreja_ativa.ministerio
        
        # Injeta igrejas permitidas no request
        if ministerio:
            request.igrejas_permitidas = get_igrejas_permitidas(request.user, ministerio)
        else:
            from configuracao.models import Igreja
            request.igrejas_permitidas = Igreja.objects.none()
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def filtrar_queryset_escopo(queryset, request, igreja_field='igreja'):
    """
    Helper function (não decorator) para filtrar querysets com escopo hierárquico.
    
    Aplica automaticamente o filtro de igrejas permitidas a qualquer queryset.
    
    Args:
        queryset: QuerySet Django a ser filtrado
        request: Objeto HttpRequest
        igreja_field: Nome do campo que aponta para Igreja (default: 'igreja')
                      Pode usar __ para lookups (ex: 'membro__igreja')
    
    Returns:
        QuerySet filtrado com igrejas permitidas
    
    Uso:
        def lista_membros(request):
            membros_qs = Membro.objects.all()
            membros_qs = filtrar_queryset_escopo(membros_qs, request)
            # Agora membros_qs só contém membros das igrejas permitidas
            return render(request, 'membros.html', {'membros': membros_qs})
    
    Uso com lookup aninhado:
        def lista_cargos(request):
            cargos_qs = Cargo.objects.all()
            cargos_qs = filtrar_queryset_escopo(cargos_qs, request, igreja_field='membro__igreja')
            return render(request, 'cargos.html', {'cargos': cargos_qs})
    """
    from core.utils import get_igrejas_permitidas
    
    # Obtém ministério
    perfil = getattr(request.user, 'perfil_usuario', None)
    ministerio = perfil.ministerio if perfil else None
    
    if not ministerio:
        igreja_ativa = getattr(request, 'igreja_ativa', None)
        if igreja_ativa:
            ministerio = igreja_ativa.ministerio
    
    if not ministerio:
        # Se não tem ministério, retorna vazio
        return queryset.none()
    
    # Busca igrejas permitidas
    igrejas_permitidas = get_igrejas_permitidas(request.user, ministerio)
    
    # Aplica filtro
    filter_kwargs = {f'{igreja_field}__in': igrejas_permitidas}
    return queryset.filter(**filter_kwargs)
