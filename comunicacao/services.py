from .models import WhatsAppConfiguracao, WhatsAppMensagemLog
from .services_whatsapp import WhatsAppSendError, send_whatsapp_text
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def _personalizar_mensagem_whatsapp(mensagem, membro, ministerio):
    return (
        mensagem.replace('{nome}', membro.nome or '')
        .replace('{igreja}', membro.igreja.nome_igreja if membro.igreja else '')
        .replace('{ministerio}', ministerio.nome_fantasia)
    )


def enviar_whatsapp_massa(*, ministerio, membros_qs, mensagem):
    """Executa envio WhatsApp em massa e retorna resumo operacional."""
    enviados = 0
    falhas = 0
    sem_config = 0
    igrejas_sem_config = set()
    falhas_detalhes = []

    igreja_ids = list(membros_qs.values_list('igreja_id', flat=True).distinct())
    configs_by_igreja = {
        cfg.igreja_id: cfg
        for cfg in WhatsAppConfiguracao.objects.filter(
            ministerio=ministerio,
            ativo=True,
            igreja_id__in=igreja_ids,
        )
    }

    for membro in membros_qs.select_related('igreja'):
        config = configs_by_igreja.get(membro.igreja_id)
        if not config:
            sem_config += 1
            falhas += 1
            nome_igreja = membro.igreja.nome_igreja if membro.igreja else 'Sem igreja'
            igrejas_sem_config.add(nome_igreja)
            if len(falhas_detalhes) < 3:
                falhas_detalhes.append(f"{membro.nome or 'Sem nome'}: igreja sem configuracao WA ativa.")
            WhatsAppMensagemLog.objects.create(
                ministerio=ministerio,
                igreja=membro.igreja,
                membro=membro,
                configuracao=None,
                tipo='manual',
                status='erro',
                telefone_destino=membro.celular or '',
                mensagem=mensagem,
                erro='Igreja sem configuracao WhatsApp ativa para envio em massa.',
            )
            continue

        texto = _personalizar_mensagem_whatsapp(mensagem, membro, ministerio)
        try:
            send_whatsapp_text(
                config,
                membro.celular,
                texto,
                tipo='manual',
                ministerio=ministerio,
                igreja=membro.igreja,
                membro=membro,
            )
            enviados += 1
        except WhatsAppSendError as exc:
            falhas += 1
            if len(falhas_detalhes) < 3:
                falhas_detalhes.append(f"{membro.nome or 'Sem nome'}: {str(exc)[:140]}")

    return {
        'enviados': enviados,
        'falhas': falhas,
        'sem_config': sem_config,
        'igrejas_sem_config': igrejas_sem_config,
        'falhas_detalhes': falhas_detalhes,
    }


def enviar_email_massa(*, ministerio, assunto, mensagem, destinatarios_emails, igrejas_destino):
    """Envia e-mail em massa e retorna quantidade de destinatários."""
    igreja_nome = None
    remetente_email = settings.DEFAULT_FROM_EMAIL

    if igrejas_destino and igrejas_destino.count() == 1:
        igreja = igrejas_destino.first()
        igreja_nome = getattr(igreja, 'nome_igreja', None)
        if getattr(igreja, 'email', None):
            remetente_email = igreja.email

    html_message = render_to_string(
        'comunicacao/email/email_massa_template.html',
        {
            'assunto': assunto,
            'mensagem': mensagem,
            'ministerio_nome': ministerio.nome_fantasia,
            'igreja_nome': igreja_nome,
            'remetente_email': remetente_email,
        },
    )

    send_mail(
        assunto,
        mensagem,
        settings.DEFAULT_FROM_EMAIL,
        destinatarios_emails,
        html_message=html_message,
        fail_silently=False,
    )

    return len(destinatarios_emails)
