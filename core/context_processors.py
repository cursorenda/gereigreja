def modo_auditoria_flag(request):
    """
    Adiciona o flag de modo auditoria ao contexto global.
    """
    return {'modo_auditoria_ativo': bool(request.session.get('modo_auditoria', False))}
from django.apps import apps

def ultimos_cadastros(request):
    """
    Adiciona os últimos 5 ministérios, igrejas e membros ao contexto global.
    """
    try:
        Ministerio = apps.get_model('configuracao', 'Ministerio')
        Igreja = apps.get_model('configuracao', 'Igreja')
        Membro = apps.get_model('secretaria', 'Membro')
    except LookupError:
        return {}


    ultimos_ministerios = Ministerio.objects.order_by('-id')[:5]
    ultimas_igrejas = Igreja.objects.order_by('-id')[:5]
    # Membro não tem id, usa chave como PK
    ultimos_membros = Membro.objects.order_by('-chave')[:5]

    return {
        'ultimos_ministerios': ultimos_ministerios,
        'ultimas_igrejas': ultimas_igrejas,
        'ultimos_membros': ultimos_membros,
    }
from django.contrib import messages
def deduplicate_assinatura_vencida(request):
    from django.utils.safestring import mark_safe
    msgs = []
    assinatura_vencida_seen = False
    # Percorre todas as mensagens do request
    for m in messages.get_messages(request):
        msg_str = str(m).lower()
        # Identifica mensagens de assinatura vencida
        if 'assinatura' in msg_str and 'vencida' in msg_str:
            if not assinatura_vencida_seen:
                # Garante que apenas uma mensagem de assinatura vencida será exibida
                # Se for objeto Message, marca o atributo message como seguro para HTML
                from django.contrib.messages.storage.base import Message
                if isinstance(m, Message):
                    m.message = mark_safe(m.message)  # Necessário para permitir HTML seguro (ex: destaque do plano)
                    msgs.append(m)
                else:
                    # Se não for objeto Message, converte para string segura
                    msgs.append(mark_safe(str(m)))
                assinatura_vencida_seen = True
            # Ignora duplicatas de assinatura vencida
        else:
            # Adiciona outras mensagens normalmente
            msgs.append(m)
    # Retorna o contexto com as mensagens tratadas
    return {'messages': msgs}

def sistema_nome(request):
    # Adiciona o nome do sistema ao contexto de todos os templates
    return {'SISTEMA_NOME': 'Gereigreja'}

def ministerio_context(request):
    """
    Adiciona o ministério do usuário ao contexto de todos os templates.
    Isso garante que a variável 'ministerio' esteja sempre disponível,
    especialmente para exibir o logo no menu lateral (base_com_menu.html).
    """
    if request.user.is_authenticated:
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.ministerio:
            return {'ministerio': request.user.perfil.ministerio}
    return {'ministerio': None}

from comunicacao.models import Notificacao

def unread_notifications(request):
    """
    Adiciona a contagem de notificações não lidas ao contexto de cada template.
    """
    if request.user.is_authenticated:
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.ministerio:
            unread_count = Notificacao.objects.filter(
                user=request.user,
                ministerio=request.user.perfil.ministerio,
                is_read=False
            ).count()
            return {'unread_notifications_count': unread_count}
    # Retorna 0 se não autenticado ou sem ministério
    return {'unread_notifications_count': 0}
