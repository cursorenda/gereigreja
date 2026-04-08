"""
Signals para auditoria automática de permissões.
Registra alterações de grupos, acessos negados e sessões de usuário.
"""
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.utils import timezone

from .models import PermissionChangeLog, AccessDeniedLog, AuditSession
from configuracao.models import Ministerio


def obter_ip_do_usuario(request):
    """
    Obtém o IP real do usuário, considerando proxies.
    """
    if not request:
        return None
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ============================================================================
# SIGNALS PARA ALTERAÇÕES DE GRUPOS (PERMISSÕES)
# ============================================================================

@receiver(m2m_changed, sender=User.groups.through)
def registrar_mudanca_grupos(sender, instance, action, reverse, model, pk_set, using, **kwargs):
    """
    Signal disparado quando um usuário é adicionado/removido de um grupo.
    
    Args:
        instance: User ou Group (dependendo de 'reverse')
        action: 'pre_add', 'post_add', 'pre_remove', 'post_remove', 'pre_clear', 'post_clear'
        pk_set: Set de PKs dos objetos sendo adicionados/removidos
        reverse: True se a relação foi modificada do outro lado (Group.user_set)
    """
    # Ignorar 'pre_*' actions - apenas registrar após a ação
    if action not in ['post_add', 'post_remove']:
        return
    
    try:
        # Determinar usuário e grupo(s) afetados
        if reverse:
            # Mudança veio de Group.user_set.add/remove() - instance é Group
            grupo = instance
            usuarios_ids = pk_set
        else:
            # Mudança veio de User.groups.add/remove() - instance é User
            usuario = instance
            grupo_ids = pk_set
        
        # Processar cada combinação usuário-grupo
        if reverse:
            usuarios = User.objects.filter(pk__in=usuarios_ids)
            for usuario in usuarios:
                _registrar_mudanca_grupo(usuario, grupo, action)
        else:
            grupos = Group.objects.filter(pk__in=grupo_ids)
            for grupo in grupos:
                _registrar_mudanca_grupo(usuario, grupo, action)
    
    except Exception as e:
        print(f"Erro ao registrar mudança de grupos: {e}")


def _registrar_mudanca_grupo(usuario, grupo, action):
    """
    Helper para registrar a mudança de um grupo específico.
    """
    # Mapear ação para tipo de log
    acao_map = {
        'post_add': 'ADD',
        'post_remove': 'REMOVE',
        'post_clear': 'REMOVE',
    }
    
    acao = acao_map.get(action, 'ADD')
    
    # Tentar obter ministério do usuário
    ministerio = None
    try:
        if hasattr(usuario, 'perfil_usuario'):
            ministerio = usuario.perfil_usuario.ministerio
    except:
        pass
    
    # Criar log
    PermissionChangeLog.objects.create(
        usuario_afetado=usuario,
        grupo=grupo,
        acao=acao,
        usuario_executor=None,  # Será preenchido pelo middleware se disponível
        ministerio=ministerio,
        observacao=f"Mudança automática de grupo via signal"
    )


@receiver(post_save, sender=Group)
def registrar_criacao_grupo(sender, instance, created, using, **kwargs):
    """
    Signal disparado quando um novo Group é criado ou modificado.
    NOTA: Desativado por enquanto pois não há usuario_afetado no modelo para grupos novos.
    """
    # Comentado: requereria permitir null em usuario_afetado
    # if not created:
    #     return  # Apenas registrar criação, não modificações
    pass


# ============================================================================
# SIGNALS PARA SESSÕES DE AUDITORIA
# ============================================================================

@receiver(post_save, sender=User)
def criar_sessao_auditoria_ao_login(sender, instance, created, **kwargs):
    """
    Signal disparado quando um usuário é criado.
    Nota: Para registrar logins reais, usar middleware ou backend customizado.
    """
    # Este signal pode ser expandido para processar logins via middleware
    pass


# ============================================================================
# HELPER PARA REGISTRAR ACESSOS NEGADOS
# ============================================================================

def registrar_acesso_negado(
    usuario,
    tipo_acesso,
    recurso,
    permissao_requerida='',
    request=None,
    igreja=None,
    ministerio=None,
):
    """
    Registra uma tentativa de acesso negado.
    
    Args:
        usuario: User object
        tipo_acesso: 'VIEW', 'OBJECT', 'ACTION', ou 'API'
        recurso: Nome do recurso que foi tentado acessar
        permissao_requerida: Permissão necessária (opcional)
        request: HttpRequest object (para capturar IP, user-agent, URL)
        igreja: Igreja object (se aplicável)
        ministerio: Ministerio object (se aplicável)
    """
    try:
        ip_address = None
        user_agent = ''
        url_path = ''
        metodo_http = ''
        
        if request:
            ip_address = obter_ip_do_usuario(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
            url_path = request.path[:500]
            metodo_http = request.method
        
        # Tentar obter ministério do usuário se não foi passado
        if not ministerio:
            try:
                if hasattr(usuario, 'perfil_usuario'):
                    ministerio = usuario.perfil_usuario.ministerio
            except:
                pass
        
        AccessDeniedLog.objects.create(
            usuario=usuario,
            tipo_acesso=tipo_acesso,
            recurso=recurso,
            permissao_requerida=permissao_requerida,
            igreja_tentada=igreja,
            ip_address=ip_address,
            user_agent=user_agent,
            url_path=url_path,
            metodo_http=metodo_http,
            ministerio=ministerio,
        )
    except Exception as e:
        print(f"Erro ao registrar acesso negado: {e}")


# ============================================================================
# HELPER PARA REGISTRAR SESSÃO DE LOGIN
# ============================================================================

def registrar_login_usuario(usuario, request):
    """
    Registra o login de um usuário (criar nova AuditSession).
    Chamar do backend de autenticação customizado ou middleware.
    """
    try:
        ministerio = None
        try:
            if hasattr(usuario, 'perfil_usuario'):
                ministerio = usuario.perfil_usuario.ministerio
        except:
            pass
        
        AuditSession.objects.create(
            usuario=usuario,
            ip_address=obter_ip_do_usuario(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255] if request else '',
            ministerio=ministerio,
        )
    except Exception as e:
        print(f"Erro ao registrar login: {e}")


def registrar_logout_usuario(usuario):
    """
    Registra o logout de um usuário (marcar AuditSession como finalizada).
    Chamar do backend de logout customizado ou middleware.
    """
    try:
        sessao = AuditSession.objects.filter(
            usuario=usuario,
            logout_data_hora__isnull=True
        ).first()
        
        if sessao:
            sessao.logout_data_hora = timezone.now()
            sessao.save()
    except Exception as e:
        print(f"Erro ao registrar logout: {e}")


# ============================================================================
# HELPER PARA INCREMENTAR CONTADOR DE PÁGINAS
# ============================================================================

def incrementar_contador_paginas(usuario):
    """
    Incrementa o contador de páginas visitadas na sessão ativa.
    """
    try:
        sessao = AuditSession.objects.filter(
            usuario=usuario,
            logout_data_hora__isnull=True
        ).first()
        
        if sessao:
            sessao.paginas_visitadas += 1
            sessao.save()
    except Exception as e:
        print(f"Erro ao incrementar contador de páginas: {e}")
