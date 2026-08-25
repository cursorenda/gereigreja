# --- RELAT├ôRIO GERAL DO DIA DA EBD ---
import logging
from datetime import date, timedelta

from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.db.models import Case, Count, IntegerField, Q, Sum, Value, When
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from core.decorators import (
    page_access_required,
    secretaria_ebd_required,
    superintendente_required,
    user_passes_test_or_403,
    verificar_assinatura_valida,
)
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from core.utils import get_igrejas_permitidas, get_request_scoped_churches
from contas.constants import SECRETARIA_EBD, user_has_permission_level_or_higher
from secretaria.models import MembroCargo
from .services_chamada import (
    construir_chave_bloqueio_chamada,
    construir_chave_idempotencia_chamada,
    formulario_chamada_corresponde_a_turma,
    preparar_calendario_chamada,
    preparar_contexto_exibicao_chamada,
    preparar_formset_inicial_chamada,
    persistir_chamada,
)
from .services_copia import (
    consolidar_resultado_copia_seletiva,
    copiar_ano_anterior_completo,
    copiar_dados_selecionados_para_ano,
)
from .services_escopo import (
    aplicar_igreja_filtro_inicial,
    filtrar_alunos_por_igrejas,
    filtrar_classes_por_igrejas,
    filtrar_ofertas_por_igrejas,
    filtrar_turmas_por_igrejas,
)
from .services_consultas import (
    colapsar_alunos_por_cadastro,
    consolidar_alunos_por_cadastro_periodo,
    construir_contexto_listagem_alunos,
    construir_contexto_template_listagem_alunos,
    construir_contexto_template_listagem_turmas,
    construir_contexto_relatorio_alunos,
    construir_filtros_listagem_turmas,
    construir_historico_anual_aluno,
    construir_listagem_licoes,
    filtrar_e_paginar_aulas_geradas,
    paginar_queryset,
    preparar_alunos_para_relatorio,
)
from .services_periodos import (
    agrupar_turmas_por_calendario,
    abrir_proximo_periodo,
    criar_licoes_cronograma,
    construir_contexto_formulario_wizard_cronograma,
    construir_previa_cronograma,
    construir_status_periodo,
    gerar_cronograma_para_turma,
    gerar_e_persistir_licoes_periodos,
    normalizar_etapa_wizard_cronograma,
    normalizar_inteiro_wizard_cronograma,
    normalizar_ids_turmas_wizard,
    obter_ano_letivo_para_criacao_turma,
    obter_periodo_filtro,
    preparar_transicao_wizard_cronograma,
    preparar_contexto_periodos_listagem_turmas,
    sincronizar_periodos_e_licoes,
    tipo_periodo_ebd_valido,
    validar_ano_letivo,
    executar_fluxo_fechamento_periodo,
    preparar_contexto_fechamento_periodo,
    construir_contexto_template_fechamento_periodo,
)
from .services_permissoes import (
    filtrar_turmas_para_usuario,
    filtrar_queryset_por_turmas_do_usuario,
    get_turmas_professor,
    pode_acessar_chamada_turma,
    pode_ver_aluno,
    usuario_pode_gerenciar_ebd,
)
from .services_observabilidade import log_ebd_audit_event, log_ebd_endpoint
from .services_dashboard import (
    construir_chave_cache_dashboard,
    construir_contexto_completo_dashboard,
    publicar_resumo_semanal_dashboard,
)
from .services_configuracao import (
    aplicar_fallback_pontos_ebd,
    igreja_tem_override_ebd,
    obter_configuracao_ebd,
    obter_configuracao_ebd_turma,
    obter_configuracao_ministerio_ebd,
    obter_dia_semana_ebd,
    obter_horario_ebd_formatado,
    obter_igreja_configuracao_ebd,
    obter_info_origem_configuracao_ebd,
    obter_pontos_ebd,
    obter_tipo_periodo_ebd,
)
from .services_relatorios import (
    construir_resumo_relatorio_diario,
    ofertas_da_turma_na_data,
)
from .services_analiticos import (
    construir_alunos_evolucao,
    construir_dados_dashboard_graficos,
    construir_meses_evolucao,
    construir_ofertas_evolucao,
)
from .services_vinculos import (
    aplicar_vinculos_selecionados_em_lote,
    listar_candidatos_vinculo_secretaria,
    obter_pessoas_base_mesma_igreja,
    tentar_vinculos_listagem_alunos,
)
from .models import (
    Aluno,
    AnoLetivo,
    Avaliacao,
    CadastroAluno,
    Classe,
    Departamento,
    DEPARTAMENTOS_SUGERIDOS,
    Frequencia,
    Licao,
    OfertaClasse,
    PeriodoEBD,
    TransferenciaAluno,
    Turma,
)

logger = logging.getLogger(__name__)


# --- FUN├ç├òES HELPER DE PERMISS├òES ---
def _legado_pode_acessar_chamada_turma(user, turma):
    """
    Verifica se usu├írio pode acessar a chamada de presen├ºa da turma.
    
    Permite acesso se:
    - ├ë superuser
    - Est├í no grupo Secretaria EBD ou Superintendente EBD
    - ├ë professor da turma espec├¡fica
    """
    # Superuser sempre pode
    if user.is_superuser:
        return True
    
    # Secretaria/Superintendente EBD podem acessar todas as turmas
    if user_has_permission_level_or_higher(user, SECRETARIA_EBD):
        return True
    
    # Verifica se ├® professor da turma
    try:
        # Acessa o membro via related_name 'membro_secretaria' (Pessoa->User)
        membro = getattr(user, 'membro_secretaria', None)
        if membro:
            # Verifica se est├í nos membros da turma
            if membro in turma.membros.all():
                # Verifica se tem cargo de professor EBD ativo
                cargo_professor_ativo = MembroCargo.objects.filter(
                    membro=membro,
                    cargo__is_ebd=True,
                    cargo__nome__icontains='professor',
                    data_fim__isnull=True
                ).exists()
                if cargo_professor_ativo:
                    return True
    except Exception as exc:
        logger.warning('Falha ao validar acesso de chamada da turma para user=%s: %s', user.pk, exc)
    
    return False


def _legado_get_turmas_professor(user):
    """
    Retorna turmas onde o usu├írio ├® professor.
    """
    
    try:
        # Acessa o membro via related_name 'membro_secretaria' (Pessoa->User)
        membro = getattr(user, 'membro_secretaria', None)
        if membro:
            # Busca turmas onde o membro est├í cadastrado
            turmas_candidatas = Turma.objects.filter(membros=membro)
            
            # Filtra apenas turmas onde tem cargo de professor EBD ativo
            turmas_professor = []
            for turma in turmas_candidatas:
                cargo_professor = MembroCargo.objects.filter(
                    membro=membro,
                    cargo__is_ebd=True,
                    cargo__nome__icontains='professor',
                    data_fim__isnull=True
                ).exists()
                if cargo_professor:
                    turmas_professor.append(turma.id)
            
            return Turma.objects.filter(id__in=turmas_professor)
    except Exception as exc:
        logger.warning('Falha ao buscar turmas do professor para user=%s: %s', user.pk, exc)
    
    return Turma.objects.none()


def _legado_pode_ver_aluno(user, aluno):
    """
    Verifica se usu├írio pode ver detalhes do aluno.
    
    Permite se:
    - ├ë superuser
    - ├ë secretaria/superintendente EBD
    - ├ë professor da turma do aluno
    """
    if user.is_superuser:
        return True
    
    # Secretaria/Superintendente EBD podem ver todos
    if user_has_permission_level_or_higher(user, SECRETARIA_EBD):
        return True
    
    # Verifica se ├® professor da turma do aluno
    return pode_acessar_chamada_turma(user, aluno.turma)


def _legado_usuario_pode_gerenciar_ebd(user):
    return user.is_superuser or user_has_permission_level_or_higher(user, SECRETARIA_EBD)


def _cache_ebd_scope_churches(request, igrejas):
    request._ebd_scope_churches_cache = igrejas
    return igrejas


def get_ebd_scope_churches(request):
    from configuracao.models import Igreja

    if hasattr(request, '_ebd_scope_churches_cache'):
        return request._ebd_scope_churches_cache

    igrejas_permitidas = getattr(request, 'igrejas_permitidas', None)
    if igrejas_permitidas is None:
        perfil = getattr(request.user, 'perfil', None) or getattr(request.user, 'perfil_usuario', None)
        ministerio = getattr(perfil, 'ministerio', None)
        if ministerio:
            igrejas_permitidas = get_igrejas_permitidas(request.user, ministerio)
            if not igrejas_permitidas.exists() and usuario_pode_gerenciar_ebd(request.user):
                igrejas_permitidas = Igreja.objects.filter(ministerio=ministerio)
        else:
            igreja_ativa = getattr(request, 'igreja_ativa', None)
            if igreja_ativa:
                return _cache_ebd_scope_churches(request, Igreja.objects.filter(pk=igreja_ativa.pk))
            return _cache_ebd_scope_churches(
                request,
                Igreja.objects.all() if request.user.is_superuser else Igreja.objects.none(),
            )

    igreja_ativa = getattr(request, 'igreja_ativa', None)
    if igreja_ativa and igrejas_permitidas.filter(pk=igreja_ativa.pk).exists():
        return _cache_ebd_scope_churches(request, igrejas_permitidas.filter(pk=igreja_ativa.pk))

    igreja_ativa_id = request.session.get('igreja_ativa_id')
    if igreja_ativa_id and igrejas_permitidas.filter(pk=igreja_ativa_id).exists():
        return _cache_ebd_scope_churches(request, igrejas_permitidas.filter(pk=igreja_ativa_id))

    return _cache_ebd_scope_churches(
        request,
        get_request_scoped_churches(request, igrejas_permitidas),
    )


def get_ebd_ministerio_config(request):
    return obter_configuracao_ministerio_ebd(request)


def _igreja_tem_override_ebd(igreja):
    return igreja_tem_override_ebd(igreja)


def get_ebd_igreja_config(request):
    return obter_igreja_configuracao_ebd(request, get_ebd_scope_churches(request))


def get_ebd_config(request):
    return obter_configuracao_ebd(request, get_ebd_igreja_config(request))


def get_ebd_config_source_info(request):
    return obter_info_origem_configuracao_ebd(get_ebd_igreja_config(request))


def get_ebd_tipo_periodo(request):
    return obter_tipo_periodo_ebd(get_ebd_config(request))


def get_ebd_dia_semana(request):
    return obter_dia_semana_ebd(get_ebd_config(request))


def get_ebd_pontos_config(request):
    return obter_pontos_ebd(get_ebd_config(request))


def get_ebd_pontos_config_com_fallback(request):
    return aplicar_fallback_pontos_ebd(get_ebd_pontos_config(request))


def _get_ebd_auto_sync_session_key(request, tipo_periodo, dia_semana):
    perfil = getattr(request.user, 'perfil', None) or getattr(request.user, 'perfil_usuario', None)
    ministerio = getattr(perfil, 'ministerio', None)
    ministerio_id = getattr(ministerio, 'id', 'global')
    igreja_ativa = get_ebd_igreja_config(request)
    igreja_id = getattr(igreja_ativa, 'id', 'all')
    return f'ebd:auto-sync:{ministerio_id}:{igreja_id}:{tipo_periodo}:{dia_semana}'


def get_ebd_periodo_filtro(request):
    return obter_periodo_filtro(
        ano_letivo_filtro=request.GET.get('ano_letivo'),
        periodo_filtro=request.GET.get('periodo'),
        tipo_periodo=get_ebd_tipo_periodo(request),
        hoje=timezone.now().date(),
    )


def auto_sync_ebd_periodos_e_licoes(request, force=False):
    """
    Garante de forma automática:
    1) períodos do ano atual e próximo ano (conforme configuração ministerial);
    2) lições do período vigente (ou próximo) para turmas do escopo.
    """
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return

    try:
        hoje = timezone.now().date()
        tipo_periodo = get_ebd_tipo_periodo(request)
        dia_semana = get_ebd_dia_semana(request)
        session_key = _get_ebd_auto_sync_session_key(request, tipo_periodo, dia_semana)
        if not force and request.session.get(session_key) == hoje.isoformat():
            return
        total_criadas, periodo_nome = sincronizar_periodos_e_licoes(
            turmas=filtrar_turmas_ebd(Turma.objects.all(), request),
            hoje=hoje,
            tipo_periodo=tipo_periodo,
            dia_semana=dia_semana,
        )
        if total_criadas:
            logger.info(
                'Auto-sync EBD criou %s lições para %s (dia=%s)',
                total_criadas,
                periodo_nome,
                dia_semana,
            )

        request.session[session_key] = hoje.isoformat()
    except Exception as exc:
        logger.warning('Falha no auto-sync de periodos/licoes da EBD para user=%s: %s', request.user.pk, exc)


def filtrar_queryset_ebd(queryset, request, igreja_lookup):
    igrejas = get_ebd_scope_churches(request)
    return queryset.filter(**{f'{igreja_lookup}__in': igrejas}).distinct()


def filtrar_turmas_ebd(queryset, request):
    return filtrar_turmas_por_igrejas(queryset, get_ebd_scope_churches(request))


def filtrar_classes_ebd(queryset, request):
    return filtrar_classes_por_igrejas(queryset, get_ebd_scope_churches(request))


def filtrar_alunos_ebd(queryset, request):
    return filtrar_alunos_por_igrejas(queryset, get_ebd_scope_churches(request))


def filtrar_frequencias_ebd(queryset, request):
    return queryset.filter(aluno__in=filtrar_alunos_ebd(Aluno.objects.all(), request)).distinct()


def filtrar_avaliacoes_ebd(queryset, request):
    return queryset.filter(aluno__in=filtrar_alunos_ebd(Aluno.objects.all(), request)).distinct()


def filtrar_ofertas_ebd(queryset, request):
    """Restringe ofertas ao escopo EBD, incluindo registros legados sem turma."""
    return filtrar_ofertas_por_igrejas(queryset, get_ebd_scope_churches(request))


def get_object_or_404_ebd(queryset, request, igreja_lookup, **lookup):
    return get_object_or_404(filtrar_queryset_ebd(queryset, request, igreja_lookup), **lookup)


def oferta_queryset_por_turma_data(turma, data):
    return ofertas_da_turma_na_data(turma, data)

@page_access_required('escola_biblica')
@log_ebd_endpoint('relatorio_ebd_dia')
@verificar_assinatura_valida
def relatorio_ebd_dia(request):
    from .models import Turma, Frequencia, OfertaClasse, AnoLetivo, Licao
    from decimal import Decimal
    turmas_escopo = filtrar_turmas_ebd(Turma.objects.all(), request)
    licoes_escopo = Licao.objects.filter(turma__in=turmas_escopo).distinct()
    
    # Se data n├úo for fornecida, busca a data da li├º├úo mais recente
    data_str = request.GET.get('data')
    if data_str:
        data = parse_date(data_str)
    else:
        # Busca a data da li├º├úo mais recente
        ultima_licao = licoes_escopo.order_by('-data').first()
        data = ultima_licao.data if ultima_licao else timezone.now().date()
    
    # Filtra turmas apenas do ano letivo correspondente ├á data selecionada
    # E que tenham li├º├Áes cadastradas na data selecionada
    ano_da_data = data.year
    ano_letivo = AnoLetivo.objects.filter(ano=ano_da_data).first()
    if ano_letivo:
        turmas_com_licao = licoes_escopo.filter(data=data).values_list('turma_id', flat=True)
        turmas = turmas_escopo.filter(ano_letivo=ano_letivo, id__in=turmas_com_licao)
    else:
        turmas = Turma.objects.none()
    
    # Busca todas as datas com li├º├Áes do ano letivo para o campo de sele├º├úo
    datas_com_licoes = []
    if ano_letivo:
        datas_com_licoes = licoes_escopo.filter(turma__ano_letivo=ano_letivo).values_list('data', flat=True).distinct().order_by('-data')
    
    resumo = construir_resumo_relatorio_diario(
        turmas=turmas,
        turmas_escopo=turmas_escopo,
        licoes_escopo=licoes_escopo,
        ano_letivo=ano_letivo,
        data=data,
        datas_com_licoes=datas_com_licoes,
    )
    
    return render(request, 'escola_biblica/relatorio_ebd_dia.html', {
        **resumo,
        'data': data,
        'datas_com_licoes': datas_com_licoes,
    })
# --- CHAMADA DE PRESEN├çA POR TURMA ---

from .forms import ChamadaPresencaFormSet


@login_required
@page_access_required('escola_biblica_professor')
@log_ebd_endpoint('chamada_presenca')
@verificar_assinatura_valida
def chamada_presenca(request, turma_id):

    """
    Chamada de presen├ºa da turma.
    
    Pode ser acessada por:
    - Secretaria EBD / Superintendente EBD (todas as turmas)
    - Professor da turma (apenas sua turma)
    """
    auto_sync_ebd_periodos_e_licoes(request)
    turma = get_object_or_404(
        filtrar_turmas_ebd(
            Turma.objects.select_related('igreja', 'classe', 'classe__igreja', 'ano_letivo'),
            request,
        ),
        pk=turma_id,
    )

    if not pode_acessar_chamada_turma(request.user, turma):
        raise PermissionDenied("Você não tem permissão para acessar a chamada desta turma.")

    alunos = turma.alunos.filter(ativo=True).order_by('nome')
    tipo_periodo = get_ebd_tipo_periodo(request)
    dia_ebd = get_ebd_dia_semana(request)
    hoje = timezone.localdate()
    data_raw = request.POST.get('data') or request.GET.get('data')
    calendario_chamada = preparar_calendario_chamada(
        turma=turma,
        tipo_periodo=tipo_periodo,
        dia_ebd=dia_ebd,
        hoje=hoje,
        data_solicitada=parse_date(data_raw) if data_raw else None,
    )
    periodo = calendario_chamada['periodo']
    datas_com_licao = calendario_chamada['datas_com_licao']
    licoes_faltantes = calendario_chamada['licoes_faltantes']
    data_selecionada = calendario_chamada['data_selecionada']
    licao_do_dia = calendario_chamada['licao_do_dia']

    if licoes_faltantes and request.method != 'POST':
        msg = f"Atenção: Existem {len(licoes_faltantes)} datas do período sem lição cadastrada para esta turma. "
        url_cronograma = redirect('escola_biblica:gerar_cronograma_wizard').url
        msg += f"<a href='{url_cronograma}?turma_id={turma.id}' class='btn btn-sm btn-warning ms-2'>Criar lições em lote</a>"
        messages.warning(request, msg)

    data = data_selecionada.isoformat() if data_selecionada else ''

    ebd_pontos_config = get_ebd_pontos_config_com_fallback(request)

    classe = turma.classe if hasattr(turma, 'classe') else None
    oferta_obj = None
    if classe and data_selecionada:
        oferta_obj = oferta_queryset_por_turma_data(turma, data_selecionada).first()

    bloqueio_chamada_msg = None
    if not data_selecionada:
        bloqueio_chamada_msg = 'Não há lição cadastrada no período atual para esta turma. Cadastre as lições antes de registrar a chamada.'

    contexto_exibicao_chamada = preparar_contexto_exibicao_chamada(
        calendario=calendario_chamada,
        oferta_atual=oferta_obj,
        bloqueio_chamada_msg=bloqueio_chamada_msg,
    )

    formset = None
    if alunos.exists() and not bloqueio_chamada_msg:
        if request.method == 'POST' and not request.POST.get('troca_data'):
            if not licao_do_dia:
                messages.error(request, 'Não é possível registrar a chamada: não existe lição cadastrada para a data selecionada.')
                return redirect(request.path + (f'?data={data}' if data else ''))

            chamada_idempotency_key = construir_chave_idempotencia_chamada(request, turma.id, data_selecionada)
            if cache.get(chamada_idempotency_key):
                log_ebd_audit_event(
                    request,
                    'chamada_duplicada_ignorada',
                    turma_id=turma.id,
                    data=data_selecionada,
                )
                messages.info(request, 'Esta chamada já foi processada recentemente. Nenhuma alteração duplicada foi aplicada.')
                return redirect('escola_biblica:turma_list')

            chamada_processing_lock_key = construir_chave_bloqueio_chamada(turma.id, data_selecionada)
            if not cache.add(chamada_processing_lock_key, request.user.pk, timeout=30):
                log_ebd_audit_event(
                    request,
                    'chamada_concorrente_ignorada',
                    turma_id=turma.id,
                    data=data_selecionada,
                )
                messages.info(request, 'Outra submissão desta chamada está sendo processada no momento. Tente novamente em instantes.')
                return redirect(request.path + (f'?data={data}' if data else ''))

            formset = ChamadaPresencaFormSet(request.POST)
            try:
                if formset.is_valid():
                    if not formulario_chamada_corresponde_a_turma(formset, alunos):
                        messages.error(
                            request,
                            'A chamada foi recusada porque a lista de alunos nao corresponde a esta turma.',
                        )
                        return redirect(request.path + (f'?data={data}' if data else ''))

                    erro_validacao = False
                    pontos_totais_aula = 0
                    try:
                        pontos_totais_aula, valor_oferta_registrada = persistir_chamada(
                            formset=formset,
                            turma=turma,
                            data=data_selecionada,
                            classe=classe,
                            pontos_cfg=ebd_pontos_config,
                            valor_oferta=request.POST.get('valor_oferta'),
                        )
                        if valor_oferta_registrada is not None:
                            log_ebd_audit_event(
                                request,
                                'chamada_oferta_registrada',
                                turma_id=turma.id,
                                data=data_selecionada,
                                valor=valor_oferta_registrada,
                            )
                    except Exception as exc:
                        erro_validacao = True
                        logger.warning(
                            'ebd.chamada.atomic_error turma_id=%s data=%s user_id=%s erro=%s',
                            turma.id,
                            data_selecionada,
                            request.user.pk,
                            exc,
                        )
                        messages.error(request, f'Erro ao registrar chamada de presença: {exc}')

                    if not erro_validacao:
                        cache.set(chamada_idempotency_key, True, 60)
                        log_ebd_audit_event(
                            request,
                            'chamada_registrada',
                            turma_id=turma.id,
                            data=data_selecionada,
                            alunos_formset=len(formset.forms),
                            pontos_totais_aula=pontos_totais_aula,
                        )
                        messages.success(request, f'Chamada de presença registrada para {turma} em {data}. Pontos da aula: {pontos_totais_aula}.')
                        return redirect('escola_biblica:turma_list')
                else:
                    messages.error(request, 'Erro ao registrar chamada de presença. Verifique os dados e tente novamente.')
            finally:
                cache.delete(chamada_processing_lock_key)
        else:
            formset = preparar_formset_inicial_chamada(
                alunos=alunos,
                data=data_selecionada,
                formset_class=ChamadaPresencaFormSet,
            )

    return render(request, 'escola_biblica/chamada_presenca.html', {
        'turma': turma,
        'formset': formset,
        **contexto_exibicao_chamada,
        'ebd_pontos_config': ebd_pontos_config,
    })
# --- IMPORTS NECESS├üRIOS PARA DECORADORES ---
# --- WIZARD: Gera├º├úo de li├º├Áes em etapas ---
@page_access_required('escola_biblica')
@log_ebd_endpoint('gerar_cronograma_wizard')
@verificar_assinatura_valida
def gerar_cronograma_wizard(request):
    auto_sync_ebd_periodos_e_licoes(request)
    tipo_periodo = get_ebd_tipo_periodo(request)
    etapa = normalizar_etapa_wizard_cronograma(
        request.POST.get('etapa', request.GET.get('etapa', 1)),
    )
    hoje = timezone.now().date()
    ano_atual = hoje.year
    # Ano letivo: apenas atual e pr├│ximo (se existir)
    anos_letivos = AnoLetivo.objects.filter(ano__gte=ano_atual).order_by('ano')
    # Turmas: ├║nicas, ordem alfab├®tica
    turmas = filtrar_turmas_ebd(
        Turma.objects.filter(ano_letivo__ano__gte=ano_atual).order_by('nome').distinct(),
        request,
    )
    # Per├¡odos: s├│ do ano letivo selecionado, abertos/futuros
    periodo_ano_raw = request.POST.get('ano_letivo', ano_atual)
    periodo_ano = normalizar_inteiro_wizard_cronograma(periodo_ano_raw, ano_atual)
    periodo_selecionado = normalizar_inteiro_wizard_cronograma(
        request.POST.get('periodo', request.GET.get('periodo')),
        None,
    )
    turmas_selecionadas = normalizar_ids_turmas_wizard(
        request.POST.getlist('turmas') if request.method == 'POST' else request.GET.getlist('turmas'),
    )
    periodos = PeriodoEBD.objects.filter(
        ano_letivo__ano=periodo_ano,
        tipo=tipo_periodo,
        data_fim__gte=hoje,
    ).order_by('numero')
    context = {
        'etapa': etapa,
        'ano_letivo_selecionado': periodo_ano,
        'periodo_selecionado': periodo_selecionado,
        'turmas_selecionadas': turmas_selecionadas,
    }
    context['modo_contingencia'] = True

    # Etapa 1: Sele├º├úo
    if etapa == 1:
        context.update({
            'anos_letivos': anos_letivos,
            'periodos': periodos,
            'turmas': turmas,
        })
        if request.method == 'POST' and request.POST.get('wizard_next'):
            transicao_wizard = preparar_transicao_wizard_cronograma(
                parametros=request.POST,
                ano_atual=ano_atual,
                turmas=turmas,
                tipo_periodo=tipo_periodo,
                hoje=hoje,
            )
            dados_wizard = transicao_wizard['dados']
            ano_letivo = dados_wizard['ano_letivo']
            periodo = dados_wizard['periodo']
            turmas_ids = dados_wizard['turmas_ids']
            material = dados_wizard['material']
            status = dados_wizard['status']
            observacoes = dados_wizard['observacoes']
            nome_licao_padrao = dados_wizard['nome_licao_padrao']
            # Buscar horário padrão da configuração EBD (igreja local com fallback ministerial)
            config = get_ebd_config(request)
            horario_inicial = obter_horario_ebd_formatado(config)
            # Inicializa periodo_nome corretamente
            selecao_wizard = transicao_wizard['selecao']
            periodo_obj = selecao_wizard['periodo']
            periodo_nome = f"{periodo_obj.get_tipo_display()} {periodo_obj.numero}" if periodo_obj else "Per├¡odo"
            if not selecao_wizard['valida']:
                context['erro_wizard'] = selecao_wizard['mensagem_erro']
                return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
            periodos_prox = PeriodoEBD.objects.filter(
                ano_letivo__ano=ano_letivo,
                tipo=tipo_periodo,
                data_fim__gte=hoje,
            ).order_by('numero')
            turmas_prox = filtrar_turmas_ebd(
                Turma.objects.filter(ano_letivo__ano=ano_letivo).order_by('nome').distinct(),
                request,
            )
            context.update({
                **construir_contexto_formulario_wizard_cronograma(
                    dados=dados_wizard,
                    horario=horario_inicial,
                    etapa=2,
                ),
                'periodos': periodos_prox,
                'turmas_lista': turmas_prox,
            })
            return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
        return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)

    # Etapa 2: Configura├º├úo
    if etapa == 2:
        config = get_ebd_config(request)
        horario_inicial = obter_horario_ebd_formatado(config)
        transicao_wizard = preparar_transicao_wizard_cronograma(
            parametros=request.POST,
            ano_atual=ano_atual,
            turmas=turmas,
            tipo_periodo=tipo_periodo,
            hoje=hoje,
            horario_padrao=horario_inicial,
            usar_horario_padrao=True,
        )
        dados_wizard = transicao_wizard['dados']
        ano_letivo = dados_wizard['ano_letivo']
        periodo = dados_wizard['periodo']
        turmas_ids = dados_wizard['turmas_ids']
        material = dados_wizard['material']
        horario = dados_wizard['horario']
        status = dados_wizard['status']
        observacoes = dados_wizard['observacoes']
        nome_licao_padrao = dados_wizard['nome_licao_padrao']
        # Buscar horário padrão da configuração EBD (igreja local com fallback ministerial)
        # Padr├úo de nome sugerido
        selecao_wizard = transicao_wizard['selecao']
        periodo_obj = selecao_wizard['periodo']
        periodo_nome = f"{periodo_obj.get_tipo_display()} {periodo_obj.numero}" if periodo_obj else "Per├¡odo"
        # Se j├í veio do POST, prioriza o valor enviado, sen├úo usa o padr├úo do sistema
        context.update(construir_contexto_formulario_wizard_cronograma(dados=dados_wizard))
        turmas_objs = selecao_wizard['turmas']
        if request.POST.get('wizard_next'):
            erro_wizard = None
            if not selecao_wizard['valida']:
                erro_wizard = 'Selecione ao menos uma turma e um per├¡odo v├ílido para continuar.'
                context['erro_wizard'] = selecao_wizard['mensagem_erro']
                return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
            context['etapa'] = 3
            # Pr├®-visualiza├º├úo das li├º├Áes
            licoes_preview = construir_previa_cronograma(
                turmas=turmas_objs,
                periodo=periodo_obj,
                periodo_nome=periodo_nome,
                nome_licao_padrao=nome_licao_padrao,
                status=status,
            )
            context['licoes_preview'] = licoes_preview
            context['nome_licao_padrao'] = nome_licao_padrao
            return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
        if request.POST.get('wizard_back'):
            # Garante que o hor├írio padr├úo seja preenchido ao voltar
            if not horario:
                horario = horario_inicial
            context['etapa'] = 1
            context['anos_letivos'] = anos_letivos
            context['periodos'] = periodos
            context['turmas'] = turmas
            context['horario'] = horario
            return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
        return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)

    # Etapa 3: Confirma├º├úo e gera├º├úo
    if etapa == 3:
        transicao_wizard = preparar_transicao_wizard_cronograma(
            parametros=request.POST,
            ano_atual=ano_atual,
            turmas=turmas,
            tipo_periodo=tipo_periodo,
            hoje=hoje,
        )
        dados_wizard = transicao_wizard['dados']
        ano_letivo = dados_wizard['ano_letivo']
        periodo = dados_wizard['periodo']
        turmas_ids = dados_wizard['turmas_ids']
        material = dados_wizard['material']
        horario = dados_wizard['horario']
        status = dados_wizard['status']
        observacoes = dados_wizard['observacoes']
        nome_licao_padrao = dados_wizard['nome_licao_padrao']
        selecao_wizard = transicao_wizard['selecao']
        periodo_obj = selecao_wizard['periodo']
        periodo_nome = f"{periodo_obj.get_tipo_display()} {periodo_obj.numero}" if periodo_obj else "Per├¡odo"
        turmas_objs = selecao_wizard['turmas']
        if request.POST.get('wizard_confirm'):
            if not selecao_wizard['valida']:
                context.update({
                    'erro_wizard': selecao_wizard['mensagem_erro'],
                    'etapa': 2,
                })
                return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
            with transaction.atomic():
                licoes_geradas = criar_licoes_cronograma(
                    turmas=turmas_objs,
                    periodo=periodo_obj,
                    periodo_nome=periodo_nome,
                    nome_licao_padrao=nome_licao_padrao,
                    material=material,
                    observacoes=observacoes,
                    horario=horario,
                    status=status,
                )
            log_ebd_audit_event(
                request,
                'cronograma_wizard_gerado',
                ano_letivo=ano_letivo,
                periodo_id=periodo_obj.id,
                periodo_numero=periodo_obj.numero,
                tipo_periodo=tipo_periodo,
                turmas_ids=','.join(str(turma_id) for turma_id in turmas_ids),
                licoes_criadas=licoes_geradas,
            )
            resultado_msg = f'{licoes_geradas} li├º├Áes geradas com sucesso!' if licoes_geradas else 'Nenhuma nova li├º├úo foi gerada (j├í existiam para este per├¡odo/turma).'
            context['resultado_msg'] = resultado_msg
            context['etapa'] = 4
            return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
        if request.POST.get('wizard_back'):
            context.update(construir_contexto_formulario_wizard_cronograma(
                dados=dados_wizard,
                etapa=2,
            ))
            return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
        # Pr├®-visualiza├º├úo
        licoes_preview = construir_previa_cronograma(
            turmas=turmas_objs,
            periodo=periodo_obj,
            periodo_nome=periodo_nome,
            nome_licao_padrao=nome_licao_padrao,
            status=status,
        )
        context['licoes_preview'] = licoes_preview
        context['nome_licao_padrao'] = nome_licao_padrao
        return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)

    # Etapa 4: Resultado
    if etapa == 4:
        return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)


# --- SELE├ç├âO DE DADOS PARA C├ôPIA DO PER├ìODO ANTERIOR ---
@page_access_required('escola_biblica')
@require_http_methods(["GET", "POST"])
@transaction.atomic
@verificar_assinatura_valida
def copiar_periodo_selecao(request):
    ano_destino = request.GET.get('ano_destino') or request.POST.get('ano_destino')
    try:
        ano_destino_int = validar_ano_letivo(ano_destino)
    except ValueError:
        messages.error(request, 'Ano destino inv├ílido.')
        return redirect('escola_biblica:turma_list')
    ano_origem = ano_destino_int - 1
    ano_letivo_origem = AnoLetivo.objects.filter(ano=ano_origem).first()
    if not ano_letivo_origem:
        messages.error(request, f'N├úo existe ano letivo anterior ({ano_origem}) para copiar.')
        return redirect('escola_biblica:turma_list')
    turmas = filtrar_turmas_ebd(Turma.objects.filter(ano_letivo=ano_letivo_origem), request)
    classes = Classe.objects.filter(turma__in=turmas).distinct()
    alunos = filtrar_alunos_ebd(Aluno.objects.filter(turma__ano_letivo=ano_letivo_origem, ativo=True), request)
    if request.method == 'POST':
        turmas_ids = request.POST.getlist('turmas_selecionadas')
        classes_ids = request.POST.getlist('classes_selecionadas')
        alunos_ids = request.POST.getlist('alunos_selecionados')
        ano_letivo_dest, _ = AnoLetivo.objects.get_or_create(ano=ano_destino_int, defaults={'ativo': True})
        ano_letivo_dest = AnoLetivo.objects.select_for_update().get(pk=ano_letivo_dest.pk)

        # Copiar classes (s├│ cria se n├úo existir)
        resultado_copia = copiar_dados_selecionados_para_ano(
            turmas_origem=turmas,
            classes_origem=classes,
            alunos_origem=alunos,
            turmas_ids=turmas_ids,
            classes_ids=classes_ids,
            alunos_ids=alunos_ids,
            ano_letivo_destino=ano_letivo_dest,
        )
        licoes_geradas = 0
        turmas_por_calendario = agrupar_turmas_por_calendario(
            turmas=resultado_copia['turmas_destino'],
        )

        for (tipo_periodo, dia_semana, horario), turmas_destino in turmas_por_calendario.items():
            licoes_geradas += gerar_e_persistir_licoes_periodos(
                ano=ano_destino_int,
                tipo_periodo=tipo_periodo,
                turmas=turmas_destino,
                horario=horario,
                dia_semana=dia_semana,
            )

        resultado_final = consolidar_resultado_copia_seletiva(
            resultado_copia=resultado_copia,
            licoes_geradas=licoes_geradas,
        )

        msg = []
        if resultado_final['turmas_criadas']:
            msg.append(f"{resultado_final['turmas_criadas']} turma(s) criada(s)")
        if resultado_final['classes_criadas']:
            msg.append(f"{resultado_final['classes_criadas']} classe(s) criada(s)")
        if resultado_final['alunos_copiados']:
            msg.append(f"{resultado_final['alunos_copiados']} aluno(s) matriculado(s)")
        if resultado_final['membros_copiados']:
            msg.append(f"{resultado_final['membros_copiados']} membro(s) (professores/colaboradores) copiado(s)")
        if licoes_geradas:
            msg.append(f'{licoes_geradas} lição(ões) gerada(s)')
        if not resultado_final['tem_novidades']:
            messages.warning(request, 'Nenhum dado novo foi criado. Todos os dados selecionados j├í existiam para o ano/per├¡odo de destino.')
        else:
            messages.success(request, f"{' | '.join(msg)} do ano {ano_origem} para {ano_destino_int}.")
        log_ebd_audit_event(
            request,
            'copia_anual_seletiva',
            ano_origem=ano_origem,
            ano_destino=ano_destino_int,
            turmas_selecionadas=len(turmas_ids),
            classes_selecionadas=len(classes_ids),
            alunos_selecionados=len(alunos_ids),
            turmas_criadas=resultado_final['turmas_criadas'],
            classes_criadas=resultado_final['classes_criadas'],
            alunos_copiados=resultado_final['alunos_copiados'],
            membros_copiados=resultado_final['membros_copiados'],
            licoes_geradas=resultado_final['licoes_geradas'],
        )
        return redirect('escola_biblica:turma_list')
    return render(request, 'escola_biblica/copiar_periodo_selecao.html', {
        'ano_destino': ano_destino_int,
        'turmas': turmas,
        'classes': classes,
        'alunos': alunos,
    })



# --- COPIAR TURMAS/CLASSES/ALUNOS DO ANO ANTERIOR ---
@page_access_required('escola_biblica')
@require_POST
@transaction.atomic
@verificar_assinatura_valida
def copiar_turmas_ano_anterior(request):
    ano_destino = request.POST.get('ano_destino')
    try:
        ano_destino_int = validar_ano_letivo(ano_destino)
    except ValueError:
        messages.error(request, 'Ano destino inv├ílido.')
        return redirect('escola_biblica:turma_list')
    ano_letivo_dest, _ = AnoLetivo.objects.get_or_create(ano=ano_destino_int, defaults={'ativo': True})
    ano_letivo_dest = AnoLetivo.objects.select_for_update().get(pk=ano_letivo_dest.pk)
    ano_origem = ano_letivo_dest.ano - 1
    ano_letivo_origem = AnoLetivo.objects.filter(ano=ano_origem).first()
    if not ano_letivo_origem:
        messages.error(request, f'N├úo existe ano letivo anterior ({ano_origem}) para copiar.')
        return redirect('escola_biblica:turma_list')
    # Copiar classes se n├úo existirem
    turmas_origem = filtrar_turmas_ebd(Turma.objects.filter(ano_letivo=ano_letivo_origem), request)
    resultado_copia = copiar_ano_anterior_completo(
        turmas_origem=turmas_origem,
        ano_letivo_destino=ano_letivo_dest,
    )
    turmas_criadas = resultado_copia['turmas_criadas']
    alunos_copiados = resultado_copia['alunos_copiados']
    log_ebd_audit_event(
        request,
        'copia_anual_completa',
        ano_origem=ano_origem,
        ano_destino=ano_destino_int,
        turmas_criadas=turmas_criadas,
        alunos_copiados=alunos_copiados,
    )
    messages.success(request, f'{turmas_criadas} turmas e {alunos_copiados} alunos copiados do ano {ano_origem} para {ano_destino_int}.')
    return redirect('escola_biblica:turma_list')

# --- ABRIR NOVO PER├ìODO EBD ---

@page_access_required('escola_biblica')
@require_POST
@verificar_assinatura_valida
def abrir_novo_periodo(request):
    ano_letivo = request.POST.get('ano_letivo')
    tipo_periodo = request.POST.get('tipo_periodo')
    if tipo_periodo and not tipo_periodo_ebd_valido(tipo_periodo):
        messages.error(request, 'Tipo de periodo invalido.')
        return redirect('escola_biblica:turma_list')
    if not ano_letivo or not tipo_periodo:
        messages.error(request, 'Ano letivo e tipo de per├¡odo s├úo obrigat├│rios.')
        return redirect('escola_biblica:turma_list')
    try:
        ano_letivo_int = validar_ano_letivo(ano_letivo)
    except ValueError:
        messages.error(request, f'Ano letivo inv├ílido: {ano_letivo}')
        return redirect('escola_biblica:turma_list')
    resultado = abrir_proximo_periodo(
        ano_letivo=ano_letivo_int,
        tipo_periodo=tipo_periodo,
    )
    if not resultado['criado']:
        messages.info(request, 'O periodo solicitado ja estava preparado.')
    elif resultado['novo_ano']:
        messages.success(
            request,
            f'Ano {resultado["ano_destino"]} criado com o primeiro periodo de {tipo_periodo}.',
        )
    else:
        messages.success(
            request,
            f'Periodo {resultado["numero_periodo"]} criado para {resultado["ano_destino"]}/{tipo_periodo}.',
        )
    return redirect(
        f'/escola_biblica/copiar_periodo_selecao/?ano_destino={resultado["ano_destino"]}',
    )
# --- FECHAMENTO FORMAL DE PERÍODO ---
@login_required
@superintendente_required
@verificar_assinatura_valida
@require_http_methods(['GET', 'POST'])
def fechamento_periodo(request, periodo_id):
    periodo = get_object_or_404(PeriodoEBD, pk=periodo_id)
    igrejas = get_ebd_scope_churches(request)
    contexto = preparar_contexto_fechamento_periodo(
        periodo=periodo, igrejas=igrejas, igreja_ativa=getattr(request, 'igreja_ativa', None),
        turmas=filtrar_turmas_ebd(Turma.objects.all(), request),
    )
    if not contexto['valido']:
        raise PermissionDenied('Selecione uma igreja válida para fechar o período.')
    igreja, turmas = contexto['igreja'], contexto['turmas']
    motivo = request.POST.get('motivo_excecao', '') if request.method == 'POST' else ''
    resultado = executar_fluxo_fechamento_periodo(
        turmas=turmas, periodo=periodo, igreja=igreja, usuario=request.user,
        hoje=timezone.localdate(), confirmar=request.method == 'POST', motivo_excecao=motivo,
    )
    if request.method == 'POST' and resultado['fechado']:
        log_ebd_audit_event(request, 'periodo_fechado', periodo_id=periodo.id, igreja_id=igreja.id, tipo=resultado['diagnostico']['tipo_fechamento'])
        messages.success(request, 'Período fechado com sucesso.')
        return redirect('escola_biblica:dashboard')
    return render(
        request,
        'escola_biblica/fechamento_periodo.html',
        construir_contexto_template_fechamento_periodo(
            periodo=periodo, igreja=igreja,
            diagnostico=resultado['diagnostico'], motivo_excecao=motivo,
        ),
    )

# --- AJAX: Retorna nome do professor da turma ---
import csv
import json
from collections import defaultdict
from .forms import LicaoForm, AlunoForm, TurmaForm, FrequenciaForm, ClasseForm, AvaliacaoForm, OfertaClasseForm, TransferenciaAlunoForm, ChamadaPresencaFormSet, DepartamentoForm, GerarCronogramaForm


def _increment_dashboard_cache_counter(counter_name):
    key = f'ebd:dashboard:{counter_name}'
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, None)


@page_access_required('escola_biblica')
@verificar_assinatura_valida
@require_GET
def get_professor_nome(request):
    turma_id = request.GET.get('turma_id')
    nome = ''
    if turma_id:
        try:
            turma = filtrar_turmas_ebd(Turma.objects.all(), request).filter(pk=turma_id).first()
        except (TypeError, ValueError):
            turma = None
        if turma is not None:
            nome = turma.get_professor_nome() or ''
    return JsonResponse({'professor': nome})

@page_access_required('escola_biblica')
@verificar_assinatura_valida
def turma_create(request):
    ano_atual = date.today().year
    ano_letivo = obter_ano_letivo_para_criacao_turma(
        ano_letivo_raw=request.GET.get('ano_letivo'),
        ano_atual=ano_atual,
    )
    if request.method == 'POST':
        form = TurmaForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma cadastrada com sucesso!')
            return redirect(
                f"{reverse('escola_biblica:turma_list')}?ano_letivo={form.instance.ano_letivo.ano}",
            )
    else:
        form = TurmaForm(initial={'ano_letivo': ano_letivo.pk}, request=request)
        aplicar_igreja_filtro_inicial(form=form, igreja_id=request.GET.get('igreja_id'))
    return render(request, 'escola_biblica/turma_form.html', {'form': form})
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def departamento_create(request):
    if request.method == 'POST':
        form = DepartamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departamento cadastrado com sucesso!')
            return redirect('escola_biblica:departamento_list')
    else:
        form = DepartamentoForm()
    return render(request, 'escola_biblica/departamento_form.html', {'form': form, 'departamentos_sugeridos': DEPARTAMENTOS_SUGERIDOS})

@page_access_required('escola_biblica')
@verificar_assinatura_valida
def departamento_edit(request, pk):
    departamento = get_object_or_404(Departamento, pk=pk)
    if request.method == 'POST':
        form = DepartamentoForm(request.POST, instance=departamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departamento atualizado com sucesso!')
            return redirect('escola_biblica:departamento_list')
    else:
        form = DepartamentoForm(instance=departamento)
    return render(request, 'escola_biblica/departamento_form.html', {'form': form, 'departamento': departamento, 'departamentos_sugeridos': DEPARTAMENTOS_SUGERIDOS})

# --- PERFIL DO ALUNO E HIST├ôRICO DE TRANSFER├èNCIAS ---


@login_required
@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def aluno_detail(request, pk):
    """
    Detalhes do aluno.
    
    Secretaria/Superintendente: veem qualquer aluno
    Professores: veem apenas alunos de suas turmas
    """
    aluno = get_object_or_404(
        filtrar_alunos_ebd(
            Aluno.objects.select_related(
            'turma',
            'cadastro',
            'cadastro__pessoa',
            'cadastro__pessoa__tipo_pessoa',
            'cadastro__pessoa__status_pessoa',
            'cadastro__pessoa__grupo_casa',
            ),
            request,
        ),
        pk=pk,
    )
    
    # Verifica permiss├úo
    if not pode_ver_aluno(request.user, aluno):
        raise PermissionDenied("Voc├¬ n├úo tem permiss├úo para ver detalhes deste aluno.")
    
    transferencias = TransferenciaAluno.objects.filter(
        aluno__cadastro_id=aluno.cadastro_id,
    ).filter(
        Q(turma_origem__in=filtrar_turmas_ebd(Turma.objects.all(), request))
        | Q(turma_destino__in=filtrar_turmas_ebd(Turma.objects.all(), request)),
    ).select_related(
        'aluno',
        'turma_origem',
        'turma_destino',
        'usuario_responsavel',
    )
    matriculas_relacionadas = filtrar_alunos_ebd(
        aluno.cadastro.matriculas.select_related('turma', 'turma__ano_letivo'),
        request,
    ).exclude(pk=aluno.pk).order_by('-turma__ano_letivo__ano', '-id')
    perfil_usuario_vinculado_url = None
    pessoa_vinculada = getattr(aluno.cadastro, 'pessoa', None)
    usuario_vinculado = getattr(pessoa_vinculada, 'usuario', None) if pessoa_vinculada else None
    if usuario_vinculado and hasattr(usuario_vinculado, 'perfil'):
        perfil_usuario_vinculado_url = reverse('configuracao:perfil_usuario', args=[usuario_vinculado.pk])
    return render(request, 'escola_biblica/aluno_detail.html', {
        'aluno': aluno,
        'transferencias': transferencias,
        'matriculas_relacionadas': matriculas_relacionadas,
        'perfil_usuario_vinculado_url': perfil_usuario_vinculado_url,
    })


@login_required
@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def aluno_historico_consolidado(request, pk):
    alunos_escopo = filtrar_alunos_ebd(
        Aluno.objects.select_related(
            'turma',
            'turma__ano_letivo',
            'cadastro',
            'cadastro__pessoa',
        ),
        request,
    )

    aluno = alunos_escopo.filter(pk=pk).first()
    if aluno is None:
        aluno = alunos_escopo.filter(cadastro_id=pk).order_by(
            '-ativo', '-turma__ano_letivo__ano', '-updated_at', '-id'
        ).first()

    if aluno is None:
        messages.warning(request, 'Aluno n├úo encontrado no escopo atual. Abra o hist├│rico pela lista de alunos.')
        return redirect('escola_biblica:aluno_list')

    if not pode_ver_aluno(request.user, aluno):
        raise PermissionDenied("Voc├¬ n├úo tem permiss├úo para ver detalhes deste aluno.")

    cadastro = aluno.cadastro
    matriculas = list(
        alunos_escopo.filter(cadastro_id=cadastro.id)
        .order_by('-turma__ano_letivo__ano', '-updated_at', '-id')
    )

    transferencias = list(
        TransferenciaAluno.objects.filter(aluno__cadastro_id=cadastro.id).filter(
            Q(turma_origem__in=filtrar_turmas_ebd(Turma.objects.all(), request))
            | Q(turma_destino__in=filtrar_turmas_ebd(Turma.objects.all(), request)),
        )
        .select_related('aluno', 'turma_origem', 'turma_destino', 'usuario_responsavel')
        .order_by('-data_transferencia', '-id')
    )

    frequencias = list(
        filtrar_frequencias_ebd(Frequencia.objects.filter(aluno__cadastro_id=cadastro.id), request)
        .select_related('aluno', 'aluno__turma', 'aluno__turma__ano_letivo')
        .order_by('-data', '-id')
    )

    avaliacoes = list(
        filtrar_avaliacoes_ebd(Avaliacao.objects.filter(aluno__cadastro_id=cadastro.id), request)
        .select_related('aluno', 'aluno__turma', 'licao', 'licao__turma', 'licao__turma__ano_letivo')
        .order_by('-licao__data', '-id')
    )

    anos_ordenados = construir_historico_anual_aluno(
        matriculas=matriculas,
        transferencias=transferencias,
        frequencias=frequencias,
        avaliacoes=avaliacoes,
    )

    return render(request, 'escola_biblica/aluno_historico_consolidado.html', {
        'aluno': aluno,
        'cadastro': cadastro,
        'historico_anual': anos_ordenados,
        'total_matriculas': len(matriculas),
        'total_transferencias': len(transferencias),
        'total_frequencias': len(frequencias),
        'total_avaliacoes': len(avaliacoes),
    })


@page_access_required('escola_biblica')
@verificar_assinatura_valida
def aluno_vinculo_secretaria(request, pk):
    aluno = get_object_or_404(
        filtrar_alunos_ebd(
            Aluno.objects.select_related(
            'turma',
            'cadastro',
            'cadastro__pessoa',
            'cadastro__pessoa__tipo_pessoa',
            'cadastro__pessoa__status_pessoa',
            ),
            request,
        ),
        pk=pk,
    )
    cadastro = aluno.cadastro
    busca = request.GET.get('q', '').strip()

    pessoas_base = obter_pessoas_base_mesma_igreja(cadastro)
    pessoas_candidatas = listar_candidatos_vinculo_secretaria(cadastro, busca=busca, limite=30)

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'desvincular':
            cadastro.pessoa = None
            cadastro.save()
            messages.success(request, 'V├¡nculo com a Secretaria removido com sucesso.')
            return redirect('escola_biblica:aluno_vinculo_secretaria', pk=aluno.pk)

        pessoa_id = request.POST.get('pessoa_id')
        if not pessoa_id:
            messages.error(request, 'Selecione uma pessoa da Secretaria para vincular.')
        else:
            pessoa = get_object_or_404(pessoas_base, pk=pessoa_id)
            cadastro.pessoa = pessoa
            cadastro.save()
            messages.success(request, f'Aluno vinculado com sucesso ├á pessoa {pessoa.nome}.')
            return redirect('escola_biblica:aluno_vinculo_secretaria', pk=aluno.pk)

    return render(request, 'escola_biblica/aluno_vinculo_secretaria.html', {
        'aluno': aluno,
        'cadastro': cadastro,
        'pessoas_candidatas': pessoas_candidatas,
        'busca': busca,
    })


@page_access_required('escola_biblica')
@verificar_assinatura_valida
def aluno_vinculo_secretaria_lote(request):
    if not usuario_pode_gerenciar_ebd(request.user):
        raise PermissionDenied('Voc├¬ n├úo tem permiss├úo para gerenciar v├¡nculos em lote.')

    nome_filtro = request.GET.get('nome', '').strip()
    turma_filtro = request.GET.get('turma', '').strip()
    ativo_filtro = request.GET.get('ativo', '').strip()
    historico = request.GET.get('historico') == '1'

    ano_atual = date.today().year
    ano_filtro_raw = request.GET.get('ano', '').strip()
    try:
        ano_filtro = int(ano_filtro_raw) if ano_filtro_raw else ano_atual
    except ValueError:
        ano_filtro = ano_atual

    alunos_list = filtrar_alunos_ebd(Aluno.objects.all().order_by('nome'), request)

    if not historico:
        alunos_list = alunos_list.filter(turma__ano_letivo__ano=ano_filtro)
    if nome_filtro:
        alunos_list = alunos_list.filter(nome__icontains=nome_filtro)
    if turma_filtro:
        alunos_list = alunos_list.filter(turma_id=turma_filtro)
    if ativo_filtro in ('True', 'False'):
        alunos_list = alunos_list.filter(ativo=(ativo_filtro == 'True'))

    if not historico:
        alunos_list = colapsar_alunos_por_cadastro(alunos_list)

    aluno_por_cadastro = dict(alunos_list.values_list('cadastro_id', 'id'))
    cadastro_ids = alunos_list.filter(cadastro__pessoa__isnull=True).values_list('cadastro_id', flat=True).distinct()
    cadastros = list(
        CadastroAluno.objects.filter(id__in=cadastro_ids, pessoa__isnull=True)
        .select_related('igreja')
        .order_by('nome')
    )

    linhas = []
    for cadastro in cadastros:
        linhas.append({
            'cadastro': cadastro,
            'aluno_id': aluno_por_cadastro.get(cadastro.id),
            'pessoas': list(listar_candidatos_vinculo_secretaria(cadastro, limite=20)),
        })

    if request.method == 'POST':
        pessoa_ids_por_cadastro = {
            cadastro.id: request.POST.get(f'pessoa_cadastro_{cadastro.id}')
            for cadastro in cadastros
        }
        resultado_vinculos = aplicar_vinculos_selecionados_em_lote(
            cadastros=cadastros,
            pessoa_ids_por_cadastro=pessoa_ids_por_cadastro,
        )
        vinculos_realizados = resultado_vinculos['vinculos_realizados']

        if vinculos_realizados:
            exibicao = ', '.join(vinculos_realizados[:10])
            restantes = len(vinculos_realizados) - 10
            sufixo = f' (+{restantes} outro(s))' if restantes > 0 else ''
            messages.success(request, f'V├¡nculos aplicados: {exibicao}{sufixo}.')
        else:
            messages.info(request, 'Nenhum v├¡nculo foi selecionado para aplicar.')

        querystring_pos_post = request.GET.urlencode()
        redirect_url = reverse('escola_biblica:aluno_vinculo_secretaria_lote')
        if querystring_pos_post:
            redirect_url = f'{redirect_url}?{querystring_pos_post}'
        return redirect(redirect_url)

    return render(request, 'escola_biblica/aluno_vinculo_secretaria_lote.html', {
        'linhas': linhas,
        'total_cadastros': len(cadastros),
    })

# --- TRANSFER├èNCIA DE ALUNO ENTRE TURMAS/CLASSES ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
@transaction.atomic
def transferir_aluno(request, aluno_id):
    aluno = get_object_or_404(
        filtrar_alunos_ebd(Aluno.objects.select_related('turma', 'cadastro'), request),
        pk=aluno_id,
    )
    turma_origem = aluno.turma
    if request.method == 'POST':
        form = TransferenciaAlunoForm(request.POST, request=request)
        if form.is_valid():
            try:
                transferencia, matricula_destino = aluno.transferir_para(
                    turma_destino=form.cleaned_data['turma_destino'],
                    usuario_responsavel=request.user,
                    motivo=form.cleaned_data.get('motivo', ''),
                )
            except ValidationError as exc:
                form.add_error('turma_destino', exc.message)
            else:
                log_ebd_audit_event(
                    request,
                    'transferencia_aluno',
                    aluno_origem_id=aluno.id,
                    cadastro_id=aluno.cadastro_id,
                    turma_origem_id=getattr(transferencia, 'turma_origem_id', None),
                    turma_destino_id=getattr(transferencia, 'turma_destino_id', None),
                    matricula_destino_id=matricula_destino.id,
                )
                messages.success(request, f'Transfer├¬ncia realizada com sucesso para {transferencia.turma_destino}!')
                return redirect('escola_biblica:aluno_detail', pk=matricula_destino.pk)
    else:
        form = TransferenciaAlunoForm(request=request)
    return render(request, 'escola_biblica/transferir_aluno.html', {
        'form': form,
        'aluno': aluno,
        'turma_origem': turma_origem,
    })



# --- RELAT├ôRIO DE FREQU├èNCIA DETALHADO ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def relatorio_frequencia(request):
    turmas = filtrar_turmas_ebd(Turma.objects.all(), request)
    classes = filtrar_classes_ebd(Classe.objects.all(), request)
    periodo_ctx = get_ebd_periodo_filtro(request)
    contexto = construir_contexto_relatorio_alunos(
        turmas=turmas,
        classes=classes,
        alunos_escopo=filtrar_alunos_ebd(
            Aluno.objects.select_related('cadastro', 'turma', 'turma__classe').all(), request,
        ),
        parametros=request.GET,
        periodo_ctx=periodo_ctx,
    )
    # Exporta├º├úo CSV
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="relatorio_frequencia.csv"'
        writer = csv.writer(response)
        writer.writerow(['Cadastro', 'Turma de Refer├¬ncia', 'Classe', 'Presen├ºas', 'Total Aulas', 'Frequ├¬ncia (%)'])
        for aluno in contexto['alunos']:
            writer.writerow([
            aluno.nome_exibicao,
                aluno.turma,
                aluno.turma.classe if aluno.turma else '',
                aluno.presencas,
                aluno.total_freq,
                aluno.freq_percent if aluno.freq_percent is not None else '-',
            ])
        return response
    return render(request, 'escola_biblica/relatorio_frequencia.html', contexto)

# --- LISTAGEM DIN├éMICA DE CARGOS/FUN├ç├òES ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def cargos_ebd_list(request):
    from secretaria.models import MembroCargo, Cargo
    cargo_nome = request.GET.get('cargo')
    cargos_disponiveis = Cargo.objects.filter(is_ebd=True).values_list('nome', flat=True).distinct()
    colaboradores = MembroCargo.objects.select_related('membro', 'cargo').filter(cargo__is_ebd=True)
    colaboradores = filtrar_queryset_ebd(colaboradores, request, 'membro__igreja')
    if cargo_nome:
        colaboradores = colaboradores.filter(cargo__nome__iexact=cargo_nome)
    return render(request, 'escola_biblica/cargos_ebd_list.html', {
        'colaboradores': colaboradores,
        'cargos_disponiveis': cargos_disponiveis,
        'cargo_selecionado': cargo_nome,
    })

# --- GR├üFICOS DE EVOLU├ç├âO ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def graficos_evolucao(request):
    periodo_ctx = get_ebd_periodo_filtro(request)
    periodo_selecionado = periodo_ctx['periodo_selecionado']
    ano_letivo_selecionado = periodo_ctx['ano_letivo_selecionado']

    meses = construir_meses_evolucao(
        periodo=periodo_selecionado,
        ano_letivo=ano_letivo_selecionado,
        hoje=timezone.now().date(),
    )

    meses_fmt = [m.strftime('%m/%Y') for m in meses]
    classes = list(filtrar_classes_ebd(Classe.objects.all(), request).order_by('nome'))

    cadastros = list(
        filtrar_queryset_ebd(
            CadastroAluno.objects.prefetch_related('matriculas__turma__classe', 'matriculas__turma__ano_letivo'),
            request,
            'igreja',
        )
    )
    transferencias = list(
        TransferenciaAluno.objects.filter(aluno__cadastro_id__in=[cadastro.id for cadastro in cadastros])
        .select_related('turma_origem', 'turma_destino')
        .order_by('data_transferencia', 'id')
    ) if cadastros else []

    alunos_evolucao = construir_alunos_evolucao(
        cadastros=cadastros,
        transferencias=transferencias,
        meses=meses,
        ano_letivo=ano_letivo_selecionado,
    )

    ofertas_evolucao = construir_ofertas_evolucao(
        classes=classes,
        ofertas_escopo=filtrar_ofertas_ebd(OfertaClasse.objects.all(), request),
        meses=meses,
    )

    context = {
        'meses': json.dumps(meses_fmt),
        'alunos_evolucao': json.dumps(alunos_evolucao),
        'ofertas_evolucao': json.dumps(ofertas_evolucao),
        **periodo_ctx,
    }
    return render(request, 'escola_biblica/graficos_evolucao.html', context)

# --- DASHBOARD GR├üFICOS ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def dashboard_graficos(request):
    periodo_ctx = get_ebd_periodo_filtro(request)
    periodo_selecionado = periodo_ctx['periodo_selecionado']
    ano_letivo_selecionado = periodo_ctx['ano_letivo_selecionado']
    dados_graficos = construir_dados_dashboard_graficos(
        classes=filtrar_classes_ebd(Classe.objects.all(), request),
        alunos_escopo=filtrar_alunos_ebd(Aluno.objects.all(), request),
        ofertas_escopo=filtrar_ofertas_ebd(OfertaClasse.objects.all(), request),
        departamentos=dict(Classe.DEPARTAMENTO_CHOICES),
        periodo=periodo_selecionado,
        ano_letivo=ano_letivo_selecionado,
    )

    context = {
        **{chave: json.dumps(valor) for chave, valor in dados_graficos.items()},
        **periodo_ctx,
    }
    return render(request, 'escola_biblica/dashboard_graficos.html', context)

# --- OFERTAS POR CLASSE ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def oferta_classe_list(request):
    ofertas = filtrar_ofertas_ebd(
        OfertaClasse.objects.select_related('turma', 'classe').order_by('-data'),
        request,
    )
    ofertas = filtrar_queryset_por_turmas_do_usuario(
        queryset=ofertas, user=request.user, campo_turma='turma',
    )
    return render(request, 'escola_biblica/oferta_classe_list.html', {'ofertas': ofertas})

@page_access_required('escola_biblica')
@verificar_assinatura_valida
def oferta_classe_create(request):
    if request.method == 'POST':
        form = OfertaClasseForm(request.POST, request=request)
        if form.is_valid():
            oferta = form.save()
            log_ebd_audit_event(
                request,
                'oferta_create',
                oferta_id=oferta.id,
                turma_id=oferta.turma_id,
                data=oferta.data,
                valor=oferta.valor,
            )
            messages.success(request, 'Oferta registrada com sucesso!')
            return redirect('escola_biblica:oferta_classe_list')
    else:
        form = OfertaClasseForm(request=request)
    return render(request, 'escola_biblica/oferta_classe_form.html', {'form': form})

@page_access_required('escola_biblica')
@verificar_assinatura_valida
def oferta_classe_edit(request, pk):
    ofertas = filtrar_ofertas_ebd(
        OfertaClasse.objects.select_related('turma', 'classe'), request,
    )
    ofertas = filtrar_queryset_por_turmas_do_usuario(
        queryset=ofertas, user=request.user, campo_turma='turma',
    )
    oferta = get_object_or_404(ofertas, pk=pk)
    if request.method == 'POST':
        form = OfertaClasseForm(request.POST, instance=oferta, request=request)
        if form.is_valid():
            oferta_atualizada = form.save()
            log_ebd_audit_event(
                request,
                'oferta_edit',
                oferta_id=oferta_atualizada.id,
                turma_id=oferta_atualizada.turma_id,
                data=oferta_atualizada.data,
                valor=oferta_atualizada.valor,
            )
            messages.success(request, 'Oferta atualizada com sucesso!')
            return redirect('escola_biblica:oferta_classe_list')
    else:
        form = OfertaClasseForm(instance=oferta, request=request)
    return render(request, 'escola_biblica/oferta_classe_form.html', {'form': form, 'oferta': oferta})

@login_required
@superintendente_required
@verificar_assinatura_valida
def oferta_classe_delete(request, pk):
    oferta = get_object_or_404(
        filtrar_ofertas_ebd(OfertaClasse.objects.select_related('turma', 'classe'), request),
        pk=pk,
    )
    if request.method == 'POST':
        oferta_id = oferta.id
        turma_id = oferta.turma_id
        data = oferta.data
        valor = oferta.valor
        oferta.delete()
        log_ebd_audit_event(
            request,
            'oferta_delete',
            oferta_id=oferta_id,
            turma_id=turma_id,
            data=data,
            valor=valor,
        )
        messages.success(request, 'Oferta exclu├¡da com sucesso!')
        return redirect('escola_biblica:oferta_classe_list')
    return render(request, 'escola_biblica/oferta_classe_confirm_delete.html', {'oferta': oferta})

# --- RELAT├ôRIO DE ALUNOS ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def relatorio_alunos(request):
    turmas = filtrar_turmas_ebd(Turma.objects.all(), request)
    classes = filtrar_classes_ebd(Classe.objects.all(), request)
    periodo_ctx = get_ebd_periodo_filtro(request)
    contexto = construir_contexto_relatorio_alunos(
        turmas=turmas,
        classes=classes,
        alunos_escopo=filtrar_alunos_ebd(
            Aluno.objects.select_related('cadastro', 'turma', 'turma__classe').all(), request,
        ),
        parametros=request.GET,
        periodo_ctx=periodo_ctx,
    )
    return render(request, 'escola_biblica/relatorio_alunos.html', contexto)
# --- LICOES ---
 
 # --- AVALIA├ç├òES ---
@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def avaliacao_list(request):
    avaliacoes = filtrar_avaliacoes_ebd(
        Avaliacao.objects.select_related('aluno', 'aluno__cadastro', 'aluno__turma', 'licao', 'licao__turma').all(),
        request,
    )
    avaliacoes = filtrar_queryset_por_turmas_do_usuario(
        queryset=avaliacoes, user=request.user, campo_turma='aluno__turma',
    )
    avaliacoes = avaliacoes.order_by('-licao__data', 'aluno__cadastro__nome')
    return render(request, 'escola_biblica/avaliacao_list.html', {'avaliacoes': avaliacoes})

@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def avaliacao_create(request):
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Avalia├º├úo cadastrada com sucesso!')
            return redirect('escola_biblica:avaliacao_list')
    else:
        form = AvaliacaoForm(request=request)
    return render(request, 'escola_biblica/avaliacao_form.html', {'form': form})

@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def avaliacao_edit(request, pk):
    avaliacoes = filtrar_avaliacoes_ebd(
        Avaliacao.objects.select_related('aluno', 'aluno__cadastro', 'licao'), request,
    )
    avaliacoes = filtrar_queryset_por_turmas_do_usuario(
        queryset=avaliacoes, user=request.user, campo_turma='aluno__turma',
    )
    avaliacao = get_object_or_404(avaliacoes, pk=pk)
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=avaliacao, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Avalia├º├úo atualizada com sucesso!')
            return redirect('escola_biblica:avaliacao_list')
    else:
        form = AvaliacaoForm(instance=avaliacao, request=request)
    return render(request, 'escola_biblica/avaliacao_form.html', {'form': form, 'avaliacao': avaliacao})

@login_required
@superintendente_required
@verificar_assinatura_valida
def avaliacao_delete(request, pk):
    avaliacao = get_object_or_404(
        filtrar_avaliacoes_ebd(Avaliacao.objects.select_related('aluno', 'aluno__cadastro', 'licao'), request),
        pk=pk,
    )
    if request.method == 'POST':
        avaliacao_id = avaliacao.id
        aluno_id = avaliacao.aluno_id
        licao_id = avaliacao.licao_id
        avaliacao.delete()
        log_ebd_audit_event(
            request,
            'avaliacao_delete',
            avaliacao_id=avaliacao_id,
            aluno_id=aluno_id,
            licao_id=licao_id,
        )
        messages.success(request, 'Avalia├º├úo exclu├¡da com sucesso!')
        return redirect('escola_biblica:avaliacao_list')
    return render(request, 'escola_biblica/avaliacao_confirm_delete.html', {'avaliacao': avaliacao})
@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def _legado_licao_list(request):
    hoje = timezone.now().date()
    
    # Buscar li├º├Áes com escopo correto
    turmas_escopo = filtrar_turmas_para_usuario(
        filtrar_turmas_ebd(Turma.objects.all(), request), request.user,
    )
    licoes_scope = Licao.objects.filter(turma__in=turmas_escopo).distinct()
    
    # Buscar per├¡odos que t├¬m li├º├Áes no escopo do usu├írio (evitar vazamento de dados)
    periodos_ids = licoes_scope.values_list('data__year', flat=True).distinct()
    periodos = PeriodoEBD.objects.select_related('ano_letivo').filter(
        data_inicio__year__in=periodos_ids
    ).order_by('-ano_letivo__ano', '-numero')
    
    # Identificar per├¡odo atual
    periodo_atual = periodos.filter(data_inicio__lte=hoje, data_fim__gte=hoje).first()
    
    # Filtro por GET
    periodo_id = request.GET.get('periodo')
    if periodo_id:
        periodo_selecionado = periodos.filter(id=periodo_id).first()
    else:
        periodo_selecionado = periodo_atual
    
    licoes = licoes_scope
    if periodo_selecionado:
        licoes = licoes.filter(periodo=periodo_selecionado)
    
    # Buscar turmas para o filtro (apenas do escopo do usu├írio)
    turma_nomes = turmas_escopo.values_list('nome', flat=True).distinct().order_by('nome')
    turma_nome = request.GET.get('turma')
    if turma_nome:
        licoes = licoes.filter(turma__nome=turma_nome)

    # Filtro de professor (apenas do escopo do usu├írio)
    from secretaria.models import Membro, MembroCargo
    igrejas_escopo = get_ebd_scope_churches(request)
    membros_professor_ids = MembroCargo.objects.filter(
        cargo__is_ebd=True,
        cargo__nome__icontains='professor',
        data_fim__isnull=True,
        membro__igreja__in=igrejas_escopo
    ).values_list('membro_id', flat=True)
    professores = Membro.objects.filter(chave__in=membros_professor_ids, igreja__in=igrejas_escopo).order_by('nome')
    professor_id = request.GET.get('professor')
    if professor_id:
        licoes = licoes.filter(professor_id=professor_id)
    
    return render(request, 'escola_biblica/licao_list.html', {
        'licoes': licoes,
        'periodos': periodos,
        'periodo_selecionado': periodo_selecionado,
        'turma_nomes': turma_nomes,
        'turma_nome': turma_nome,
        'professores': professores,
        'professor_id': professor_id,
    })

@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def licao_list(request):
    hoje = timezone.now().date()
    turmas_escopo = filtrar_turmas_para_usuario(
        filtrar_turmas_ebd(Turma.objects.all(), request), request.user,
    )
    contexto = construir_listagem_licoes(
        turmas_escopo=turmas_escopo,
        igrejas_escopo=get_ebd_scope_churches(request),
        parametros=request.GET,
        hoje=hoje,
    )
    return render(request, 'escola_biblica/licao_list.html', contexto)


@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def licao_create(request):
    turmas = filtrar_turmas_para_usuario(
        filtrar_turmas_ebd(Turma.objects.all(), request), request.user,
    )
    if request.method == 'POST':
        form = LicaoForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Li├º├úo cadastrada com sucesso!')
            return redirect('escola_biblica:licao_list')
    else:
        form = LicaoForm(request=request)
    return render(request, 'escola_biblica/licao_form.html', {'form': form, 'turmas': turmas})

@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def licao_edit(request, pk):
    turmas = filtrar_turmas_para_usuario(
        filtrar_turmas_ebd(Turma.objects.all(), request), request.user,
    )
    licao = get_object_or_404(
        Licao.objects.select_related('turma').filter(
            turma__in=turmas,
        ),
        pk=pk,
    )
    if request.method == 'POST':
        form = LicaoForm(request.POST, request.FILES, instance=licao, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Li├º├úo atualizada com sucesso!')
            return redirect('escola_biblica:licao_list')
    else:
        form = LicaoForm(instance=licao, request=request)
    return render(request, 'escola_biblica/licao_form.html', {'form': form, 'licao': licao, 'turmas': turmas})

@login_required
@superintendente_required
@verificar_assinatura_valida
def licao_delete(request, pk):
    licao = get_object_or_404(
        Licao.objects.select_related('turma', 'turma__classe').filter(
            turma__in=filtrar_turmas_ebd(Turma.objects.all(), request),
        ),
        pk=pk,
    )
    if request.method == 'POST':
        if licao.avaliacao_set.exists():
            messages.error(
                request,
                'Esta lição possui avaliações registradas. Exclua as avaliações antes de excluir a lição.',
            )
            return redirect('escola_biblica:licao_list')
        licao_id = licao.id
        turma_id = licao.turma_id
        data = licao.data
        licao.delete()
        log_ebd_audit_event(
            request,
            'licao_delete',
            licao_id=licao_id,
            turma_id=turma_id,
            data=data,
        )
        messages.success(request, 'Li├º├úo exclu├¡da com sucesso!')
        return redirect('escola_biblica:licao_list')
    return render(request, 'escola_biblica/licao_confirm_delete.html', {'licao': licao})
# --- CLASSES ---
# --- CLASSES ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def classe_list(request):
    classes = filtrar_classes_ebd(Classe.objects.all(), request)
    igreja_filtro = request.GET.get('igreja_id')
    if igreja_filtro:
        try:
            classes = classes.filter(igreja_id=int(igreja_filtro))
        except ValueError:
            pass
    return render(request, 'escola_biblica/classe_list.html', {'classes': classes})

@page_access_required('escola_biblica')
@verificar_assinatura_valida
def classe_create(request):
    if request.method == 'POST':
        form = ClasseForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Classe cadastrada com sucesso!')
            return redirect('escola_biblica:classe_list')
    else:
        form = ClasseForm(request=request)
        aplicar_igreja_filtro_inicial(form=form, igreja_id=request.GET.get('igreja_id'))
    return render(request, 'escola_biblica/classe_form.html', {'form': form})

@page_access_required('escola_biblica')
@verificar_assinatura_valida
def classe_edit(request, pk):
    classe = get_object_or_404(filtrar_classes_ebd(Classe.objects.all(), request), pk=pk)
    if request.method == 'POST':
        form = ClasseForm(request.POST, instance=classe, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Classe atualizada com sucesso!')
            return redirect('escola_biblica:classe_list')
    else:
        form = ClasseForm(instance=classe, request=request)
    return render(request, 'escola_biblica/classe_form.html', {'form': form, 'classe': classe})

@login_required
@superintendente_required
@verificar_assinatura_valida
def classe_delete(request, pk):
    classe = get_object_or_404(filtrar_classes_ebd(Classe.objects.all(), request), pk=pk)
    if request.method == 'POST':
        classe_id = classe.id
        igreja_id = classe.igreja_id
        try:
            classe.delete()
        except ProtectedError:
            messages.error(request, 'Esta classe possui turmas vinculadas e não pode ser excluída.')
            return redirect('escola_biblica:classe_list')
        log_ebd_audit_event(request, 'classe_delete', classe_id=classe_id, igreja_id=igreja_id)
        messages.success(request, 'Classe exclu├¡da com sucesso!')
        return redirect('escola_biblica:classe_list')
    return render(request, 'escola_biblica/classe_confirm_delete.html', {'classe': classe})






@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
@log_ebd_endpoint('dashboard')
def dashboard(request):
    auto_sync_ebd_periodos_e_licoes(request)
    perfil = getattr(request.user, 'perfil', None) or getattr(request.user, 'perfil_usuario', None)
    ministerio = getattr(perfil, 'ministerio', None)

    if request.method == 'POST' and request.POST.get('acao') == 'publicar_resumo_semanal':
        if not ministerio or not usuario_pode_gerenciar_ebd(request.user):
            messages.error(request, 'Você não tem permissão para publicar o resumo semanal da EBD.')
            return redirect('escola_biblica:dashboard')

        publicacao = publicar_resumo_semanal_dashboard(
            ministerio=ministerio,
            autor=request.user,
            igrejas_escopo=get_ebd_scope_churches(request),
            hoje=timezone.localdate(),
        )
        log_ebd_audit_event(
            request,
            'resumo_semanal_publicado',
            ministerio_id=ministerio.id,
            inicio=publicacao['inicio'],
            fim=publicacao['fim'],
        )
        messages.success(request, 'Resumo semanal da EBD publicado em Avisos para secretaria/liderança.')
        return redirect('escola_biblica:dashboard')

    turmas = filtrar_turmas_ebd(Turma.objects.all(), request)
    alunos = filtrar_alunos_ebd(Aluno.objects.all(), request)
    classes = filtrar_classes_ebd(Classe.objects.all(), request)
    licoes = Licao.objects.filter(turma__in=turmas).distinct()
    avaliacoes = filtrar_avaliacoes_ebd(Avaliacao.objects.all(), request)
    igrejas_escopo = get_ebd_scope_churches(request)
    ofertas_escopo = filtrar_ofertas_ebd(OfertaClasse.objects.all(), request)

    igreja = getattr(request, 'igreja_ativa', None)
    if igreja is None and igrejas_escopo.count() == 1:
        igreja = igrejas_escopo.first()

    hoje = date.today()
    ano_atual = hoje.year

    periodo_ctx = get_ebd_periodo_filtro(request)
    ebd_config_source_info = get_ebd_config_source_info(request)
    ebd_pontos_config = get_ebd_pontos_config_com_fallback(request)
    dia_ebd = get_ebd_dia_semana(request)

    cache_version = cache.get('ebd:dashboard:version') or 1
    tipo_periodo = periodo_ctx['tipo_periodo']
    cache_key = construir_chave_cache_dashboard(
        versao=cache_version,
        usuario_id=request.user.pk,
        igreja_id=getattr(igreja, 'pk', None),
        tipo_periodo=tipo_periodo,
        ano_letivo=request.GET.get('ano_letivo', ''),
        periodo=request.GET.get('periodo', ''),
        data_relatorio=request.GET.get('data_relatorio', ''),
    )
    cached_html = cache.get(cache_key)
    if cached_html is not None:
        _increment_dashboard_cache_counter('cache_hit')
        logger.info(
            'ebd.dashboard.cache result=hit user_id=%s igreja_ativa_id=%s tipo_periodo=%s',
            request.user.pk,
            getattr(igreja, 'pk', None),
            tipo_periodo,
        )
        return HttpResponse(cached_html)

    _increment_dashboard_cache_counter('cache_miss')
    logger.info(
        'ebd.dashboard.cache result=miss user_id=%s igreja_ativa_id=%s tipo_periodo=%s',
        request.user.pk,
        getattr(igreja, 'pk', None),
        tipo_periodo,
    )

    contexto_template_dashboard = construir_contexto_completo_dashboard(
        request=request,
        turmas=turmas,
        alunos=alunos,
        classes=classes,
        licoes=licoes,
        avaliacoes=avaliacoes,
        ofertas_escopo=ofertas_escopo,
        igrejas_escopo=igrejas_escopo,
        igreja=igreja,
        ministerio=ministerio,
        hoje=hoje,
        ano_atual=ano_atual,
        periodo_ctx=periodo_ctx,
        ebd_config_source_info=ebd_config_source_info,
        ebd_pontos_config=ebd_pontos_config,
        dia_ebd=dia_ebd,
    )
    response = render(request, 'escola_biblica/dashboard.html', contexto_template_dashboard)
    cache.set(cache_key, response.content, 120)
    return response

@login_required
@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def aluno_list(request):
    """
    Lista de alunos.
    
    Secretaria/Superintendente EBD: veem todos os alunos
    Professores: veem apenas alunos de suas turmas
    """

    # Verifica se ├® secretaria EBD (acesso total)
    is_secretaria = (
        request.user.is_superuser or 
        request.user.groups.filter(name__in=['Secretaria EBD', 'Superintendente EBD']).exists()
    )

    if is_secretaria:
        # Secretaria v├¬ todos os alunos
        alunos_list = Aluno.objects.all().order_by('nome')
        alunos_list = filtrar_alunos_ebd(alunos_list, request)
    else:
        # Professor v├¬ apenas alunos de suas turmas
        turmas_professor = get_turmas_professor(request.user)
        alunos_list = filtrar_alunos_ebd(Aluno.objects.filter(turma__in=turmas_professor).order_by('nome').distinct(), request)

    turmas_filtro = filtrar_turmas_ebd(Turma.objects.all(), request).order_by('nome')
    if not is_secretaria:
        turmas_filtro = turmas_filtro.filter(id__in=turmas_professor.values('id'))

    contexto_listagem = construir_contexto_listagem_alunos(
        alunos_escopo=alunos_list,
        turmas_escopo=turmas_filtro,
        anos_letivos=AnoLetivo.objects.order_by('-ano'),
        parametros=request.GET,
        ano_atual=date.today().year,
    )
    alunos_list = contexto_listagem['alunos']

    if request.method == 'POST' and is_secretaria and request.POST.get('acao') == 'tentar_vinculo_lote':
        resultado_vinculos = tentar_vinculos_listagem_alunos(alunos_list)
        vinculados = resultado_vinculos['vinculados']
        sem_correspondencia = resultado_vinculos['sem_correspondencia']
        vinculados_detalhes = resultado_vinculos['detalhes']

        if vinculados:
            exibicao = ', '.join(vinculados_detalhes[:10])
            restantes = len(vinculados_detalhes) - 10
            sufixo = f' (+{restantes} outro(s))' if restantes > 0 else ''
            messages.success(
                request,
                f'{vinculados} cadastro(s) vinculados automaticamente ├á Secretaria. Vinculados: {exibicao}{sufixo}.',
            )
        if sem_correspondencia:
            messages.warning(request, f'{sem_correspondencia} cadastro(s) continuam sem correspond├¬ncia segura.')
        if not vinculados and not sem_correspondencia:
            messages.info(request, 'Nenhum cadastro eleg├¡vel para tentativa de v├¡nculo autom├ítico.')

        querystring_pos_post = request.GET.urlencode()
        redirect_url = reverse('escola_biblica:aluno_list')
        if querystring_pos_post:
            redirect_url = f'{redirect_url}?{querystring_pos_post}'
        return redirect(redirect_url)

    total_alunos = alunos_list.count()
    
    alunos = paginar_queryset(
        queryset=alunos_list, pagina=request.GET.get('page'), por_pagina=20,
    )
    contexto_template = construir_contexto_template_listagem_alunos(
        contexto_listagem=contexto_listagem,
        alunos_paginados=alunos,
        total_alunos=total_alunos,
        usuario_pode_vincular=is_secretaria,
    )
    return render(request, 'escola_biblica/aluno_list.html', contexto_template)

@page_access_required('escola_biblica')
@verificar_assinatura_valida
def aluno_create(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return redirect('escola_biblica:aluno_list')
    else:
        form = AlunoForm(request=request)
    return render(request, 'escola_biblica/aluno_form.html', {'form': form})

@login_required
@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def turma_list(request):
    auto_sync_ebd_periodos_e_licoes(request)
    ebd_config_source_info = get_ebd_config_source_info(request)
    now = date.today()
    ano_letivo_filtro = request.GET.get('ano_letivo')
    periodo_filtro = request.GET.get('periodo')
    igreja_filtro = request.GET.get('igreja_id')
    turma_filtro = request.GET.get('turma', '').strip()
    nome_filtro = request.GET.get('nome', '').strip()
    classe_filtro = request.GET.get('classe', '').strip()

    # Sele├º├úo do ano letivo
    # Sugerir c├│pia de turmas/classes/alunos do ano anterior se o ano letivo acabou de ser criado e n├úo h├í turmas
    tipo_periodo = get_ebd_tipo_periodo(request)
    contexto_periodos = preparar_contexto_periodos_listagem_turmas(
        ano_letivo_raw=ano_letivo_filtro,
        periodo_raw=periodo_filtro,
        tipo_periodo=tipo_periodo,
        hoje=now,
    )
    ano_letivo_selecionado = contexto_periodos['ano_letivo_selecionado']
    periodo_atual = contexto_periodos['periodo_atual']
    periodo_selecionado = contexto_periodos['periodo_selecionado']

    # Base de turmas do ano letivo (considerando escopo/permissão)
    turmas_base = Turma.objects.filter(ano_letivo=ano_letivo_selecionado)
    if igreja_filtro:
        try:
            turmas_base = turmas_base.filter(igreja_id=int(igreja_filtro))
        except ValueError:
            pass
    
    # Verifica se ├® secretaria EBD (acesso total) ou professor (acesso limitado)
    turmas_base = filtrar_turmas_para_usuario(turmas_base, request.user)

    # Aplica o escopo antes de montar as opcoes auxiliares dos filtros.
    turmas_base = filtrar_turmas_ebd(turmas_base, request)

    filtros_listagem = construir_filtros_listagem_turmas(
        turmas_base=turmas_base,
        periodo=periodo_selecionado,
        turma_filtro=turma_filtro,
        nome_filtro=nome_filtro,
        classe_filtro=classe_filtro,
    )
    turmas_list = filtros_listagem['turmas_list']
    turmas_list = filtrar_turmas_ebd(turmas_list, request)
    turmas_total = turmas_list.count()

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    turmas = paginar_queryset(
        queryset=turmas_list, pagina=request.GET.get('page'), por_pagina=20,
    )
    # Banner do per├¡odo EBD atual
    ebd_periodo_atual = periodo_atual or periodo_selecionado
    status_periodo = construir_status_periodo(periodo=ebd_periodo_atual, hoje=now)
    context = construir_contexto_template_listagem_turmas(
        turmas=turmas,
        turmas_total=turmas_total,
        contexto_periodos=contexto_periodos,
        filtros_listagem=filtros_listagem,
        turma_filtro=turma_filtro,
        classe_filtro=classe_filtro,
        tipo_periodo=tipo_periodo,
        now=now,
        request=request,
        status_periodo=status_periodo,
        ebd_periodo_atual=ebd_periodo_atual,
        ebd_config_source_info=ebd_config_source_info,
        querystring=querystring,
    )
    return render(request, 'escola_biblica/turma_list.html', context)

# --- EDITAR TURMA ---
from .forms import TurmaForm

@page_access_required('escola_biblica')
@verificar_assinatura_valida
def turma_edit(request, pk):
    turma = get_object_or_404(filtrar_turmas_ebd(Turma.objects.all(), request), pk=pk)
    if request.method == 'POST':
        form = TurmaForm(request.POST, instance=turma, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma atualizada com sucesso!')
            return redirect(
                f"{reverse('escola_biblica:turma_list')}?ano_letivo={form.instance.ano_letivo.ano}",
            )
    else:
        form = TurmaForm(instance=turma, request=request)
    return render(request, 'escola_biblica/turma_form.html', {'form': form, 'turma': turma})

# --- EXCLUIR TURMA ---
@login_required
@superintendente_required
@verificar_assinatura_valida
def turma_delete(request, pk):
    turma = get_object_or_404(
        filtrar_turmas_ebd(Turma.objects.select_related('igreja', 'classe'), request),
        pk=pk,
    )
    if request.method == 'POST':
        turma_id = turma.id
        igreja_id = turma.igreja_id
        ano_letivo_id = turma.ano_letivo_id
        try:
            turma.delete()
        except ProtectedError:
            messages.error(request, 'Esta turma possui dados vinculados e não pode ser excluída.')
            return redirect('escola_biblica:turma_list')
        log_ebd_audit_event(
            request,
            'turma_delete',
            turma_id=turma_id,
            igreja_id=igreja_id,
            ano_letivo_id=ano_letivo_id,
        )
        messages.success(request, 'Turma exclu├¡da com sucesso!')
        return redirect('escola_biblica:turma_list')
    return render(request, 'escola_biblica/turma_confirm_delete.html', {'turma': turma})

@page_access_required('escola_biblica')
@verificar_assinatura_valida
def frequencia_list(request):
    frequencias_list = filtrar_frequencias_ebd(
        Frequencia.objects.select_related('aluno', 'aluno__cadastro', 'aluno__turma').all().order_by('-data'),
        request,
    )
    frequencias = paginar_queryset(
        queryset=frequencias_list, pagina=request.GET.get('page'), por_pagina=30,
    )
    return render(request, 'escola_biblica/frequencia_list.html', {'frequencias': frequencias})


# --- NOVA VIEW: Gera├º├úo autom├ítica de per├¡odos e li├º├Áes em lote ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
@transaction.atomic
def gerar_cronograma(request):
    ano_atual = date.today().year
    turmas = filtrar_turmas_ebd(
        Turma.objects.filter(ano_letivo__ano=ano_atual, ano_letivo__ativo=True),
        request,
    )
    turma_selecionada = None
    tipo_periodo = get_ebd_tipo_periodo(request)
    if request.method == 'POST':
        form = GerarCronogramaForm(request.POST, request=request, turmas=turmas)
        if form.is_valid():
            turma_selecionada = form.cleaned_data['turma']
            material = form.cleaned_data.get('material', '')
            observacoes = form.cleaned_data.get('observacoes', '')
            status = form.cleaned_data.get('status', 'ativa')
            resultado_geracao = gerar_cronograma_para_turma(
                ano=ano_atual,
                turma_selecionada=turma_selecionada,
                turmas_escopo=turmas,
                material=material,
                observacoes=observacoes,
                status=status,
            )
            criadas = resultado_geracao['criadas']
            tipo_periodo = resultado_geracao['tipo_periodo']
            if criadas:
                messages.success(request, f'{criadas} li├º├Áes geradas com sucesso!')
            else:
                messages.info(request, 'Nenhuma nova li├º├úo foi gerada (j├í existem para este per├¡odo/turma).')
            return redirect('escola_biblica:gerar_cronograma')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erro no campo {field}: {error}')
    else:
        form = GerarCronogramaForm(request=request, turmas=turmas)
        turma_id = request.GET.get('turma')
        if turma_id:
            turma_selecionada = turmas.filter(id=turma_id).first()
    aulas = Licao.objects.filter(turma=turma_selecionada) if turma_selecionada else Licao.objects.none()
    aulas = filtrar_e_paginar_aulas_geradas(
        aulas=aulas,
        data=request.GET.get('data', ''),
        tema=request.GET.get('tema', ''),
        pagina=request.GET.get('page'),
    )
    aulas_count = aulas.paginator.count
    return render(request, 'escola_biblica/gerar_cronograma_form.html', {
        'form': form,
        'turmas': turmas,
        'aulas': aulas,
        'aulas_count': aulas_count,
        'turma_selecionada': turma_selecionada,
        'tipo_periodo': tipo_periodo,
        'ano_atual': ano_atual,
    })
