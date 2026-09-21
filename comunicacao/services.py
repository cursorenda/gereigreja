from datetime import timedelta
from decimal import Decimal
import logging

from django.db import transaction

from configuracao.models import Igreja
from eventos.models import Evento
from financeiro.models import Receitas
from secretaria.models import Membro, Pessoa

from .models import AutomacaoAniversariantes, WhatsAppConfiguracao, WhatsAppMensagemAgendada, WhatsAppMensagemLog
from .services_whatsapp import WhatsAppSendError, send_whatsapp_text
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone


logger = logging.getLogger(__name__)


WHATSAPP_TEMPLATE_NOVO_MEMBRO = (
    'Ola {primeiro_nome}, seja muito bem-vindo(a) a {igreja}! '
    'E uma alegria receber voce em nossa familia de fe. '
    'Conte com o carinho pastoral do {ministerio}.'
)

WHATSAPP_TEMPLATE_VISITANTE = (
    'Ola {primeiro_nome}, foi uma alegria receber voce na {igreja}! '
    'Esperamos voce novamente no proximo encontro. '
    'Com carinho, equipe pastoral do {ministerio}.'
)

WHATSAPP_TEMPLATE_EVENTO = (
    '{quando} teremos "{evento}" as {hora} na {igreja}. '
    'Esperamos voce!'
)

WHATSAPP_TEMPLATE_AGRADECIMENTO_DIZIMO = (
    'Obrigado, {primeiro_nome}, por sua fidelidade no dizimo de {valor}. '
    'Deus abencoe sua vida.'
)


def _obter_automacao_comunicacao(ministerio):
    automacao, _ = AutomacaoAniversariantes.objects.get_or_create(ministerio=ministerio)
    return automacao


def _configuracao_whatsapp_pertence_ao_ministerio(configuracao, ministerio):
    """Retorna False para configurações históricas que cruzam tenants."""
    igreja = getattr(configuracao, 'igreja', None)
    if igreja is None:
        logger.warning('Configuracao WhatsApp sem igreja ignorada: config=%s', getattr(configuracao, 'pk', None))
        return False

    igreja_ministerio_id = getattr(igreja, 'ministerio_id', None)
    config_ministerio_id = getattr(configuracao, 'ministerio_id', None)
    ministerio_id = getattr(ministerio, 'id', None)
    if igreja_ministerio_id is not None and config_ministerio_id is not None and igreja_ministerio_id != config_ministerio_id:
        logger.warning('Configuracao WhatsApp cross-tenant ignorada: config=%s', getattr(configuracao, 'pk', None))
        return False
    if igreja_ministerio_id is not None and ministerio_id is not None and igreja_ministerio_id != ministerio_id:
        logger.warning('Configuracao WhatsApp fora do ministerio solicitado ignorada: config=%s', getattr(configuracao, 'pk', None))
        return False
    return True


def _formatar_valor_brasileiro(valor):
    valor_decimal = Decimal(valor or 0).quantize(Decimal('0.01'))
    texto = f'{valor_decimal:,.2f}'
    return 'R$ ' + texto.replace(',', 'X').replace('.', ',').replace('X', '.')


def personalizar_template_comunicacao(template, membro, ministerio, substituicoes=None):
    primeiro_nome = (membro.nome or '').strip().split()[0] if (membro.nome or '').strip() else ''
    data_aniversario = membro.nascimento.strftime('%d/%m') if getattr(membro, 'nascimento', None) else ''
    texto = (
        template.replace('{nome}', membro.nome or '')
        .replace('{primeiro_nome}', primeiro_nome)
        .replace('{igreja}', membro.igreja.nome_igreja if membro.igreja else '')
        .replace('{ministerio}', ministerio.nome_fantasia)
        .replace('{data_aniversario}', data_aniversario)
    )
    if substituicoes:
        for chave, valor in substituicoes.items():
            texto = texto.replace(f'{{{chave}}}', '' if valor is None else str(valor))
    return texto


def agendar_agradecimentos_dizimo_fechamento(*, fechamento, force=False):
    if fechamento is None or not fechamento.igreja_id:
        return {'agendados': 0, 'ignorados': 0, 'inativo': True}

    config = WhatsAppConfiguracao.objects.filter(
        ministerio=fechamento.igreja.ministerio,
        igreja=fechamento.igreja,
        ativo=True,
        auto_contribuicoes=True,
    ).first()
    if not config:
        return {'agendados': 0, 'ignorados': 0, 'inativo': True}
    if not _configuracao_whatsapp_pertence_ao_ministerio(config, fechamento.igreja.ministerio):
        return {'agendados': 0, 'ignorados': 0, 'inativo': True}

    recebimentos = (
        Receitas.objects.filter(
            igreja=fechamento.igreja,
            data__range=(fechamento.data_inicio, fechamento.data_fim),
            categoria='dizimo',
            membro__isnull=False,
        )
        .exclude(membro__celular__isnull=True)
        .exclude(membro__celular='')
        .select_related('membro', 'igreja')
    )

    totais_por_membro = {}
    for receita in recebimentos:
        membro = receita.membro
        if not membro or not membro.celular:
            continue
        acumulado = totais_por_membro.setdefault(
            membro.pk,
            {
                'membro': membro,
                'valor': Decimal('0.00'),
            },
        )
        acumulado['valor'] += receita.valor or Decimal('0.00')

    agendados = 0
    ignorados = 0

    for membro_id, dados in totais_por_membro.items():
        membro = dados['membro']
        valor_total = dados['valor']
        chave_agendamento = f'fechamento:{fechamento.pk}:membro:{membro_id}:dizimo'
        mensagem = personalizar_template_comunicacao(
            config.auto_contribuicoes_template or WHATSAPP_TEMPLATE_AGRADECIMENTO_DIZIMO,
            membro,
            fechamento.igreja.ministerio,
            substituicoes={'valor': _formatar_valor_brasileiro(valor_total)},
        )

        defaults = {
            'ministerio': fechamento.igreja.ministerio,
            'igreja': fechamento.igreja,
            'membro': membro,
            'configuracao': config,
            'fechamento_caixa': fechamento,
            'tipo': 'dizimo',
            'status': 'pendente',
            'telefone_destino': membro.celular,
            'mensagem': mensagem,
            'valor': valor_total,
            'data_agendada': timezone.now(),
        }

        agendamento, created = WhatsAppMensagemAgendada.objects.get_or_create(
            chave_agendamento=chave_agendamento,
            defaults=defaults,
        )

        if not created and force:
            for campo, valor in defaults.items():
                setattr(agendamento, campo, valor)
            agendamento.status = 'pendente'
            agendamento.erro = None
            agendamento.data_envio = None
            agendamento.resposta_waha = None
            agendamento.save()
            agendados += 1
            continue

        if created:
            agendados += 1
        else:
            ignorados += 1

    return {'agendados': agendados, 'ignorados': ignorados, 'inativo': False}


def processar_whatsapp_agendados(*, ministerio=None, force=False):
    queryset = WhatsAppMensagemAgendada.objects.filter(status='pendente', data_agendada__lte=timezone.now())
    if ministerio is not None:
        queryset = queryset.filter(ministerio=ministerio)

    enviados = 0
    falhas = 0
    ignorados = 0

    for agendamento in queryset.select_related('ministerio', 'igreja', 'membro', 'configuracao'):
        config = agendamento.configuracao
        if not config or not config.ativo:
            agendamento.status = 'erro'
            agendamento.erro = 'Configuracao WhatsApp inativa ou ausente.'
            agendamento.save(update_fields=['status', 'erro', 'atualizado_em'])
            falhas += 1
            continue
        if not _configuracao_whatsapp_pertence_ao_ministerio(config, agendamento.ministerio):
            agendamento.status = 'erro'
            agendamento.erro = 'Configuracao WhatsApp pertence a outro ministerio.'
            agendamento.save(update_fields=['status', 'erro', 'atualizado_em'])
            falhas += 1
            continue

        if not agendamento.telefone_destino:
            agendamento.status = 'erro'
            agendamento.erro = 'Telefone destino ausente.'
            agendamento.save(update_fields=['status', 'erro', 'atualizado_em'])
            falhas += 1
            continue

        if not force and agendamento.status != 'pendente':
            ignorados += 1
            continue

        try:
            send_whatsapp_text(
                config,
                agendamento.telefone_destino,
                agendamento.mensagem,
                tipo=agendamento.tipo,
                ministerio=agendamento.ministerio,
                igreja=agendamento.igreja,
                membro=agendamento.membro,
            )
            agendamento.status = 'enviado'
            agendamento.data_envio = timezone.now()
            agendamento.erro = None
            agendamento.save(update_fields=['status', 'data_envio', 'erro', 'atualizado_em'])
            enviados += 1
        except WhatsAppSendError as exc:
            agendamento.status = 'erro'
            agendamento.erro = str(exc)
            agendamento.save(update_fields=['status', 'erro', 'atualizado_em'])
            falhas += 1

    return {'enviados': enviados, 'falhas': falhas, 'ignorados': ignorados}


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
        if _configuracao_whatsapp_pertence_ao_ministerio(cfg, ministerio)
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

        texto = personalizar_template_comunicacao(mensagem, membro, ministerio)
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


def enviar_email_personalizado(*, ministerio, membro, assunto_template, mensagem_template):
    assunto = personalizar_template_comunicacao(assunto_template, membro, ministerio)
    mensagem = personalizar_template_comunicacao(mensagem_template, membro, ministerio)
    remetente_email = settings.DEFAULT_FROM_EMAIL
    igreja_nome = membro.igreja.nome_igreja if membro.igreja else None

    if getattr(membro.igreja, 'email', None):
        remetente_email = membro.igreja.email

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
        [membro.email],
        html_message=html_message,
        fail_silently=False,
    )


def executar_automacao_aniversario_whatsapp(*, ministerio, referencia=None, force=False):
    automacao = AutomacaoAniversariantes.objects.get(ministerio=ministerio)
    hoje = referencia or timezone.localdate()

    if automacao.ultima_execucao_whatsapp == hoje and not force:
        return {'enviados': 0, 'falhas': 0, 'ignorado': True}

    enviados = 0
    falhas = 0
    configs = WhatsAppConfiguracao.objects.filter(
        ministerio=ministerio,
        ativo=True,
        auto_aniversariantes=True,
    ).select_related('igreja', 'ministerio')

    for config in configs:
        if not _configuracao_whatsapp_pertence_ao_ministerio(config, ministerio):
            continue
        pessoas = Membro.objects.filter(
            igreja=config.igreja,
            nascimento__month=hoje.month,
            nascimento__day=hoje.day,
        ).exclude(celular__isnull=True).exclude(celular='').select_related('igreja')

        for pessoa in pessoas:
            texto = personalizar_template_comunicacao(automacao.whatsapp_template, pessoa, ministerio)
            try:
                send_whatsapp_text(
                    config,
                    pessoa.celular,
                    texto,
                    tipo='aniversario',
                    ministerio=ministerio,
                    igreja=config.igreja,
                    membro=pessoa,
                )
                enviados += 1
            except WhatsAppSendError:
                falhas += 1

    with transaction.atomic():
        AutomacaoAniversariantes.objects.filter(pk=automacao.pk).update(ultima_execucao_whatsapp=hoje)

    return {'enviados': enviados, 'falhas': falhas, 'ignorado': False}


def executar_automacao_aniversario_email(*, ministerio, referencia=None, force=False):
    automacao = AutomacaoAniversariantes.objects.get(ministerio=ministerio)
    hoje = referencia or timezone.localdate()

    if automacao.ultima_execucao_email == hoje and not force:
        return {'enviados': 0, 'falhas': 0, 'ignorado': True}

    enviados = 0
    falhas = 0

    # Itera por igreja para garantir isolamento de escopo (evitar escape entre igrejas do ministerio)
    igrejas = Igreja.objects.filter(ministerio=ministerio)
    for igreja in igrejas:
        pessoas = Membro.objects.filter(
            igreja=igreja,
            nascimento__month=hoje.month,
            nascimento__day=hoje.day,
        ).exclude(email__isnull=True).exclude(email='').select_related('igreja')

        for pessoa in pessoas:
            try:
                enviar_email_personalizado(
                    ministerio=ministerio,
                    membro=pessoa,
                    assunto_template=automacao.email_assunto_template,
                    mensagem_template=automacao.email_mensagem_template,
                )
                enviados += 1
            except Exception:
                falhas += 1

    with transaction.atomic():
        AutomacaoAniversariantes.objects.filter(pk=automacao.pk).update(ultima_execucao_email=hoje)

    return {'enviados': enviados, 'falhas': falhas, 'ignorado': False}


def executar_automacao_novos_membros_whatsapp(*, ministerio, referencia=None, dias=7, force=False):
    """Envia boas-vindas no WhatsApp para novos cadastros ainda sem envio de boas-vindas."""
    hoje = referencia or timezone.localdate()
    data_inicio = hoje - timedelta(days=max(int(dias), 0))

    enviados = 0
    falhas = 0
    ignorados = 0

    configs = WhatsAppConfiguracao.objects.filter(
        ministerio=ministerio,
        ativo=True,
        auto_novos_membros=True,
    ).select_related('igreja', 'ministerio')

    for config in configs:
        if not _configuracao_whatsapp_pertence_ao_ministerio(config, ministerio):
            continue
        pessoas = (
            Membro.objects.filter(
                igreja=config.igreja,
                criado_em__date__gte=data_inicio,
            )
            .exclude(celular__isnull=True)
            .exclude(celular='')
            .select_related('igreja')
        )

        for pessoa in pessoas:
            ja_enviado = WhatsAppMensagemLog.objects.filter(
                ministerio=ministerio,
                igreja=config.igreja,
                membro=pessoa,
                tipo='novo_membro',
                status='sucesso',
            ).exists()
            if ja_enviado and not force:
                ignorados += 1
                continue

            texto = personalizar_template_comunicacao(WHATSAPP_TEMPLATE_NOVO_MEMBRO, pessoa, ministerio)
            try:
                send_whatsapp_text(
                    config,
                    pessoa.celular,
                    texto,
                    tipo='novo_membro',
                    ministerio=ministerio,
                    igreja=config.igreja,
                    membro=pessoa,
                )
                enviados += 1
            except WhatsAppSendError:
                falhas += 1

    return {'enviados': enviados, 'falhas': falhas, 'ignorados': ignorados}


def executar_automacao_followup_visitantes_whatsapp(*, ministerio, referencia=None, dias_apos=1, force=False):
    """Envia follow-up para visitantes em D+N da primeira visita."""
    automacao = _obter_automacao_comunicacao(ministerio)
    if not automacao.followup_visitantes_ativo:
        return {'enviados': 0, 'falhas': 0, 'ignorados': 0, 'inativo': True}

    hoje = referencia or timezone.localdate()
    dias_followup = automacao.followup_visitantes_dias_apos
    if dias_apos is not None:
        dias_followup = dias_apos
    data_alvo = hoje - timedelta(days=max(int(dias_followup), 0))

    enviados = 0
    falhas = 0
    ignorados = 0

    configs = WhatsAppConfiguracao.objects.filter(
        ministerio=ministerio,
        ativo=True,
        auto_novos_membros=True,
    ).select_related('igreja', 'ministerio')

    for config in configs:
        if not _configuracao_whatsapp_pertence_ao_ministerio(config, ministerio):
            continue
        pessoas = (
            Pessoa.objects.filter(
                igreja=config.igreja,
                data_primeira_visita=data_alvo,
            )
            .exclude(celular__isnull=True)
            .exclude(celular='')
            .select_related('igreja')
        )

        for pessoa in pessoas:
            template = automacao.followup_visitantes_template or WHATSAPP_TEMPLATE_VISITANTE
            texto = personalizar_template_comunicacao(template, pessoa, ministerio)
            ja_enviado = WhatsAppMensagemLog.objects.filter(
                ministerio=ministerio,
                igreja=config.igreja,
                membro=pessoa,
                tipo='outro',
                status='sucesso',
                mensagem=texto,
                criado_em__date=hoje,
            ).exists()
            if ja_enviado and not force:
                ignorados += 1
                continue

            try:
                send_whatsapp_text(
                    config,
                    pessoa.celular,
                    texto,
                    tipo='outro',
                    ministerio=ministerio,
                    igreja=config.igreja,
                    membro=pessoa,
                )
                enviados += 1
            except WhatsAppSendError:
                falhas += 1

    return {'enviados': enviados, 'falhas': falhas, 'ignorados': ignorados}


def executar_automacao_lembrete_eventos_whatsapp(*, ministerio, referencia=None, force=False):
    """Envia lembretes de eventos para D-1 e D-0, evitando duplicidade no mesmo dia."""
    automacao = _obter_automacao_comunicacao(ministerio)
    if not automacao.lembrete_eventos_ativo:
        return {'enviados': 0, 'falhas': 0, 'ignorados': 0, 'eventos_processados': 0, 'inativo': True}

    agora = referencia or timezone.localtime()
    hoje = agora.date()
    amanha = hoje + timedelta(days=1)

    enviados = 0
    falhas = 0
    ignorados = 0
    eventos_processados = 0

    configs = WhatsAppConfiguracao.objects.filter(
        ministerio=ministerio,
        ativo=True,
        auto_lembrete_eventos=True,
    ).select_related('igreja', 'ministerio')

    for config in configs:
        if not _configuracao_whatsapp_pertence_ao_ministerio(config, ministerio):
            continue
        eventos = Evento.objects.filter(
            igreja=config.igreja,
            data_inicio__date__in=[hoje, amanha],
        ).order_by('data_inicio')
        if not eventos.exists():
            continue

        pessoas = (
            Pessoa.objects.filter(igreja=config.igreja)
            .exclude(celular__isnull=True)
            .exclude(celular='')
        )

        for evento in eventos:
            data_evento = timezone.localtime(evento.data_inicio)
            if data_evento.date() == hoje and data_evento <= agora:
                continue

            dias_para_evento = (data_evento.date() - hoje).days
            if dias_para_evento not in (0, 1):
                continue

            eventos_processados += 1
            prefixo = 'Amanha' if dias_para_evento == 1 else 'Hoje'
            template = automacao.lembrete_eventos_template or WHATSAPP_TEMPLATE_EVENTO
            texto = (
                template
                .replace('{quando}', prefixo)
                .replace('{evento}', evento.titulo or 'Evento')
                .replace('{hora}', data_evento.strftime('%H:%M'))
                .replace('{igreja}', config.igreja.nome_igreja if config.igreja else '')
                .replace('{ministerio}', ministerio.nome_fantasia)
            )

            for pessoa in pessoas:
                ja_enviado = WhatsAppMensagemLog.objects.filter(
                    ministerio=ministerio,
                    igreja=config.igreja,
                    membro=pessoa,
                    tipo='evento',
                    status='sucesso',
                    mensagem=texto,
                    criado_em__date=hoje,
                ).exists()
                if ja_enviado and not force:
                    ignorados += 1
                    continue

                try:
                    send_whatsapp_text(
                        config,
                        pessoa.celular,
                        texto,
                        tipo='evento',
                        ministerio=ministerio,
                        igreja=config.igreja,
                        membro=pessoa,
                    )
                    enviados += 1
                except WhatsAppSendError:
                    falhas += 1

    return {
        'enviados': enviados,
        'falhas': falhas,
        'ignorados': ignorados,
        'eventos_processados': eventos_processados,
    }
