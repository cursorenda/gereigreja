# c:\Gereigreja\core\utils.py
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse

# É importante que os modelos referenciados aqui não criem dependências circulares.
# configuracao.models é um local comum para PerfilUsuario, Organizacao, AssinaturaOrganizacao.
from configuracao.models import PerfilUsuario, Organizacao, AssinaturaOrganizacao

import logging
logger = logging.getLogger(__name__)

def get_organizacao_or_error(request):
    """
    Obtém a organização do usuário logado.
    Levanta PermissionDenied se não autenticado, superuser, ou erro de perfil.
    Levanta Http404 se o perfil não tem organização associada.
    Retorna o objeto Organizacao em caso de sucesso.
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

    organizacao = perfil.organizacao
    if not organizacao:
        # messages.error(request, "Seu usuário não está associado a nenhuma organização.")
        raise Http404("Organização não encontrada para o usuário.")
    
    if not organizacao.ativo:
        # messages.warning(request, f"A organização '{organizacao.nome_fantasia}' não está ativa. Contate o suporte do sistema.")
        raise PermissionDenied(f"Acesso negado: Organização '{organizacao.nome_fantasia}' inativa.")
    
    # --- VERIFICAÇÃO DO STATUS DA ASSINATURA ---
    # Para uma função utilitária, adicionar mensagens diretamente pode não ser ideal.
    # Considere retornar um status ou levantar exceções específicas que a view pode tratar.
    # Mantendo a lógica de mensagens por enquanto, mas com verificações para evitar loops.
    try:
        assinatura = organizacao.assinatura 
        status_validos = ['ativa', 'gratuita']
        
        if assinatura.status not in status_validos and \
           not assinatura.is_periodo_cortesia_valido() and \
           not (assinatura.status == 'vencida' and organizacao.verificar_elegibilidade_plano_gratuito()):
            if request.path != reverse('configuracao:gerenciar_assinatura'):
                mensagem_aviso = f"Sua assinatura do plano {assinatura.plano.get_nome_display() if assinatura.plano else ''} está {assinatura.get_status_display()}. Por favor, regularize sua situação ou ative sua cortesia."
                if not any(m.message == mensagem_aviso for m in messages.get_messages(request)):
                    messages.warning(request, mensagem_aviso)
    except AssinaturaOrganizacao.DoesNotExist:
        if not organizacao.verificar_elegibilidade_plano_gratuito() and request.path != reverse('configuracao:gerenciar_assinatura'):
            mensagem_aviso_sem_assinatura = "Sua organização não possui uma assinatura ativa. Por favor, escolha um plano ou ative sua cortesia."
            if not any(m.message == mensagem_aviso_sem_assinatura for m in messages.get_messages(request)):
                messages.warning(request, mensagem_aviso_sem_assinatura)
    except Exception as e_assinatura:
        logger.error(f"Erro ao verificar assinatura para organização {organizacao.id} em get_organizacao_or_error: {e_assinatura}")

    return organizacao