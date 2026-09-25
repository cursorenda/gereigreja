from datetime import date
import unicodedata
from urllib.parse import urlencode

from django.db.models import Q
from django.utils import timezone

from secretaria.models import Membro, StatusPessoa

from .models import AutomacaoAniversariantes, Aviso, WhatsAppConfiguracao, WhatsAppMensagemLog


def _normalizar_texto(valor):
    texto = (valor or '').strip().lower()
    texto = unicodedata.normalize('NFKD', texto)
    return ''.join(ch for ch in texto if not unicodedata.combining(ch))


def _q_status_permitidos_whatsapp():
    return Q(nome__iexact='Ativo') | Q(nome__iexact='Inativo')


def tipos_exigem_status_restrito_whatsapp(tipos_pessoa):
    """Retorna True quando houver tipo nao-membro, restringindo status para envio."""
    nomes_tipos = [_normalizar_texto(getattr(tipo, 'nome', '')) for tipo in tipos_pessoa]
    if not nomes_tipos:
        return False
    return any('membro' not in nome for nome in nomes_tipos)


def status_queryset_whatsapp_por_tipos(tipos_pessoa):
    """Retorna queryset de status permitido para os tipos selecionados no WhatsApp em massa."""
    qs = StatusPessoa.objects.all().order_by('nome')
    if tipos_exigem_status_restrito_whatsapp(tipos_pessoa):
        qs = qs.filter(_q_status_permitidos_whatsapp())
    return qs


def filtrar_status_whatsapp_para_tipos(status_qs, tipos_pessoa):
    """Aplica a regra de status permitido ao queryset de status ja selecionado."""
    if status_qs is None:
        return status_qs
    if tipos_exigem_status_restrito_whatsapp(tipos_pessoa):
        return status_qs.filter(_q_status_permitidos_whatsapp())
    return status_qs


def parse_whatsapp_filtros(query_data):
    tipos_pessoa_ids = [int(v) for v in query_data.getlist('tipos_pessoa') if str(v).isdigit()]
    status_pessoa_ids = [int(v) for v in query_data.getlist('status_pessoa') if str(v).isdigit()]
    graus_eclesiasticos = [v for v in query_data.getlist('graus_eclesiasticos') if v]

    return {
        'tipos_pessoa_ids': tipos_pessoa_ids,
        'status_pessoa_ids': status_pessoa_ids,
        'graus_eclesiasticos': graus_eclesiasticos,
        'aniversariantes_do_mes': query_data.get('aniversariantes_do_mes') in ('on', 'true', '1'),
        'somente_com_celular': query_data.get('somente_com_celular') in ('on', 'true', '1'),
    }


def build_whatsapp_filtros_querystring(filtros):
    params = []
    for tipo_id in filtros.get('tipos_pessoa_ids', []):
        params.append(('tipos_pessoa', str(tipo_id)))
    for status_id in filtros.get('status_pessoa_ids', []):
        params.append(('status_pessoa', str(status_id)))
    for grau in filtros.get('graus_eclesiasticos', []):
        params.append(('graus_eclesiasticos', str(grau)))
    if filtros.get('aniversariantes_do_mes'):
        params.append(('aniversariantes_do_mes', 'on'))
    if filtros.get('somente_com_celular'):
        params.append(('somente_com_celular', 'on'))
    return urlencode(params, doseq=True)


def filtrar_membros_whatsapp_destino(
    *,
    ministerio,
    igreja_ativa,
    tipos_pessoa,
    graus_eclesiasticos,
    status_pessoa,
    aniversariantes_do_mes,
    somente_com_celular,
):
    """Filtra membros por critérios de envio WhatsApp."""
    membros_qs = Membro.objects.filter(igreja__ministerio=ministerio)

    if igreja_ativa:
        membros_qs = membros_qs.filter(igreja=igreja_ativa)

    if tipos_pessoa:
        membros_qs = membros_qs.filter(tipo_pessoa__in=tipos_pessoa)
    if graus_eclesiasticos:
        membros_qs = membros_qs.filter(grau_eclesiastico__in=graus_eclesiasticos)
    if status_pessoa:
        membros_qs = membros_qs.filter(status_pessoa__in=status_pessoa)
    if aniversariantes_do_mes:
        hoje = date.today()
        membros_qs = membros_qs.filter(nascimento__month=hoje.month)
    if somente_com_celular:
        membros_qs = membros_qs.exclude(celular__isnull=True).exclude(celular='')

    return membros_qs.select_related('igreja').distinct()


def build_whatsapp_preview_data(*, ministerio, membros_qs, limite_nomes=200):
    """Monta payload de prévia de destinatários com totais e motivos de bloqueio."""
    config_igrejas_ids = set(
        WhatsAppConfiguracao.objects.filter(ministerio=ministerio, ativo=True)
        .exclude(igreja__isnull=True)
        .values_list('igreja_id', flat=True)
    )

    sem_celular_q = Q(celular__isnull=True) | Q(celular='')
    total_filtrados = membros_qs.count()
    sem_config_total = membros_qs.exclude(igreja_id__in=config_igrejas_ids).count()
    sem_celular_total = membros_qs.filter(sem_celular_q).count()

    aptos_qs = membros_qs.filter(igreja_id__in=config_igrejas_ids).exclude(sem_celular_q)
    total_aptos = aptos_qs.count()

    pessoas = []
    membros_preview = membros_qs.order_by('pk')[:limite_nomes]
    for membro in membros_preview:
        tem_celular = bool((membro.celular or '').strip())
        tem_config = membro.igreja_id in config_igrejas_ids
        habilitado = tem_celular and tem_config

        motivo_bloqueio = ''
        if not tem_celular:
            motivo_bloqueio = 'Sem celular cadastrado'
        elif not tem_config:
            motivo_bloqueio = 'Igreja sem configuracao WhatsApp ativa'

        pessoas.append(
            {
                'id': membro.pk,
                'nome': membro.nome or 'Sem nome',
                'igreja': membro.igreja.nome_igreja if membro.igreja else 'Sem igreja',
                'celular': membro.celular or '-',
                'tem_celular': tem_celular,
                'habilitado': habilitado,
                'motivo_bloqueio': motivo_bloqueio,
            }
        )

    return {
        'total_filtrados': total_filtrados,
        'total_aptos': total_aptos,
        'sem_config_total': sem_config_total,
        'sem_celular_total': sem_celular_total,
        'pessoas': pessoas,
        'limite_nomes': limite_nomes,
    }


def filtrar_membros_email_destino(
    *,
    ministerio,
    igrejas_destino,
    tipos_pessoa,
    graus_eclesiasticos,
    status_pessoa,
    aniversariantes_do_mes,
):
    """Filtra membros por critérios para envio de e-mail em massa."""
    membros_qs = Membro.objects.filter(igreja__ministerio=ministerio)

    if igrejas_destino:
        igreja_ids = []
        for item in igrejas_destino:
            if hasattr(item, 'pk'):
                if item.pk:
                    igreja_ids.append(int(item.pk))
                continue
            if str(item).isdigit():
                igreja_ids.append(int(item))

        if igreja_ids:
            membros_qs = membros_qs.filter(igreja_id__in=igreja_ids)
    if tipos_pessoa:
        membros_qs = membros_qs.filter(tipo_pessoa__in=tipos_pessoa)
    if graus_eclesiasticos:
        membros_qs = membros_qs.filter(grau_eclesiastico__in=graus_eclesiasticos)
    if status_pessoa:
        membros_qs = membros_qs.filter(status_pessoa__in=status_pessoa)
    if aniversariantes_do_mes:
        hoje = date.today()
        membros_qs = membros_qs.filter(nascimento__month=hoje.month)

    return membros_qs


def listar_destinatarios_email(membros_qs):
    """Retorna lista distinta de e-mails válidos do queryset de membros."""
    return list(
        membros_qs.filter(email__isnull=False)
        .exclude(email='')
        .values_list('email', flat=True)
        .distinct()
    )


def build_email_preview_data(*, membros_qs, limite_nomes=200):
    """Monta payload de prévia de destinatários de e-mail com totais e aptidão."""
    total_filtrados = membros_qs.count()
    membros_com_email_qs = membros_qs.filter(email__isnull=False).exclude(email='')
    total_com_email = membros_com_email_qs.count()
    sem_email_total = max(total_filtrados - total_com_email, 0)

    pessoas = []
    membros_preview = membros_qs.select_related('igreja').order_by('pk')[:limite_nomes]
    for membro in membros_preview:
        tem_email = bool((membro.email or '').strip())
        pessoas.append(
            {
                'id': membro.pk,
                'nome': membro.nome or 'Sem nome',
                'igreja': membro.igreja.nome_igreja if membro.igreja else 'Sem igreja',
                'email': membro.email or '-',
                'habilitado': tem_email,
            }
        )

    return {
        'total_filtrados': total_filtrados,
        'total_aptos': total_com_email,
        'sem_email_total': sem_email_total,
        'pessoas': pessoas,
        'limite_nomes': limite_nomes,
    }


def obter_automacao_aniversariantes(*, ministerio):
    automacao, _ = AutomacaoAniversariantes.objects.get_or_create(ministerio=ministerio)
    return automacao


def listar_agendamentos_aniversariantes(*, ministerio):
    automacao = obter_automacao_aniversariantes(ministerio=ministerio)
    agora = timezone.localtime()

    def proxima_execucao(horario):
        referencia = agora.replace(hour=horario.hour, minute=horario.minute, second=0, microsecond=0)
        if referencia < agora:
            referencia += timezone.timedelta(days=1)
        return referencia

    agendamentos = []

    if automacao.whatsapp_ativo:
        configs_ativas = WhatsAppConfiguracao.objects.filter(
            ministerio=ministerio,
            ativo=True,
            auto_aniversariantes=True,
        ).count()
        agendamentos.append(
            {
                'canal': 'WhatsApp',
                'ativo': True,
                'horario': automacao.whatsapp_horario_envio.strftime('%H:%M'),
                'proxima_execucao': proxima_execucao(automacao.whatsapp_horario_envio),
                'ultima_execucao': automacao.ultima_execucao_whatsapp,
                'resumo': f'{configs_ativas} congregacao(oes) com envio automatico habilitado.',
            }
        )

    if automacao.email_ativo:
        agendamentos.append(
            {
                'canal': 'E-mail',
                'ativo': True,
                'horario': automacao.email_horario_envio.strftime('%H:%M'),
                'proxima_execucao': proxima_execucao(automacao.email_horario_envio),
                'ultima_execucao': automacao.ultima_execucao_email,
                'resumo': 'Disparo individual para aniversariantes com e-mail valido.',
            }
        )

    configs_dizimos = WhatsAppConfiguracao.objects.filter(
        ministerio=ministerio,
        ativo=True,
        auto_contribuicoes=True,
    ).count()
    if configs_dizimos:
        agendamentos.append(
            {
                'canal': 'Dízimos',
                'ativo': True,
                'horario': 'Fechamento do caixa',
                'proxima_execucao': None,
                'ultima_execucao': None,
                'resumo': f'{configs_dizimos} congregacao(oes) com agradecimento agendado ao fechar o caixa.',
            }
        )

    return agendamentos


def listar_proximos_aniversariantes(*, ministerio, igreja=None, dias=7, limite=8):
    base_qs = Membro.objects.filter(igreja__ministerio=ministerio).exclude(nascimento__isnull=True).select_related('igreja')
    if igreja:
        base_qs = base_qs.filter(igreja=igreja)

    hoje = timezone.localdate()
    proximos = []

    for membro in base_qs:
        nascimento = membro.nascimento
        if not nascimento:
            continue

        proxima_data = date(hoje.year, nascimento.month, nascimento.day)
        if proxima_data < hoje:
            proxima_data = date(hoje.year + 1, nascimento.month, nascimento.day)

        delta = (proxima_data - hoje).days
        if delta > dias:
            continue

        proximos.append(
            {
                'nome': membro.nome or 'Sem nome',
                'igreja': membro.igreja.nome_igreja if membro.igreja else 'Sem igreja',
                'data': proxima_data,
                'dias_restantes': delta,
            }
        )

    proximos.sort(key=lambda item: (item['data'], item['nome']))
    return proximos[:limite]


def _tendencia_whatsapp_7_dias(*, ministerio):
    """Retorna listas de labels, enviados e falhas agrupados por dia nos últimos 7 dias."""
    from django.db.models import Count
    from django.db.models.functions import TruncDate

    hoje = timezone.localdate()
    inicio = hoje - timezone.timedelta(days=6)

    # monta lookup por data
    qs = (
        WhatsAppMensagemLog.objects
        .filter(ministerio=ministerio, criado_em__date__gte=inicio)
        .exclude(status='recebido')
        .annotate(dia=TruncDate('criado_em'))
        .values('dia', 'status')
        .annotate(total=Count('id'))
        .order_by('dia')
    )

    sucesso_por_dia = {}
    falha_por_dia = {}
    for row in qs:
        d = row['dia']
        if row['status'] == 'sucesso':
            sucesso_por_dia[d] = row['total']
        else:
            falha_por_dia[d] = falha_por_dia.get(d, 0) + row['total']

    labels = []
    dados_enviados = []
    dados_falhas = []
    for i in range(7):
        d = inicio + timezone.timedelta(days=i)
        labels.append(d.strftime('%d/%m'))
        dados_enviados.append(sucesso_por_dia.get(d, 0))
        dados_falhas.append(falha_por_dia.get(d, 0))

    return {'labels': labels, 'enviados': dados_enviados, 'falhas': dados_falhas}


def obter_contexto_home_comunicacao(*, ministerio, igreja_ativa=None, dias=30, limite_logs=10, limite_avisos=5):
    """Retorna KPIs e listas da home de Comunicação."""
    logs_whatsapp_recentes = WhatsAppMensagemLog.objects.filter(
        igreja__ministerio=ministerio
    ).order_by('-criado_em')[:limite_logs]

    referencia = timezone.now() - timezone.timedelta(days=dias)
    total_logs_ultimos_dias = WhatsAppMensagemLog.objects.filter(
        igreja__ministerio=ministerio,
        criado_em__gte=referencia,
    ).count()

    logs_sucesso_ultimos_dias = WhatsAppMensagemLog.objects.filter(
        igreja__ministerio=ministerio,
        criado_em__gte=referencia,
        status='sucesso',
    ).count()

    taxa_entrega = (
        (logs_sucesso_ultimos_dias / total_logs_ultimos_dias * 100)
        if total_logs_ultimos_dias > 0
        else 0
    )

    avisos_recentes = Aviso.objects.filter(
        ministerio=ministerio,
        publicado=True,
    ).order_by('-data_publicacao')[:limite_avisos]

    configuracoes_whatsapp = WhatsAppConfiguracao.objects.filter(
        igreja__ministerio=ministerio
    ).count()

    logs_aniversario_ultimos_dias = WhatsAppMensagemLog.objects.filter(
        igreja__ministerio=ministerio,
        criado_em__gte=referencia,
        tipo='aniversario',
    ).count()

    automacao_aniversarios = obter_automacao_aniversariantes(ministerio=ministerio)
    agendamentos_aniversario = listar_agendamentos_aniversariantes(ministerio=ministerio)
    proximos_aniversariantes = listar_proximos_aniversariantes(
        ministerio=ministerio,
        igreja=igreja_ativa,
        dias=7,
        limite=6,
    )
    total_automacoes_ativas = sum(
        int(bool(flag))
        for flag in (
            automacao_aniversarios.whatsapp_ativo,
            automacao_aniversarios.email_ativo,
            WhatsAppConfiguracao.objects.filter(
                igreja__ministerio=ministerio,
                ativo=True,
                auto_contribuicoes=True,
            ).exists(),
            automacao_aniversarios.followup_visitantes_ativo,
            automacao_aniversarios.lembrete_eventos_ativo,
        )
    )
    tendencia_7_dias = _tendencia_whatsapp_7_dias(ministerio=ministerio)

    return {
        'total_logs_ultimos_30_dias': total_logs_ultimos_dias,
        'logs_sucesso_ultimos_30_dias': logs_sucesso_ultimos_dias,
        'logs_aniversario_ultimos_30_dias': logs_aniversario_ultimos_dias,
        'taxa_entrega': round(taxa_entrega, 1),
        'logs_whatsapp_recentes': logs_whatsapp_recentes,
        'avisos_recentes': avisos_recentes,
        'configuracoes_whatsapp': configuracoes_whatsapp,
        'automacao_aniversarios': automacao_aniversarios,
        'agendamentos_aniversario': agendamentos_aniversario,
        'proximos_aniversariantes': proximos_aniversariantes,
        'total_automacoes_ativas': total_automacoes_ativas,
        'tendencia_labels': tendencia_7_dias['labels'],
        'tendencia_enviados': tendencia_7_dias['enviados'],
        'tendencia_falhas': tendencia_7_dias['falhas'],
    }


def _base_logs_whatsapp_qs(*, ministerio, status=None, tipo=None, busca=None):
    qs = WhatsAppMensagemLog.objects.filter(ministerio=ministerio).select_related('igreja', 'membro')

    if status:
        qs = qs.filter(status=status)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if busca:
        busca = busca.strip()
        if busca:
            qs = qs.filter(
                Q(telefone_destino__icontains=busca)
                | Q(mensagem__icontains=busca)
                | Q(igreja__nome_igreja__icontains=busca)
                | Q(erro__icontains=busca)
            )

    return qs.order_by('-criado_em')


def listar_logs_whatsapp(*, ministerio, limite=200, status=None, tipo=None, busca=None):
    """Lista logs de WhatsApp do ministério para a tela operacional."""
    qs = _base_logs_whatsapp_qs(
        ministerio=ministerio,
        status=status,
        tipo=tipo,
        busca=busca,
    )
    return qs[:limite]


def resumir_logs_whatsapp(*, ministerio, status=None, tipo=None, busca=None):
    """Retorna indicadores rápidos para a tela de logs de WhatsApp.

    Nota: neutralizado_demo e contado separadamente e NAO como entrega real.
    Ele representa fluxo funcional concluido no Demo, nao entrega externa.
    """
    qs = _base_logs_whatsapp_qs(
        ministerio=ministerio,
        status=status,
        tipo=tipo,
        busca=busca,
    )
    total = qs.count()
    sucesso = qs.filter(status='sucesso').count()
    erro = qs.filter(status='erro').count()
    recebido = qs.filter(status='recebido').count()
    neutralizado_demo = qs.filter(status='neutralizado_demo').count()
    return {
        'total': total,
        'sucesso': sucesso,
        'erro': erro,
        'recebido': recebido,
        'neutralizado_demo': neutralizado_demo,
    }
