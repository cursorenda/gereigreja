from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.contrib import messages
from configuracao.models import PerfilUsuario
from django.urls import reverse

from configuracao.models import AssinaturaMinisterio
from comunicacao.models import Notificacao

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string # Útil para renderizar templates de email
import logging

# Importar o modelo Membro do app secretaria
from secretaria.models import Membro # Certifique-se que o caminho está correto

logger = logging.getLogger(__name__)

def enviar_email_para_membro(membro: Membro, assunto: str, corpo_html: str, corpo_texto: str = None):
    """
    Envia um email para um membro específico.

    Args:
        membro: Objeto Membro destinatário.
        assunto: Assunto do email.
        corpo_html: Corpo do email em formato HTML.
        corpo_texto: Corpo do email em formato texto puro (opcional, fallback).
    """
    if not membro.email:
        logger.warning(f"Tentativa de enviar email para membro {membro.pk} ({membro.nome}), mas o email não está cadastrado.")
        # Opcional: Adicionar uma mensagem de erro ou logar de forma mais específica
        return False # Indica que o envio não foi possível

    # Tenta usar o email da igreja do membro como remetente
    # Se a igreja não tiver email, usa o email padrão das configurações
    import re
    def extract_email(address):
        match = re.search(r'<([^>]+)>', address)
        return match.group(1) if match else address.strip()

    if membro.igreja and membro.igreja.email:
        from_email = extract_email(membro.igreja.email)
    else:
        from_email = extract_email(settings.DEFAULT_FROM_EMAIL)

        from_email = from_email  # Usa apenas o e-mail puro como remetente

    try:
        send_mail(
            assunto,
            corpo_texto or '', # Corpo em texto puro (fallback)
                from_email, # Remetente: apenas o e-mail puro
            [membro.email], # Destinatário (lista de emails)
            html_message=corpo_html, # Corpo em HTML
            fail_silently=False, # Para ver erros se o envio falhar
        )
        logger.info(f"Email '{assunto}' enviado com sucesso para {membro.email} (Membro ID: {membro.pk}).")
        return True # Indica sucesso
    except Exception as e:
        logger.error(f"Erro ao enviar email '{assunto}' para {membro.email} (Membro ID: {membro.pk}): {e}", exc_info=True)
        # Opcional: Adicionar mensagem de erro para o usuário que tentou enviar
        # messages.error(request, f"Erro ao enviar email para {membro.nome}: {e}")
        return False # Indica falha

# Exemplo de como usar em uma view (ex: em secretaria/views.py ou comunicacao/views.py)
# from comunicacao.utils import enviar_email_para_membro
# from secretaria.models import Membro # Se estiver em outro app

# def enviar_email_aniversario_view(request, membro_id):
#     membro = get_object_or_404(Membro, pk=membro_id)
#     assunto = "Feliz Aniversário!"
#     # Renderizar um template de email
#     corpo_html = render_to_string('comunicacao/emails/aniversario.html', {'membro': membro})
#     corpo_texto = "Feliz Aniversário, " + membro.nome + "!" # Versão texto simples

#     if enviar_email_para_membro(membro, assunto, corpo_html, corpo_texto):
#         messages.success(request, f"Email de aniversário enviado para {membro.nome}.")
#     else:
#         messages.error(request, f"Falha ao enviar email de aniversário para {membro.nome}. Verifique os logs.")

#     return redirect('secretaria:detalhe_membro', pk=membro_id) # Exemplo de redirecionamento

def get_ministerio_or_error(request):
    """
    Obtém a ministério do usuário logado.
    Levanta PermissionDenied se não autenticado, superuser, ou erro de perfil.
    Levanta Http404 se o perfil não tem ministério associada.
    Retorna o objeto Ministerio em caso de sucesso.
    """
    if not request.user.is_authenticated:
        raise PermissionDenied("Usuário não autenticado.")
    
    if request.user.is_superuser:
        # A mensagem pode ser adicionada pela view que chama, se necessário,
        # para manter esta função mais genérica.
        # messages.info(request, "Superusuários devem usar o painel Admin para gestão global.")
        raise PermissionDenied("Superusuário não acessa esta área diretamente.")
    
    try:
        perfil = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        # messages.error(request, "Perfil de usuário não encontrado. Contate o suporte.")
        raise PermissionDenied("Acesso negado: Perfil de usuário não encontrado.")

    ministerio = perfil.ministerio
    if not ministerio:
        # messages.error(request, "Seu usuário não está associado a nenhuma ministério.")
        raise Http404("Ministério não encontrada para o usuário.")
    
    if not ministerio.ativo:
        messages.warning(request, f"A ministério '{ministerio.nome_fantasia}' não está ativa. Contate o suporte do sistema.")
        raise PermissionDenied(f"Acesso negado: Ministério '{ministerio.nome_fantasia}' inativa.")
    
    # --- VERIFICAÇÃO DO STATUS DA ASSINATURA ---
    # Para uma função utilitária, adicionar mensagens diretamente pode não ser ideal.
    # Considere retornar um status ou levantar exceções específicas que a view pode tratar.
    # Mantendo a lógica de mensagens por enquanto, mas com verificações para evitar loops.
    try:
        assinatura = ministerio.assinatura 
        status_validos = ['ativa', 'gratuita']
        if assinatura.status not in status_validos and \
           not assinatura.is_periodo_cortesia_valido() and \
           not (assinatura.status == 'vencida' and ministerio.verificar_elegibilidade_plano_gratuito()):
            if request.path != reverse('configuracao:gerenciar_assinatura'):
                plano_nome = assinatura.plano.get_nome_display() if assinatura.plano else ''
                if plano_nome:
                    plano_html = f'<span class="plano-nome">Plano</span> <span class="plano-nome">{plano_nome}</span>'
                else:
                    plano_html = f'<span class="plano-nome">Plano</span>'
                from django.utils.safestring import mark_safe
                mensagem_aviso = mark_safe(f"Sua assinatura do {plano_html} está {assinatura.get_status_display()}. Por favor, regularize sua situação ou ative sua cortesia.")
                if not any(m.message == mensagem_aviso for m in messages.get_messages(request)):
                    messages.warning(request, mensagem_aviso)

                # --- Notificação no sininho para todos os usuários ativos do ministério ---
                from configuracao.models import PerfilUsuario
                from django.utils import timezone
                # Evita duplicar notificações não lidas do mesmo tipo para o mesmo usuário
                users_in_org = [p.user for p in PerfilUsuario.objects.filter(ministerio=ministerio, user__is_active=True)]
                for user in users_in_org:
                    existe = Notificacao.objects.filter(
                        user=user,
                        ministerio=ministerio,
                        notification_type='financeiro',
                        is_read=False,
                        message__icontains='assinatura',
                    ).exists()
                    if not existe:
                        Notificacao.objects.create(
                            user=user,
                            ministerio=ministerio,
                            message=f"Sua assinatura do {assinatura.plano.get_nome_display() if assinatura.plano else ''} está {assinatura.get_status_display()}. Regularize sua situação ou ative sua cortesia.",
                            notification_type='financeiro',
                            url=reverse('configuracao:gerenciar_assinatura'),
                        )
    except AssinaturaMinisterio.DoesNotExist:
        if not ministerio.verificar_elegibilidade_plano_gratuito() and request.path != reverse('configuracao:gerenciar_assinatura'):
            mensagem_aviso_sem_assinatura = "Sua ministério não possui uma assinatura ativa. Por favor, escolha um plano ou ative sua cortesia."
            if not any(m.message == mensagem_aviso_sem_assinatura for m in messages.get_messages(request)):
                messages.warning(request, mensagem_aviso_sem_assinatura)
    except Exception as e_assinatura:
        logger.error(f"Erro ao verificar assinatura para ministério {ministerio.id} em get_ministerio_or_error: {e_assinatura}")

    return ministerio

