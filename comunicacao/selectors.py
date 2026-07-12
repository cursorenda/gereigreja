from datetime import date
from urllib.parse import urlencode

from django.db.models import Q
from django.utils import timezone

from secretaria.models import Membro

from .models import Aviso, WhatsAppConfiguracao, WhatsAppMensagemLog


def parse_whatsapp_filtros(query_data):
    tipos_pessoa_ids = [int(v) for v in query_data.getlist('tipos_pessoa') if str(v).isdigit()]
    status_pessoa_ids = [int(v) for v in query_data.getlist('status_pessoa') if str(v).isdigit()]

    return {
        'tipos_pessoa_ids': tipos_pessoa_ids,
        'status_pessoa_ids': status_pessoa_ids,
        'aniversariantes_do_mes': query_data.get('aniversariantes_do_mes') in ('on', 'true', '1'),
        'somente_com_celular': query_data.get('somente_com_celular') in ('on', 'true', '1'),
    }


def build_whatsapp_filtros_querystring(filtros):
    params = []
    for tipo_id in filtros.get('tipos_pessoa_ids', []):
        params.append(('tipos_pessoa', str(tipo_id)))
    for status_id in filtros.get('status_pessoa_ids', []):
        params.append(('status_pessoa', str(status_id)))
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
    status_pessoa,
    apenas_ativos_para_relatorios,
    aniversariantes_do_mes,
):
    """Filtra membros por critérios para envio de e-mail em massa."""
    membros_qs = Membro.objects.filter(igreja__ministerio=ministerio)

    if igrejas_destino:
        membros_qs = membros_qs.filter(igreja__in=igrejas_destino)
    if tipos_pessoa:
        membros_qs = membros_qs.filter(tipo_pessoa__in=tipos_pessoa)
    if status_pessoa:
        membros_qs = membros_qs.filter(status_pessoa__in=status_pessoa)
    if apenas_ativos_para_relatorios:
        membros_qs = membros_qs.filter(status_pessoa__considerar_ativo_relatorios=True)
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


def obter_contexto_home_comunicacao(*, ministerio, dias=30, limite_logs=10, limite_avisos=5):
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

    return {
        'total_logs_ultimos_30_dias': total_logs_ultimos_dias,
        'logs_sucesso_ultimos_30_dias': logs_sucesso_ultimos_dias,
        'taxa_entrega': round(taxa_entrega, 1),
        'logs_whatsapp_recentes': logs_whatsapp_recentes,
        'avisos_recentes': avisos_recentes,
        'configuracoes_whatsapp': configuracoes_whatsapp,
    }


def listar_logs_whatsapp(*, ministerio, limite=200):
    """Lista logs de WhatsApp do ministério para a tela operacional."""
    return WhatsAppMensagemLog.objects.filter(ministerio=ministerio).select_related('igreja', 'membro')[:limite]
