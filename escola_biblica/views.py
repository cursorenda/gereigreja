# --- RELAT├ôRIO GERAL DO DIA DA EBD ---
import time
import logging
import hashlib
from functools import wraps
from django.db.models import Count, Sum, Q, OuterRef, Subquery
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from core.decorators import secretaria_ebd_required, user_passes_test_or_403, page_access_required
from django.core.exceptions import PermissionDenied, ValidationError
from core.utils import get_igrejas_permitidas, get_request_scoped_churches
from contas.constants import SECRETARIA_EBD, user_has_permission_level_or_higher
from secretaria.models import MembroCargo

logger = logging.getLogger(__name__)


def log_ebd_endpoint(action):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            started_at = time.perf_counter()
            status_code = 500
            user_id = getattr(request.user, 'pk', None)
            igreja_ativa = getattr(request, 'igreja_ativa', None)
            igreja_ativa_id = getattr(igreja_ativa, 'pk', None)
            try:
                response = view_func(request, *args, **kwargs)
                status_code = getattr(response, 'status_code', 200)
                return response
            except Exception:
                logger.exception(
                    'ebd.endpoint.error action=%s method=%s path=%s user_id=%s igreja_ativa_id=%s',
                    action,
                    request.method,
                    request.path,
                    user_id,
                    igreja_ativa_id,
                )
                raise
            finally:
                elapsed_ms = (time.perf_counter() - started_at) * 1000
                logger.info(
                    'ebd.endpoint.metric action=%s method=%s path=%s status=%s elapsed_ms=%.2f user_id=%s igreja_ativa_id=%s',
                    action,
                    request.method,
                    request.path,
                    status_code,
                    elapsed_ms,
                    user_id,
                    igreja_ativa_id,
                )

        return _wrapped

    return decorator


def log_ebd_audit_event(request, action, **extra):
    igreja_ativa = getattr(request, 'igreja_ativa', None)
    payload = {
        'action': action,
        'user_id': getattr(request.user, 'pk', None),
        'igreja_ativa_id': getattr(igreja_ativa, 'pk', None),
        **extra,
    }
    kv = ' '.join(f'{key}={value}' for key, value in payload.items())
    logger.info('ebd.audit %s', kv)


def _build_chamada_idempotency_key(request, turma_id, data_selecionada):
    total_forms = int(request.POST.get('form-TOTAL_FORMS') or 0)
    alunos_payload = []
    for idx in range(total_forms):
        alunos_payload.append(
            (
                request.POST.get(f'form-{idx}-aluno_id', ''),
                1 if request.POST.get(f'form-{idx}-presente') else 0,
                1 if request.POST.get(f'form-{idx}-trouxe_biblia') else 0,
                1 if request.POST.get(f'form-{idx}-trouxe_revista') else 0,
                1 if request.POST.get(f'form-{idx}-trouxe_visitante') else 0,
                1 if request.POST.get(f'form-{idx}-trouxe_oferta') else 0,
            )
        )

    raw = json.dumps(
        {
            'user_id': request.user.pk,
            'turma_id': turma_id,
            'data': data_selecionada.isoformat() if data_selecionada else '',
            'valor_oferta': request.POST.get('valor_oferta', ''),
            'alunos': alunos_payload,
        },
        sort_keys=True,
        ensure_ascii=True,
    )
    digest = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    return f'ebd:chamada:idempotency:{digest}'

# --- FUN├ç├òES HELPER DE PERMISS├òES ---
def pode_acessar_chamada_turma(user, turma):
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


def get_turmas_professor(user):
    """
    Retorna turmas onde o usu├írio ├® professor.
    """
    from .models import Turma
    
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


def pode_ver_aluno(user, aluno):
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


def usuario_pode_gerenciar_ebd(user):
    return user.is_superuser or user_has_permission_level_or_higher(user, SECRETARIA_EBD)


def get_ebd_scope_churches(request):
    from configuracao.models import Igreja

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
                return Igreja.objects.filter(pk=igreja_ativa.pk)
            return Igreja.objects.all() if request.user.is_superuser else Igreja.objects.none()

    igreja_ativa = getattr(request, 'igreja_ativa', None)
    if igreja_ativa and igrejas_permitidas.filter(pk=igreja_ativa.pk).exists():
        return igrejas_permitidas.filter(pk=igreja_ativa.pk)

    igreja_ativa_id = request.session.get('igreja_ativa_id')
    if igreja_ativa_id and igrejas_permitidas.filter(pk=igreja_ativa_id).exists():
        return igrejas_permitidas.filter(pk=igreja_ativa_id)

    return get_request_scoped_churches(request, igrejas_permitidas)


def get_ebd_ministerio_config(request):
    from configuracao.models import ConfiguracaoSistema

    perfil = getattr(request.user, 'perfil', None) or getattr(request.user, 'perfil_usuario', None)
    ministerio = getattr(perfil, 'ministerio', None)
    if not ministerio:
        return None
    return ConfiguracaoSistema.objects.filter(ministerio=ministerio).first()


def _igreja_tem_override_ebd(igreja):
    if igreja is None:
        return False
    return bool(
        igreja.ebd_periodo
        or igreja.ebd_dia_semana is not None
        or igreja.ebd_horario is not None
    )


def get_ebd_igreja_config(request):
    igreja_ativa = getattr(request, 'igreja_ativa', None)
    if igreja_ativa:
        return igreja_ativa

    igrejas_escopo = get_ebd_scope_churches(request)
    if igrejas_escopo.count() == 1:
        return igrejas_escopo.first()
    return None


def get_ebd_config(request):
    igreja = get_ebd_igreja_config(request)
    if _igreja_tem_override_ebd(igreja):
        return igreja
    return get_ebd_ministerio_config(request)


def get_ebd_config_source_info(request):
    igreja = get_ebd_igreja_config(request)
    if _igreja_tem_override_ebd(igreja):
        return {
            'ebd_config_source': 'igreja',
            'ebd_config_source_label': f'Origem: configuração local ({igreja.nome_igreja})',
            'ebd_config_source_hint': 'Período, dia e horário definidos na igreja em escopo.',
        }

    return {
        'ebd_config_source': 'ministerio',
        'ebd_config_source_label': 'Origem: configuração herdada do ministério',
        'ebd_config_source_hint': 'Sem override local nesta igreja. A EBD segue os parâmetros ministeriais.',
    }


def get_ebd_tipo_periodo(request):
    config = get_ebd_config(request)
    if config and config.ebd_periodo:
        return config.ebd_periodo
    return 'trimestre'


def get_ebd_dia_semana(request):
    config = get_ebd_config(request)
    if config and config.ebd_dia_semana is not None:
        return config.ebd_dia_semana
    return 6


EBD_PONTOS_DEFAULT = {
    'presente': 10,
    'biblia': 2,
    'revista': 2,
    'oferta': 3,
    'visitante': 5,
}


def get_ebd_pontos_config(request):
    config = get_ebd_config(request)
    return {
        'presente': getattr(config, 'ebd_pontos_presente', None) if config else None,
        'biblia': getattr(config, 'ebd_pontos_biblia', None) if config else None,
        'revista': getattr(config, 'ebd_pontos_revista', None) if config else None,
        'oferta': getattr(config, 'ebd_pontos_oferta', None) if config else None,
        'visitante': getattr(config, 'ebd_pontos_visitante', None) if config else None,
    }


def get_ebd_pontos_config_com_fallback(request):
    cfg = get_ebd_pontos_config(request)
    return {
        'presente': EBD_PONTOS_DEFAULT['presente'] if cfg['presente'] is None else int(cfg['presente']),
        'biblia': EBD_PONTOS_DEFAULT['biblia'] if cfg['biblia'] is None else int(cfg['biblia']),
        'revista': EBD_PONTOS_DEFAULT['revista'] if cfg['revista'] is None else int(cfg['revista']),
        'oferta': EBD_PONTOS_DEFAULT['oferta'] if cfg['oferta'] is None else int(cfg['oferta']),
        'visitante': EBD_PONTOS_DEFAULT['visitante'] if cfg['visitante'] is None else int(cfg['visitante']),
    }


def calcular_pontos_frequencia_flags(*, presente=False, trouxe_biblia=False, trouxe_revista=False, trouxe_oferta=False, trouxe_visitante=False, pontos_cfg=None):
    cfg = pontos_cfg or EBD_PONTOS_DEFAULT
    total = 0
    if presente:
        total += cfg['presente']
    if trouxe_biblia:
        total += cfg['biblia']
    if trouxe_revista:
        total += cfg['revista']
    if trouxe_oferta:
        total += cfg['oferta']
    if trouxe_visitante:
        total += cfg['visitante']
    return total


def _get_expr_pontos_frequencia(pontos_cfg):
    return (
        Case(
            When(presente=True, then=Value(pontos_cfg['presente'])),
            default=Value(0),
            output_field=IntegerField(),
        )
        + Case(
            When(trouxe_biblia=True, then=Value(pontos_cfg['biblia'])),
            default=Value(0),
            output_field=IntegerField(),
        )
        + Case(
            When(trouxe_revista=True, then=Value(pontos_cfg['revista'])),
            default=Value(0),
            output_field=IntegerField(),
        )
        + Case(
            When(trouxe_oferta=True, then=Value(pontos_cfg['oferta'])),
            default=Value(0),
            output_field=IntegerField(),
        )
        + Case(
            When(trouxe_visitante=True, then=Value(pontos_cfg['visitante'])),
            default=Value(0),
            output_field=IntegerField(),
        )
    )


def _get_ebd_auto_sync_session_key(request, tipo_periodo, dia_semana):
    perfil = getattr(request.user, 'perfil', None) or getattr(request.user, 'perfil_usuario', None)
    ministerio = getattr(perfil, 'ministerio', None)
    ministerio_id = getattr(ministerio, 'id', 'global')
    igreja_ativa = get_ebd_igreja_config(request)
    igreja_id = getattr(igreja_ativa, 'id', 'all')
    return f'ebd:auto-sync:{ministerio_id}:{igreja_id}:{tipo_periodo}:{dia_semana}'


def get_ebd_periodo_filtro(request):
    from .models import AnoLetivo, PeriodoEBD

    hoje = timezone.now().date()
    tipo_periodo = get_ebd_tipo_periodo(request)
    ano_letivo_filtro = request.GET.get('ano_letivo')
    periodo_filtro = request.GET.get('periodo')

    anos_letivos = AnoLetivo.objects.order_by('-ano')
    if ano_letivo_filtro:
        try:
            ano_letivo_selecionado = anos_letivos.get(ano=int(str(ano_letivo_filtro).strip()))
        except (AnoLetivo.DoesNotExist, ValueError):
            ano_letivo_selecionado = anos_letivos.filter(ano=hoje.year).first() or anos_letivos.first()
    else:
        ano_letivo_selecionado = anos_letivos.filter(ano=hoje.year).first() or anos_letivos.first()

    periodos_disponiveis = PeriodoEBD.objects.none()
    if ano_letivo_selecionado:
        periodos_disponiveis = PeriodoEBD.objects.filter(
            ano_letivo=ano_letivo_selecionado,
            tipo=tipo_periodo,
        ).order_by('numero')

    periodo_selecionado = None
    if periodos_disponiveis.exists():
        if periodo_filtro:
            try:
                periodo_selecionado = periodos_disponiveis.get(numero=int(periodo_filtro))
            except (PeriodoEBD.DoesNotExist, ValueError):
                periodo_selecionado = periodos_disponiveis.filter(data_inicio__lte=hoje, data_fim__gte=hoje).first() or periodos_disponiveis.first()
        else:
            periodo_selecionado = periodos_disponiveis.filter(data_inicio__lte=hoje, data_fim__gte=hoje).first() or periodos_disponiveis.first()

    return {
        'tipo_periodo': tipo_periodo,
        'anos_letivos': anos_letivos,
        'ano_letivo_selecionado': ano_letivo_selecionado,
        'periodos_disponiveis': periodos_disponiveis,
        'periodo_selecionado': periodo_selecionado,
    }


def auto_sync_ebd_periodos_e_licoes(request, force=False):
    """
    Garante de forma automática:
    1) períodos do ano atual e próximo ano (conforme configuração ministerial);
    2) lições do período vigente (ou próximo) para turmas do escopo.
    """
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return

    try:
        from .models import AnoLetivo, Licao, PeriodoEBD, Turma
        from .utils import gerar_datas_semana_periodo, gerar_periodos_ebd

        hoje = timezone.now().date()
        tipo_periodo = get_ebd_tipo_periodo(request)
        dia_semana = get_ebd_dia_semana(request)
        session_key = _get_ebd_auto_sync_session_key(request, tipo_periodo, dia_semana)

        if not force and request.session.get(session_key) == hoje.isoformat():
            return

        anos = [hoje.year, hoje.year + 1]
        anos_letivos = []

        for ano in anos:
            ano_letivo, _ = AnoLetivo.objects.get_or_create(ano=ano, defaults={'ativo': ano == hoje.year})
            anos_letivos.append(ano_letivo)

            for periodo in gerar_periodos_ebd(ano, tipo_periodo):
                PeriodoEBD.objects.get_or_create(
                    ano_letivo=ano_letivo,
                    tipo=tipo_periodo,
                    numero=periodo['numero'],
                    defaults={
                        'data_inicio': periodo['data_inicio'],
                        'data_fim': periodo['data_fim'],
                    },
                )

        periodo_referencia = PeriodoEBD.objects.filter(
            ano_letivo__in=anos_letivos,
            tipo=tipo_periodo,
            data_inicio__lte=hoje,
            data_fim__gte=hoje,
        ).order_by('ano_letivo__ano', 'numero').first()

        if periodo_referencia is None:
            periodo_referencia = PeriodoEBD.objects.filter(
                ano_letivo__in=anos_letivos,
                tipo=tipo_periodo,
                data_inicio__gte=hoje,
            ).order_by('data_inicio').first()

        if periodo_referencia is not None:
            datas_aula = gerar_datas_semana_periodo(
                periodo_referencia.data_inicio,
                periodo_referencia.data_fim,
                dia_semana=dia_semana,
            )

            turmas = filtrar_turmas_ebd(
                Turma.objects.filter(ano_letivo=periodo_referencia.ano_letivo),
                request,
            ).order_by('id')

            total_criadas = 0
            periodo_nome = f"{periodo_referencia.get_tipo_display()} {periodo_referencia.numero}/{periodo_referencia.ano_letivo.ano}"
            for turma in turmas:
                for idx, data_aula in enumerate(datas_aula, start=1):
                    _, criada = Licao.objects.get_or_create(
                        turma=turma,
                        data=data_aula,
                        defaults={
                            'tema': f'Lição {idx} - {periodo_nome}',
                            'status': 'ativa',
                               'periodo': periodo_referencia,
                        },
                    )
                    if criada:
                        total_criadas += 1

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
    igrejas = get_ebd_scope_churches(request)
    return queryset.filter(
        Q(igreja__in=igrejas) | Q(igreja__isnull=True, membros__igreja__in=igrejas)
    ).distinct()


def filtrar_classes_ebd(queryset, request):
    igrejas = get_ebd_scope_churches(request)
    return queryset.filter(
        Q(igreja__in=igrejas) | Q(igreja__isnull=True, turma__membros__igreja__in=igrejas)
    ).distinct()


def filtrar_alunos_ebd(queryset, request):
    igrejas = get_ebd_scope_churches(request)
    return queryset.filter(
        Q(turma__igreja__in=igrejas) |
        Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas)
    ).distinct()


def filtrar_frequencias_ebd(queryset, request):
    return queryset.filter(aluno__in=filtrar_alunos_ebd(Aluno.objects.all(), request)).distinct()


def filtrar_avaliacoes_ebd(queryset, request):
    return queryset.filter(aluno__in=filtrar_alunos_ebd(Aluno.objects.all(), request)).distinct()


def colapsar_alunos_por_cadastro(queryset):
    ultimo_aluno_por_cadastro = queryset.filter(cadastro_id=OuterRef('cadastro_id')).order_by(
        '-ativo', '-turma__ano_letivo__ano', '-updated_at', '-id'
    ).values('id')[:1]
    return queryset.filter(id=Subquery(ultimo_aluno_por_cadastro))


def consolidar_alunos_por_cadastro_periodo(queryset, inicio=None, fim=None, turma_id=None, classe_id=None, periodo=None):
    if periodo is not None:
        inicio = periodo.data_inicio
        fim = periodo.data_fim

    data_referencia = fim or inicio or timezone.now().date()
    matriculas = list(queryset.select_related('cadastro', 'turma', 'turma__classe', 'turma__ano_letivo'))
    if not matriculas:
        return []

    matriculas_por_cadastro = defaultdict(list)
    for matricula in matriculas:
        matriculas_por_cadastro[matricula.cadastro_id].append(matricula)

    alunos_referencia = []
    for cadastro_id, matriculas_cadastro in matriculas_por_cadastro.items():
        cadastro = matriculas_cadastro[0].cadastro
        matricula_referencia = cadastro.get_matricula_referencia(data_referencia=data_referencia, matriculas=matriculas_cadastro)
        if matricula_referencia is None:
            continue
        if turma_id and str(matricula_referencia.turma_id) != str(turma_id):
            continue
        if classe_id and str(matricula_referencia.turma.classe_id) != str(classe_id):
            continue
        alunos_referencia.append(matricula_referencia)

    if not alunos_referencia:
        return []

    cadastro_ids = [aluno.cadastro_id for aluno in alunos_referencia]

    frequencias = Frequencia.objects.filter(aluno__cadastro_id__in=cadastro_ids)
    if inicio:
        frequencias = frequencias.filter(data__gte=inicio)
    if fim:
        frequencias = frequencias.filter(data__lte=fim)
    frequencias_por_cadastro = {
        item['aluno__cadastro_id']: item
        for item in frequencias.values('aluno__cadastro_id').annotate(
            total_freq=Count('id'),
            presencas=Count('id', filter=Q(presente=True)),
        )
    }

    avaliacoes = Avaliacao.objects.filter(aluno__cadastro_id__in=cadastro_ids)
    if periodo is not None:
        avaliacoes = avaliacoes.filter(licao__periodo=periodo)
    else:
        if inicio:
            avaliacoes = avaliacoes.filter(licao__data__gte=inicio)
        if fim:
            avaliacoes = avaliacoes.filter(licao__data__lte=fim)
    avaliacoes_por_cadastro = {
        item['aluno__cadastro_id']: item
        for item in avaliacoes.values('aluno__cadastro_id').annotate(
            media_nota=Avg('nota'),
            participacao=Count('id', filter=Q(participacao=True)),
        )
    }

    for aluno in alunos_referencia:
        aluno.nome_exibicao = aluno.cadastro.nome
        freq_info = frequencias_por_cadastro.get(aluno.cadastro_id, {})
        total_freq = freq_info.get('total_freq', 0)
        presencas = freq_info.get('presencas', 0)
        aluno.total_freq = total_freq
        aluno.presencas = presencas
        aluno.freq_percent = round((presencas / total_freq) * 100, 1) if total_freq else None

        aval_info = avaliacoes_por_cadastro.get(aluno.cadastro_id, {})
        media_nota = aval_info.get('media_nota')
        aluno.media_nota = round(media_nota, 2) if media_nota is not None else None
        aluno.participacao = aval_info.get('participacao', 0)

    return sorted(alunos_referencia, key=lambda item: (item.nome_exibicao.lower(), item.turma.nome.lower()))


def get_object_or_404_ebd(queryset, request, igreja_lookup, **lookup):
    return get_object_or_404(filtrar_queryset_ebd(queryset, request, igreja_lookup), **lookup)


def oferta_queryset_por_turma_data(turma, data):
    return OfertaClasse.objects.filter(
        Q(turma=turma) | Q(turma__isnull=True, classe=turma.classe),
        data=data,
    )

@page_access_required('escola_biblica')
@log_ebd_endpoint('relatorio_ebd_dia')
def relatorio_ebd_dia(request):
    from .models import Turma, Frequencia, OfertaClasse, AnoLetivo, Licao
    from decimal import Decimal
    
    # Se data n├úo for fornecida, busca a data da li├º├úo mais recente
    data_str = request.GET.get('data')
    if data_str:
        data = parse_date(data_str)
    else:
        # Busca a data da li├º├úo mais recente
        ultima_licao = filtrar_queryset_ebd(Licao.objects.all(), request, 'turma__membros__igreja').order_by('-data').first()
        data = ultima_licao.data if ultima_licao else timezone.now().date()
    
    # Filtra turmas apenas do ano letivo correspondente ├á data selecionada
    # E que tenham li├º├Áes cadastradas na data selecionada
    ano_da_data = data.year
    ano_letivo = AnoLetivo.objects.filter(ano=ano_da_data).first()
    if ano_letivo:
        turmas_com_licao = filtrar_queryset_ebd(Licao.objects.filter(data=data), request, 'turma__membros__igreja').values_list('turma_id', flat=True)
        turmas = filtrar_queryset_ebd(Turma.objects.filter(ano_letivo=ano_letivo, id__in=turmas_com_licao), request, 'membros__igreja')
    else:
        turmas = Turma.objects.none()
    
    # Busca todas as datas com li├º├Áes do ano letivo para o campo de sele├º├úo
    datas_com_licoes = []
    if ano_letivo:
        datas_com_licoes = filtrar_queryset_ebd(Licao.objects.filter(turma__ano_letivo=ano_letivo), request, 'turma__membros__igreja').values_list('data', flat=True).distinct().order_by('-data')
    
    relatorio_turmas = []
    total_geral = {
        'matriculados': 0, 'presentes': 0, 'ausentes': 0, 'visitantes': 0,
        'biblias': 0, 'revistas': 0, 'oferta': Decimal('0.0')
    }
    for turma in turmas:
        alunos = turma.alunos.filter(ativo=True)
        matriculados = alunos.count()
        freq = Frequencia.objects.filter(aluno__in=alunos, data=data)
        presentes = freq.filter(presente=True).count()
        ausentes = matriculados - presentes
        visitantes = freq.filter(trouxe_visitante=True).count()
        biblias = freq.filter(trouxe_biblia=True).count()
        revistas = freq.filter(trouxe_revista=True).count()
        oferta = oferta_queryset_por_turma_data(turma, data).aggregate(s=Sum('valor'))['s'] or Decimal('0.0')
        relatorio_turmas.append({
            'nome': turma.nome,
            'matriculados': matriculados,
            'presentes': presentes,
            'ausentes': ausentes,
            'visitantes': visitantes,
            'biblias': biblias,
            'revistas': revistas,
            'oferta': oferta,
        })
        total_geral['matriculados'] += matriculados
        total_geral['presentes'] += presentes
        total_geral['ausentes'] += ausentes
        total_geral['visitantes'] += visitantes
        total_geral['biblias'] += biblias
        total_geral['revistas'] += revistas
        total_geral['oferta'] += oferta
    
    # Busca dados da aula anterior
    data_anterior = None
    total_anterior = None
    if datas_com_licoes:
        datas_lista = list(datas_com_licoes)
        try:
            indice_atual = datas_lista.index(data)
            if indice_atual + 1 < len(datas_lista):
                data_anterior = datas_lista[indice_atual + 1]
        except ValueError:
            pass
    
    if data_anterior and ano_letivo:
        turmas_anterior = filtrar_queryset_ebd(Licao.objects.filter(data=data_anterior), request, 'turma__membros__igreja').values_list('turma_id', flat=True)
        turmas_ant = filtrar_queryset_ebd(Turma.objects.filter(ano_letivo=ano_letivo, id__in=turmas_anterior), request, 'membros__igreja')
        total_anterior = {
            'matriculados': 0, 'presentes': 0, 'ausentes': 0, 'visitantes': 0,
            'biblias': 0, 'revistas': 0, 'oferta': Decimal('0.0')
        }
        for turma in turmas_ant:
            alunos = turma.alunos.filter(ativo=True)
            matriculados = alunos.count()
            freq = Frequencia.objects.filter(aluno__in=alunos, data=data_anterior)
            presentes = freq.filter(presente=True).count()
            ausentes = matriculados - presentes
            visitantes = freq.filter(trouxe_visitante=True).count()
            biblias = freq.filter(trouxe_biblia=True).count()
            revistas = freq.filter(trouxe_revista=True).count()
            oferta = oferta_queryset_por_turma_data(turma, data_anterior).aggregate(s=Sum('valor'))['s'] or Decimal('0.0')
            total_anterior['matriculados'] += matriculados
            total_anterior['presentes'] += presentes
            total_anterior['ausentes'] += ausentes
            total_anterior['visitantes'] += visitantes
            total_anterior['biblias'] += biblias
            total_anterior['revistas'] += revistas
            total_anterior['oferta'] += oferta
    
    return render(request, 'escola_biblica/relatorio_ebd_dia.html', {
        'relatorio_turmas': relatorio_turmas,
        'total_geral': total_geral,
        'total_anterior': total_anterior,
        'data': data,
        'data_anterior': data_anterior,
        'datas_com_licoes': datas_com_licoes,
    })
# --- CHAMADA DE PRESEN├çA POR TURMA ---
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from .forms import ChamadaPresencaFormSet
from .models import Turma, Aluno, Licao, PeriodoEBD, Frequencia, OfertaClasse


@login_required
@page_access_required('escola_biblica_professor')
@log_ebd_endpoint('chamada_presenca')
def chamada_presenca(request, turma_id):

    """
    Chamada de presen├ºa da turma.
    
    Pode ser acessada por:
    - Secretaria EBD / Superintendente EBD (todas as turmas)
    - Professor da turma (apenas sua turma)
    """
    auto_sync_ebd_periodos_e_licoes(request)
    turma = get_object_or_404(filtrar_turmas_ebd(Turma.objects.all(), request), pk=turma_id)

    if not pode_acessar_chamada_turma(request.user, turma):
        raise PermissionDenied("Você não tem permissão para acessar a chamada desta turma.")

    alunos = turma.alunos.filter(ativo=True).order_by('nome')
    ano_letivo = turma.ano_letivo
    tipo_periodo = get_ebd_tipo_periodo(request)
    dia_ebd = get_ebd_dia_semana(request)
    hoje = timezone.localdate()

    periodos_qs = PeriodoEBD.objects.filter(ano_letivo=ano_letivo, tipo=tipo_periodo).order_by('data_inicio')
    periodo = periodos_qs.filter(data_inicio__lte=hoje, data_fim__gte=hoje).first()
    if periodo is None:
        periodo = periodos_qs.filter(data_inicio__gte=hoje).first() or periodos_qs.last()

    datas_esperadas = []
    licoes_qs = Licao.objects.none()
    if periodo is not None:
        from .utils import gerar_datas_semana_periodo

        datas_esperadas = gerar_datas_semana_periodo(periodo.data_inicio, periodo.data_fim, dia_semana=dia_ebd)
        licoes_qs = Licao.objects.filter(
            turma=turma,
            data__gte=periodo.data_inicio,
            data__lte=periodo.data_fim,
        ).select_related('professor').order_by('data', 'id')

    datas_com_licao = []
    licao_por_data = {}
    for licao in licoes_qs:
        if licao.data not in licao_por_data:
            licao_por_data[licao.data] = licao
            datas_com_licao.append(licao.data)

    licoes_faltantes = [d for d in datas_esperadas if d not in licao_por_data]
    if licoes_faltantes and request.method != 'POST':
        msg = f"Atenção: Existem {len(licoes_faltantes)} datas do período sem lição cadastrada para esta turma. "
        url_cronograma = redirect('escola_biblica:gerar_cronograma_wizard').url
        msg += f"<a href='{url_cronograma}?turma_id={turma.id}' class='btn btn-sm btn-warning ms-2'>Criar lições em lote</a>"
        messages.warning(request, msg)

    data_raw = request.POST.get('data') or request.GET.get('data')
    data_selecionada = parse_date(data_raw) if data_raw else None
    datas_validas_set = set(datas_com_licao)
    if data_selecionada not in datas_validas_set:
        if hoje in datas_validas_set:
            data_selecionada = hoje
        else:
            datas_passadas = [d for d in datas_com_licao if d <= hoje]
            data_selecionada = (max(datas_passadas) if datas_passadas else (datas_com_licao[0] if datas_com_licao else None))

    licao_do_dia = licao_por_data.get(data_selecionada) if data_selecionada else None
    data = data_selecionada.isoformat() if data_selecionada else ''

    opcoes_aula = []
    for idx, d in enumerate(datas_com_licao, start=1):
        licao = licao_por_data.get(d)
        status_data = 'hoje' if d == hoje else ('passada' if d < hoje else 'futura')
        opcoes_aula.append({
            'value': d.isoformat(),
            'label': f"{idx}ª aula - {d.strftime('%d/%m/%Y')}",
            'tema': getattr(licao, 'tema', ''),
            'status': status_data,
        })

    status_aula_selecionada = None
    if data_selecionada:
        if data_selecionada == hoje:
            status_aula_selecionada = 'hoje'
        elif data_selecionada < hoje:
            status_aula_selecionada = 'passada'
        else:
            status_aula_selecionada = 'futura'

    ebd_pontos_config = get_ebd_pontos_config_com_fallback(request)

    valor_oferta_atual = ''
    classe = turma.classe if hasattr(turma, 'classe') else None
    if classe and data_selecionada:
        oferta_obj = oferta_queryset_por_turma_data(turma, data_selecionada).first()
        if oferta_obj and oferta_obj.valor is not None:
            valor_oferta_atual = f"{oferta_obj.valor:.2f}"

    bloqueio_chamada_msg = None
    if not data_selecionada:
        bloqueio_chamada_msg = 'Não há lição cadastrada no período atual para esta turma. Cadastre as lições antes de registrar a chamada.'

    formset = None
    if alunos.exists() and not bloqueio_chamada_msg:
        if request.method == 'POST' and not request.POST.get('troca_data'):
            if not licao_do_dia:
                messages.error(request, 'Não é possível registrar a chamada: não existe lição cadastrada para a data selecionada.')
                return redirect(request.path + (f'?data={data}' if data else ''))

            chamada_idempotency_key = _build_chamada_idempotency_key(request, turma.id, data_selecionada)
            if cache.get(chamada_idempotency_key):
                log_ebd_audit_event(
                    request,
                    'chamada_duplicada_ignorada',
                    turma_id=turma.id,
                    data=data_selecionada,
                )
                messages.info(request, 'Esta chamada já foi processada recentemente. Nenhuma alteração duplicada foi aplicada.')
                return redirect('escola_biblica:turma_list')

            formset = ChamadaPresencaFormSet(request.POST)
            if formset.is_valid():
                erro_validacao = False
                pontos_totais_aula = 0
                for form in formset:
                    aluno_id = form.cleaned_data['aluno_id']
                    presente = form.cleaned_data.get('presente', False)
                    trouxe_biblia = form.cleaned_data.get('trouxe_biblia', False)
                    trouxe_revista = form.cleaned_data.get('trouxe_revista', False)
                    trouxe_visitante = form.cleaned_data.get('trouxe_visitante', False)
                    trouxe_oferta = form.cleaned_data.get('trouxe_oferta', False)
                    freq, _ = Frequencia.objects.get_or_create(
                        aluno_id=aluno_id,
                        data=data_selecionada,
                        defaults={
                            'presente': presente,
                            'trouxe_biblia': trouxe_biblia,
                            'trouxe_revista': trouxe_revista,
                            'trouxe_visitante': trouxe_visitante,
                            'trouxe_oferta': trouxe_oferta,
                        }
                    )
                    freq.presente = presente
                    freq.trouxe_biblia = trouxe_biblia
                    freq.trouxe_revista = trouxe_revista
                    freq.trouxe_visitante = trouxe_visitante
                    freq.trouxe_oferta = trouxe_oferta
                    freq.pontos_total = calcular_pontos_frequencia_flags(
                        presente=presente,
                        trouxe_biblia=trouxe_biblia,
                        trouxe_revista=trouxe_revista,
                        trouxe_oferta=trouxe_oferta,
                        trouxe_visitante=trouxe_visitante,
                        pontos_cfg=ebd_pontos_config,
                    )
                    pontos_totais_aula += freq.pontos_total
                    try:
                        freq.save()
                    except Exception as exc:
                        erro_validacao = True
                        logger.warning(
                            'ebd.chamada.save_error turma_id=%s aluno_id=%s data=%s user_id=%s erro=%s',
                            turma.id,
                            aluno_id,
                            data_selecionada,
                            request.user.pk,
                            exc,
                        )
                        messages.error(request, f'Erro ao registrar chamada para {freq.aluno.nome}: {exc}')

                valor_oferta = request.POST.get('valor_oferta')
                if valor_oferta is not None and classe and data_selecionada:
                    try:
                        valor_str = str(valor_oferta).replace(',', '.').strip()
                        valor_float = float(valor_str) if valor_str else 0.0
                        oferta_obj, created = OfertaClasse.objects.get_or_create(
                            turma=turma,
                            data=data_selecionada,
                            defaults={'classe': classe, 'valor': valor_float}
                        )
                        if not created:
                            oferta_obj.valor = valor_float
                            oferta_obj.save()
                        log_ebd_audit_event(
                            request,
                            'chamada_oferta_registrada',
                            turma_id=turma.id,
                            data=data_selecionada,
                            valor=valor_float,
                        )
                    except Exception as exc:
                        logger.warning(
                            'ebd.chamada.oferta_error turma_id=%s data=%s user_id=%s erro=%s',
                            turma.id,
                            data_selecionada,
                            request.user.pk,
                            exc,
                        )
                        messages.error(request, f'Erro ao registrar valor da oferta: {exc}')

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
        else:
            freq_registros = {
                item.aluno_id: item
                for item in Frequencia.objects.filter(aluno__in=alunos, data=data_selecionada)
            }
            initial = [
                {
                    'aluno_id': aluno.id,
                    'nome': aluno.nome,
                    'presente': bool(freq_registros.get(aluno.id) and freq_registros[aluno.id].presente),
                    'trouxe_biblia': bool(freq_registros.get(aluno.id) and freq_registros[aluno.id].trouxe_biblia),
                    'trouxe_revista': bool(freq_registros.get(aluno.id) and freq_registros[aluno.id].trouxe_revista),
                    'trouxe_visitante': bool(freq_registros.get(aluno.id) and freq_registros[aluno.id].trouxe_visitante),
                    'trouxe_oferta': bool(freq_registros.get(aluno.id) and freq_registros[aluno.id].trouxe_oferta),
                }
                for aluno in alunos
            ]
            formset = ChamadaPresencaFormSet(initial=initial)

    periodo_label = ''
    if periodo is not None:
        periodo_label = f"{periodo.get_tipo_display()} {periodo.numero} ({periodo.data_inicio.strftime('%d/%m/%Y')} - {periodo.data_fim.strftime('%d/%m/%Y')})"

    return render(request, 'escola_biblica/chamada_presenca.html', {
        'turma': turma,
        'formset': formset,
        'data': data,
        'datas_validas': datas_com_licao,
        'opcoes_aula': opcoes_aula,
        'periodo': periodo,
        'periodo_label': periodo_label,
        'valor_oferta_atual': valor_oferta_atual,
        'licao_do_dia': licao_do_dia,
        'bloqueio_chamada_msg': bloqueio_chamada_msg,
        'status_aula_selecionada': status_aula_selecionada,
        'ebd_pontos_config': ebd_pontos_config,
    })
# --- IMPORTS NECESS├üRIOS PARA DECORADORES ---
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from core.decorators import secretaria_ebd_required
# --- WIZARD: Gera├º├úo de li├º├Áes em etapas ---
@page_access_required('escola_biblica')
@csrf_exempt
def gerar_cronograma_wizard(request):
    from .models import AnoLetivo, PeriodoEBD, Turma, Licao
    from datetime import date
    from django.utils import timezone
    auto_sync_ebd_periodos_e_licoes(request)
    etapa = int(request.POST.get('etapa', request.GET.get('etapa', 1)))
    hoje = timezone.now().date()
    ano_atual = hoje.year
    # Ano letivo: apenas atual e pr├│ximo (se existir)
    anos_letivos = AnoLetivo.objects.filter(ano__gte=ano_atual).order_by('ano')
    # Turmas: ├║nicas, ordem alfab├®tica
    turmas = filtrar_queryset_ebd(Turma.objects.filter(ano_letivo__ano__gte=ano_atual).order_by('nome').distinct(), request, 'membros__igreja')
    # Per├¡odos: s├│ do ano letivo selecionado, abertos/futuros
    periodo_ano_raw = request.POST.get('ano_letivo', ano_atual)
    periodo_ano = int(str(periodo_ano_raw).replace('.', '').replace(' ', ''))
    periodos = PeriodoEBD.objects.filter(ano_letivo__ano=periodo_ano, data_fim__gte=hoje).order_by('numero')
    context = {'etapa': etapa}
    context['modo_contingencia'] = True

    # Etapa 1: Sele├º├úo
    if etapa == 1:
        context.update({
            'anos_letivos': anos_letivos,
            'periodos': periodos,
            'turmas': turmas,
        })
        if request.method == 'POST' and request.POST.get('wizard_next'):
            ano_letivo_raw = request.POST.get('ano_letivo')
            ano_letivo = int(str(ano_letivo_raw).replace('.', '').replace(' ', ''))
            periodo = int(request.POST.get('periodo'))
            turmas_ids = request.POST.getlist('turmas')
            # Buscar horário padrão da configuração EBD (igreja local com fallback ministerial)
            horario_inicial = ''
            config = get_ebd_config(request)
            if config and config.ebd_horario:
                if isinstance(config.ebd_horario, str):
                    horario_inicial = config.ebd_horario[:5]
                else:
                    horario_inicial = config.ebd_horario.strftime('%H:%M')
            # Inicializa periodo_nome corretamente
            periodo_obj = PeriodoEBD.objects.filter(ano_letivo__ano=ano_letivo, numero=periodo).first()
            periodo_nome = f"{periodo_obj.get_tipo_display()} {periodo_obj.numero}" if periodo_obj else "Per├¡odo"
            periodos_prox = PeriodoEBD.objects.filter(ano_letivo__ano=ano_letivo, data_fim__gte=hoje).order_by('numero')
            turmas_prox = filtrar_queryset_ebd(Turma.objects.filter(ano_letivo__ano=ano_letivo).order_by('nome').distinct(), request, 'membros__igreja')
            context.update({
                'ano_letivo': ano_letivo,
                'periodo': periodo,
                'turmas': turmas_ids,
                'periodos': periodos_prox,
                'turmas_lista': turmas_prox,
                'etapa': 2,
                'horario': horario_inicial,
                'material': request.POST.get('material', ''),
                'status': request.POST.get('status', 'ativa'),
                'observacoes': request.POST.get('observacoes', ''),
                'nome_licao_padrao': request.POST.get('nome_licao_padrao', f'Li├º├úo {{n}} - {periodo_nome}'),
            })
            return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
        return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)

    # Etapa 2: Configura├º├úo
    if etapa == 2:
        ano_letivo_raw = request.POST.get('ano_letivo')
        ano_letivo = int(str(ano_letivo_raw).replace('.', '').replace(' ', ''))
        periodo = int(request.POST.get('periodo'))
        turmas_ids = request.POST.getlist('turmas')
        # Buscar horário padrão da configuração EBD (igreja local com fallback ministerial)
        horario_inicial = ''
        config = get_ebd_config(request)
        if config and config.ebd_horario:
            # Garante que o valor esteja no formato HH:MM
            if isinstance(config.ebd_horario, str):
                horario_inicial = config.ebd_horario[:5]
            else:
                horario_inicial = config.ebd_horario.strftime('%H:%M')
        # Padr├úo de nome sugerido
        periodo_obj = PeriodoEBD.objects.filter(ano_letivo__ano=ano_letivo, numero=periodo).first()
        periodo_nome = f"{periodo_obj.get_tipo_display()} {periodo_obj.numero}" if periodo_obj else "Per├¡odo"
        nome_licao_padrao = request.POST.get('nome_licao_padrao', f'Li├º├úo {{n}} - {periodo_nome}')
        # Se j├í veio do POST, prioriza o valor enviado, sen├úo usa o padr├úo do sistema
        if 'horario' in request.POST:
            horario = request.POST.get('horario', '')
            if not horario:
                horario = horario_inicial
        else:
            horario = horario_inicial
        material = request.POST.get('material', '')
        status = request.POST.get('status', 'ativa')
        observacoes = request.POST.get('observacoes', '')
        context.update({
            'ano_letivo': ano_letivo,
            'periodo': periodo,
            'turmas': turmas_ids,
            'material': material,
            'horario': horario,
            'status': status,
            'observacoes': observacoes,
            'nome_licao_padrao': nome_licao_padrao,
        })
        if request.POST.get('wizard_next'):
            erro_wizard = None
            if not turmas_ids or not periodo_obj:
                erro_wizard = 'Selecione ao menos uma turma e um per├¡odo v├ílido para continuar.'
                context['erro_wizard'] = erro_wizard
                return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
            context['etapa'] = 3
            # Pr├®-visualiza├º├úo das li├º├Áes
            turmas_objs = filtrar_queryset_ebd(Turma.objects.filter(id__in=turmas_ids), request, 'membros__igreja')
            licoes_preview = []
            if periodo_obj:
                from .utils import gerar_domingos_periodo
                domingos = gerar_domingos_periodo(periodo_obj.data_inicio, periodo_obj.data_fim)
                for turma in turmas_objs:
                    for idx, domingo in enumerate(domingos, start=1):
                        tema = nome_licao_padrao.replace('{n}', str(idx)).replace('{periodo}', periodo_nome)
                        licoes_preview.append({
                            'turma_nome': turma.nome,
                            'data': domingo,
                            'tema': tema,
                            'professor': turma.get_professor_nome(),
                            'status': status,
                        })
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
        ano_letivo_raw = request.POST.get('ano_letivo')
        ano_letivo = int(str(ano_letivo_raw).replace('.', '').replace(' ', ''))
        periodo = int(request.POST.get('periodo'))
        turmas_ids = request.POST.getlist('turmas')
        material = request.POST.get('material', '')
        horario = request.POST.get('horario', '')
        status = request.POST.get('status', 'ativa')
        observacoes = request.POST.get('observacoes', '')
        nome_licao_padrao = request.POST.get('nome_licao_padrao', '')
        periodo_obj = PeriodoEBD.objects.filter(ano_letivo__ano=ano_letivo, numero=periodo).first()
        periodo_nome = f"{periodo_obj.get_tipo_display()} {periodo_obj.numero}" if periodo_obj else "Per├¡odo"
        turmas_objs = filtrar_queryset_ebd(Turma.objects.filter(id__in=turmas_ids), request, 'membros__igreja')
        licoes_geradas = 0
        if request.POST.get('wizard_confirm'):
            from .utils import gerar_domingos_periodo
            domingos = gerar_domingos_periodo(periodo_obj.data_inicio, periodo_obj.data_fim) if periodo_obj else []
            for turma in turmas_objs:
                for idx, domingo in enumerate(domingos, start=1):
                    tema = nome_licao_padrao.replace('{n}', str(idx)).replace('{periodo}', periodo_nome)
                    if not Licao.objects.filter(turma=turma, data=domingo, tema=tema).exists():
                        Licao.objects.create(
                            turma=turma,
                            data=domingo,
                            tema=tema,
                            material=material,
                            observacoes=observacoes,
                            horario=horario,
                            status=status,
                            professor=turma.get_professor_nome(),
                        )
                        licoes_geradas += 1
            resultado_msg = f'{licoes_geradas} li├º├Áes geradas com sucesso!' if licoes_geradas else 'Nenhuma nova li├º├úo foi gerada (j├í existiam para este per├¡odo/turma).'
            context['resultado_msg'] = resultado_msg
            context['etapa'] = 4
            return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
        if request.POST.get('wizard_back'):
            context.update({
                'ano_letivo': ano_letivo,
                'periodo': periodo,
                'turmas': turmas_ids,
                'material': material,
                'horario': horario,
                'status': status,
                'observacoes': observacoes,
                'nome_licao_padrao': nome_licao_padrao,
                'etapa': 2,
            })
            return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
        # Pr├®-visualiza├º├úo
        licoes_preview = []
        if periodo_obj:
            from .utils import gerar_domingos_periodo
            domingos = gerar_domingos_periodo(periodo_obj.data_inicio, periodo_obj.data_fim)
            for turma in turmas_objs:
                for idx, domingo in enumerate(domingos, start=1):
                    tema = nome_licao_padrao.replace('{n}', str(idx)).replace('{periodo}', periodo_nome)
                    licoes_preview.append({
                        'turma_nome': turma.nome,
                        'data': domingo,
                        'tema': tema,
                        'professor': turma.get_professor_nome(),
                        'status': status,
                    })
        context['licoes_preview'] = licoes_preview
        context['nome_licao_padrao'] = nome_licao_padrao
        return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)

    # Etapa 4: Resultado
    if etapa == 4:
        return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)

from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from core.decorators import secretaria_ebd_required
from django.contrib import messages
from django.shortcuts import render, redirect

# --- SELE├ç├âO DE DADOS PARA C├ôPIA DO PER├ìODO ANTERIOR ---
@page_access_required('escola_biblica')
@require_http_methods(["GET", "POST"])
def copiar_periodo_selecao(request):
    from .models import AnoLetivo, Turma, Classe, Aluno
    ano_destino = request.GET.get('ano_destino') or request.POST.get('ano_destino')
    try:
        ano_destino_int = int(float(str(ano_destino).replace('.', '')))
    except Exception:
        messages.error(request, 'Ano destino inv├ílido.')
        return redirect('escola_biblica:turma_list')
    ano_origem = ano_destino_int - 1
    ano_letivo_origem = AnoLetivo.objects.filter(ano=ano_origem).first()
    if not ano_letivo_origem:
        messages.error(request, f'N├úo existe ano letivo anterior ({ano_origem}) para copiar.')
        return redirect('escola_biblica:turma_list')
    turmas = filtrar_queryset_ebd(Turma.objects.filter(ano_letivo=ano_letivo_origem), request, 'membros__igreja')
    classes = Classe.objects.filter(turma__in=turmas).distinct()
    alunos = filtrar_queryset_ebd(Aluno.objects.filter(turma__ano_letivo=ano_letivo_origem, ativo=True), request, 'turma__membros__igreja')
    if request.method == 'POST':
        turmas_ids = request.POST.getlist('turmas_selecionadas')
        classes_ids = request.POST.getlist('classes_selecionadas')
        alunos_ids = request.POST.getlist('alunos_selecionados')
        ano_letivo_dest, _ = AnoLetivo.objects.get_or_create(ano=ano_destino_int, defaults={'ativo': True})

        # Copiar classes (s├│ cria se n├úo existir)
        classes_criadas = 0
        for classe in classes.filter(id__in=classes_ids):
            filtro_classe = Classe.objects.filter(nome=classe.nome)
            if classe.igreja_id:
                filtro_classe = filtro_classe.filter(igreja_id=classe.igreja_id)
            if not filtro_classe.exists():
                Classe.objects.create(
                    nome=classe.nome,
                    igreja=classe.igreja,
                    departamento=classe.departamento,
                    faixa_etaria=classe.faixa_etaria,
                    descricao=classe.descricao
                )
                classes_criadas += 1

        # Copiar turmas (sempre cria nova para o novo ano)
        turmas_criadas = 0
        membros_copiados_total = 0
        for turma in turmas.filter(id__in=turmas_ids):
            classe_dest = Classe.objects.filter(nome=turma.classe.nome)
            if turma.igreja_id:
                classe_dest = classe_dest.filter(igreja_id=turma.igreja_id)
            classe_dest = classe_dest.first() or turma.classe
            turma_nova, created = Turma.objects.get_or_create(
                nome=turma.nome,
                ano_letivo=ano_letivo_dest,
                defaults={
                    'classe': classe_dest,
                    'igreja': turma.igreja,
                }
            )
            if created:
                turmas_criadas += 1
            # Copiar membros (professores/colaboradores) da turma anterior para a nova turma
            membros_anteriores = turma.membros.all()
            for membro in membros_anteriores:
                turma_nova.membros.add(membro)
                membros_copiados_total += 1

        # Copiar alunos (matricular na nova turma, sem duplicar cadastro de pessoa)
        alunos_copiados = 0
        for aluno in alunos.filter(id__in=alunos_ids):
            turma_dest = Turma.objects.filter(nome=aluno.turma.nome, ano_letivo=ano_letivo_dest).first()
            if turma_dest:
                # Evita duplicidade: s├│ matricula se n├úo houver aluno com mesmo nome e data_nascimento na turma_dest
                existe = Aluno.objects.filter(nome=aluno.nome, data_nascimento=aluno.data_nascimento, turma=turma_dest).exists()
                if not existe:
                    Aluno.objects.create(
                        nome=aluno.nome,
                        data_nascimento=aluno.data_nascimento,
                        turma=turma_dest,
                        responsavel=aluno.responsavel,
                        telefone_responsavel=aluno.telefone_responsavel,
                        observacoes=aluno.observacoes,
                        ativo=True
                    )
                    alunos_copiados += 1

        msg = []
        if turmas_criadas:
            msg.append(f'{turmas_criadas} turma(s) criada(s)')
        if classes_criadas:
            msg.append(f'{classes_criadas} classe(s) criada(s)')
        if alunos_copiados:
            msg.append(f'{alunos_copiados} aluno(s) matriculado(s)')
        if membros_copiados_total:
            msg.append(f'{membros_copiados_total} membro(s) (professores/colaboradores) copiado(s)')
        if not (turmas_criadas or classes_criadas or alunos_copiados or membros_copiados_total):
            messages.warning(request, 'Nenhum dado novo foi criado. Todos os dados selecionados j├í existiam para o ano/per├¡odo de destino.')
        else:
            messages.success(request, f"{' | '.join(msg)} do ano {ano_origem} para {ano_destino_int}.")
        return redirect('escola_biblica:turma_list')
    return render(request, 'escola_biblica/copiar_periodo_selecao.html', {
        'ano_destino': ano_destino_int,
        'turmas': turmas,
        'classes': classes,
        'alunos': alunos,
    })


from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from core.decorators import secretaria_ebd_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import AnoLetivo, PeriodoEBD, Turma
from configuracao.models import ConfiguracaoSistema
from datetime import date
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.shortcuts import render, redirect

# --- COPIAR TURMAS/CLASSES/ALUNOS DO ANO ANTERIOR ---
@page_access_required('escola_biblica')
@require_POST
def copiar_turmas_ano_anterior(request):
    from .models import AnoLetivo, Turma, Classe, Aluno
    ano_destino = request.POST.get('ano_destino')
    try:
        ano_destino_int = int(float(str(ano_destino).replace('.', '')))
    except Exception:
        messages.error(request, 'Ano destino inv├ílido.')
        return redirect('escola_biblica:turma_list')
    ano_letivo_dest, _ = AnoLetivo.objects.get_or_create(ano=ano_destino_int, defaults={'ativo': True})
    ano_origem = ano_letivo_dest.ano - 1
    ano_letivo_origem = AnoLetivo.objects.filter(ano=ano_origem).first()
    if not ano_letivo_origem:
        messages.error(request, f'N├úo existe ano letivo anterior ({ano_origem}) para copiar.')
        return redirect('escola_biblica:turma_list')
    # Copiar classes se n├úo existirem
    turmas_origem = filtrar_queryset_ebd(Turma.objects.filter(ano_letivo=ano_letivo_origem), request, 'membros__igreja')
    classes_origem = Classe.objects.filter(turma__in=turmas_origem).distinct()
    for classe in classes_origem:
        filtro_classe = Classe.objects.filter(nome=classe.nome)
        if classe.igreja_id:
            filtro_classe = filtro_classe.filter(igreja_id=classe.igreja_id)
        if not filtro_classe.exists():
            Classe.objects.create(
                nome=classe.nome,
                igreja=classe.igreja,
                departamento=classe.departamento,
                faixa_etaria=classe.faixa_etaria,
                descricao=classe.descricao
            )
    # Copiar turmas
    turmas_criadas = 0
    alunos_copiados = 0
    for turma in turmas_origem:
        classe_dest = Classe.objects.filter(nome=turma.classe.nome)
        if turma.igreja_id:
            classe_dest = classe_dest.filter(igreja_id=turma.igreja_id)
        classe_dest = classe_dest.first() or turma.classe
        turma_nova, created = Turma.objects.get_or_create(
            nome=turma.nome,
            ano_letivo=ano_letivo_dest,
            defaults={
                'classe': classe_dest,
                'igreja': turma.igreja,
            }
        )
        if created:
            turmas_criadas += 1
        # Copiar alunos ativos
        alunos_origem = turma.alunos.filter(ativo=True)
        for aluno in alunos_origem:
            Aluno.objects.create(
                nome=aluno.nome,
                data_nascimento=aluno.data_nascimento,
                turma=turma_nova,
                responsavel=aluno.responsavel,
                telefone_responsavel=aluno.telefone_responsavel,
                observacoes=aluno.observacoes,
                ativo=True
            )
            alunos_copiados += 1
    messages.success(request, f'{turmas_criadas} turmas e {alunos_copiados} alunos copiados do ano {ano_origem} para {ano_destino_int}.')
    return redirect('escola_biblica:turma_list')

# --- ABRIR NOVO PER├ìODO EBD ---
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from core.decorators import secretaria_ebd_required

@page_access_required('escola_biblica')
@require_POST
def abrir_novo_periodo(request):
    from .models import AnoLetivo, PeriodoEBD
    from configuracao.models import ConfiguracaoSistema
    from .utils import gerar_periodos_ebd
    from datetime import date
    ano_letivo = request.POST.get('ano_letivo')
    tipo_periodo = request.POST.get('tipo_periodo')
    if not ano_letivo or not tipo_periodo:
        messages.error(request, 'Ano letivo e tipo de per├¡odo s├úo obrigat├│rios.')
        return redirect('escola_biblica:turma_list')
    try:
        ano_letivo_int = int(float(str(ano_letivo).replace('.', '')))
    except ValueError:
        messages.error(request, f'Ano letivo inv├ílido: {ano_letivo}')
        return redirect('escola_biblica:turma_list')
    ano_letivo_obj, _ = AnoLetivo.objects.get_or_create(ano=ano_letivo_int, defaults={'ativo': True})
    # Descobre per├¡odos j├í existentes
    periodos_existentes = PeriodoEBD.objects.filter(ano_letivo=ano_letivo_obj, tipo=tipo_periodo).order_by('numero')
    # Gera todos os per├¡odos poss├¡veis para o ano
    periodos_gerados = gerar_periodos_ebd(ano_letivo_int, tipo_periodo)
    # L├│gica: cria s├│ o pr├│ximo per├¡odo (ou o primeiro do ano, se nenhum existir)
    if not periodos_existentes.exists():
        proximo = periodos_gerados[0]
        PeriodoEBD.objects.create(
            ano_letivo=ano_letivo_obj,
            numero=proximo['numero'],
            tipo=tipo_periodo,
            data_inicio=proximo['data_inicio'],
            data_fim=proximo['data_fim']
        )
        messages.success(request, f'Per├¡odo {proximo["numero"]} criado para {ano_letivo}/{tipo_periodo}.')
        # Redireciona para sele├º├úo de c├│pia
        return redirect(f'/escola_biblica/copiar_periodo_selecao/?ano_destino={ano_letivo_int}')
    else:
        ultimo = periodos_existentes.last()
        proximo_num = ultimo.numero + 1
        proximo = next((p for p in periodos_gerados if p['numero'] == proximo_num), None)
        if proximo:
            PeriodoEBD.objects.create(
                ano_letivo=ano_letivo_obj,
                numero=proximo['numero'],
                tipo=tipo_periodo,
                data_inicio=proximo['data_inicio'],
                data_fim=proximo['data_fim']
            )
            messages.success(request, f'Pr├│ximo per├¡odo ({proximo["numero"]}) criado para {ano_letivo}/{tipo_periodo}.')
            return redirect(f'/escola_biblica/copiar_periodo_selecao/?ano_destino={ano_letivo_int}')
        else:
            # Todos os per├¡odos do ano j├í existem, criar novo ano e 1┬║ per├¡odo do pr├│ximo ano
            proximo_ano = ano_letivo_obj.ano + 1
            proximo_ano_obj, _ = AnoLetivo.objects.get_or_create(ano=proximo_ano, defaults={'ativo': True})
            periodos_prox_ano = gerar_periodos_ebd(proximo_ano, tipo_periodo)
            primeiro_prox_ano = periodos_prox_ano[0]
            PeriodoEBD.objects.create(
                ano_letivo=proximo_ano_obj,
                numero=primeiro_prox_ano['numero'],
                tipo=tipo_periodo,
                data_inicio=primeiro_prox_ano['data_inicio'],
                data_fim=primeiro_prox_ano['data_fim']
            )
            messages.success(request, f'Ano {proximo_ano} criado com o 1┬║ per├¡odo ({primeiro_prox_ano["numero"]}) de {tipo_periodo}.')
            return redirect(f'/escola_biblica/copiar_periodo_selecao/?ano_destino={proximo_ano}')
from django.http import JsonResponse
# --- AJAX: Retorna nome do professor da turma ---
from django.views.decorators.http import require_GET
from configuracao.models import ConfiguracaoSistema
from .utils import gerar_licoes_periodos
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv
import json
from collections import defaultdict
from datetime import timedelta, date
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import superintendente_required, secretaria_ebd_required, verificar_assinatura_valida
from django.db.models import Avg, Case, Count, IntegerField, Q, Sum, Value, When
from django.db.models.functions import Coalesce
from django.core.cache import cache
from django.db import transaction
from .models import Licao, Aluno, CadastroAluno, Turma, Frequencia, Classe, Avaliacao, OfertaClasse, TransferenciaAluno, Departamento, DEPARTAMENTOS_SUGERIDOS
from .forms import LicaoForm, AlunoForm, TurmaForm, FrequenciaForm, ClasseForm, AvaliacaoForm, OfertaClasseForm, TransferenciaAlunoForm, ChamadaPresencaFormSet, DepartamentoForm, GerarCronogramaForm
from secretaria.models import Pessoa


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
            turma = get_object_or_404_ebd(Turma.objects.all(), request, 'membros__igreja', pk=turma_id)
            nome = turma.get_professor_nome() or ''
        except Exception:
            nome = ''
    return JsonResponse({'professor': nome})

@page_access_required('escola_biblica')
@verificar_assinatura_valida
def turma_create(request):
    from datetime import date
    from .models import AnoLetivo
    ano_atual = date.today().year
    ano_letivo, created = AnoLetivo.objects.get_or_create(ano=ano_atual, defaults={'ativo': True})
    if request.method == 'POST':
        form = TurmaForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma cadastrada com sucesso!')
            return redirect('escola_biblica:turma_list')
    else:
        form = TurmaForm(initial={'ano_letivo': ano_letivo.pk}, request=request)
        igreja_filtro = request.GET.get('igreja_id')
        if igreja_filtro and 'igreja' in form.fields:
            try:
                igreja_id = int(igreja_filtro)
                if form.fields['igreja'].queryset.filter(pk=igreja_id).exists():
                    form.fields['igreja'].initial = igreja_id
            except ValueError:
                pass
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
    
    transferencias = TransferenciaAluno.objects.filter(aluno__cadastro_id=aluno.cadastro_id).select_related(
        'aluno',
        'turma_origem',
        'turma_destino',
        'usuario_responsavel',
    )
    matriculas_relacionadas = aluno.cadastro.matriculas.select_related('turma', 'turma__ano_letivo').exclude(pk=aluno.pk).order_by('-turma__ano_letivo__ano', '-id')
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
        cadastro.matriculas.select_related('turma', 'turma__ano_letivo')
        .order_by('-turma__ano_letivo__ano', '-updated_at', '-id')
    )

    transferencias = list(
        TransferenciaAluno.objects.filter(aluno__cadastro_id=cadastro.id)
        .select_related('aluno', 'turma_origem', 'turma_destino', 'usuario_responsavel')
        .order_by('-data_transferencia', '-id')
    )

    frequencias = list(
        Frequencia.objects.filter(aluno__cadastro_id=cadastro.id)
        .select_related('aluno', 'aluno__turma', 'aluno__turma__ano_letivo')
        .order_by('-data', '-id')
    )

    avaliacoes = list(
        Avaliacao.objects.filter(aluno__cadastro_id=cadastro.id)
        .select_related('aluno', 'aluno__turma', 'licao', 'licao__turma', 'licao__turma__ano_letivo')
        .order_by('-licao__data', '-id')
    )

    por_ano = {}

    def _ano_bucket(ano):
        return por_ano.setdefault(
            ano,
            {
                'ano': ano,
                'matriculas': [],
                'transferencias': [],
                'total_frequencias': 0,
                'presencas': 0,
                'percentual_frequencia': None,
                'total_avaliacoes': 0,
                'media_notas': None,
                'participacoes': 0,
            },
        )

    for matricula in matriculas:
        ano = getattr(getattr(matricula.turma, 'ano_letivo', None), 'ano', None) or 'Sem ano'
        _ano_bucket(ano)['matriculas'].append(matricula)

    for transferencia in transferencias:
        ano = transferencia.data_transferencia.year if transferencia.data_transferencia else 'Sem ano'
        _ano_bucket(ano)['transferencias'].append(transferencia)

    acumulado_notas = defaultdict(list)

    for freq in frequencias:
        ano = freq.data.year if freq.data else 'Sem ano'
        bucket = _ano_bucket(ano)
        bucket['total_frequencias'] += 1
        if freq.presente:
            bucket['presencas'] += 1

    for avaliacao in avaliacoes:
        data_licao = getattr(avaliacao.licao, 'data', None)
        ano = data_licao.year if data_licao else 'Sem ano'
        bucket = _ano_bucket(ano)
        bucket['total_avaliacoes'] += 1
        if avaliacao.participacao:
            bucket['participacoes'] += 1
        if avaliacao.nota is not None:
            acumulado_notas[ano].append(float(avaliacao.nota))

    for ano, bucket in por_ano.items():
        if bucket['total_frequencias']:
            bucket['percentual_frequencia'] = round((bucket['presencas'] / bucket['total_frequencias']) * 100, 1)
        if acumulado_notas.get(ano):
            notas = acumulado_notas[ano]
            bucket['media_notas'] = round(sum(notas) / len(notas), 2)

    anos_ordenados = sorted(
        por_ano.values(),
        key=lambda item: item['ano'] if isinstance(item['ano'], int) else -1,
        reverse=True,
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

    pessoas_base = Pessoa.objects.filter(igreja_id=cadastro.igreja_id).select_related('tipo_pessoa', 'status_pessoa')
    if busca:
        pessoas_candidatas = pessoas_base.filter(nome__icontains=busca)
    else:
        primeiro_nome = ((cadastro.nome or '').strip().split() or [''])[0]
        pessoas_candidatas = pessoas_base
        if cadastro.data_nascimento and primeiro_nome:
            pessoas_candidatas = pessoas_candidatas.filter(
                Q(nascimento=cadastro.data_nascimento) | Q(nome__icontains=primeiro_nome)
            )
        elif cadastro.data_nascimento:
            pessoas_candidatas = pessoas_candidatas.filter(nascimento=cadastro.data_nascimento)
        elif primeiro_nome:
            pessoas_candidatas = pessoas_candidatas.filter(nome__icontains=primeiro_nome)

    pessoas_candidatas = pessoas_candidatas.annotate(
        prioridade_nome=Case(
            When(nome__iexact=cadastro.nome, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
        prioridade_data=Case(
            When(nascimento=cadastro.data_nascimento, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
    ).order_by('prioridade_nome', 'prioridade_data', 'nome')[:30]

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
        pessoas_base = Pessoa.objects.filter(igreja_id=cadastro.igreja_id).select_related('tipo_pessoa', 'status_pessoa')
        primeiro_nome = ((cadastro.nome or '').strip().split() or [''])[0]
        pessoas_candidatas = pessoas_base
        if cadastro.data_nascimento and primeiro_nome:
            pessoas_candidatas = pessoas_candidatas.filter(
                Q(nascimento=cadastro.data_nascimento) | Q(nome__icontains=primeiro_nome)
            )
        elif cadastro.data_nascimento:
            pessoas_candidatas = pessoas_candidatas.filter(nascimento=cadastro.data_nascimento)
        elif primeiro_nome:
            pessoas_candidatas = pessoas_candidatas.filter(nome__icontains=primeiro_nome)

        linhas.append({
            'cadastro': cadastro,
            'aluno_id': aluno_por_cadastro.get(cadastro.id),
            'pessoas': list(
                pessoas_candidatas.annotate(
                    prioridade_nome=Case(
                        When(nome__iexact=cadastro.nome, then=Value(0)),
                        default=Value(1),
                        output_field=IntegerField(),
                    ),
                    prioridade_data=Case(
                        When(nascimento=cadastro.data_nascimento, then=Value(0)),
                        default=Value(1),
                        output_field=IntegerField(),
                    ),
                ).order_by('prioridade_nome', 'prioridade_data', 'nome')[:20]
            ),
        })

    if request.method == 'POST':
        vinculos_realizados = []
        for cadastro in cadastros:
            pessoa_id = request.POST.get(f'pessoa_cadastro_{cadastro.id}')
            if not pessoa_id:
                continue

            pessoa = Pessoa.objects.filter(pk=pessoa_id, igreja_id=cadastro.igreja_id).first()
            if pessoa is None:
                continue

            cadastro.pessoa = pessoa
            cadastro.save()
            vinculos_realizados.append(f'{cadastro.nome} -> {pessoa.nome}')

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
    alunos = filtrar_alunos_ebd(Aluno.objects.select_related('cadastro', 'turma', 'turma__classe').all(), request)
    periodo_ctx = get_ebd_periodo_filtro(request)
    turma_id = request.GET.get('turma')
    classe_id = request.GET.get('classe')
    inicio = parse_date(request.GET.get('inicio') or '')
    fim = parse_date(request.GET.get('fim') or '')
    alunos = consolidar_alunos_por_cadastro_periodo(
        alunos,
        inicio=inicio,
        fim=fim,
        turma_id=turma_id,
        classe_id=classe_id,
        periodo=periodo_ctx['periodo_selecionado'],
    )
    # Exporta├º├úo CSV
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="relatorio_frequencia.csv"'
        writer = csv.writer(response)
        writer.writerow(['Cadastro', 'Turma de Refer├¬ncia', 'Classe', 'Presen├ºas', 'Total Aulas', 'Frequ├¬ncia (%)'])
        for aluno in alunos:
            writer.writerow([
            aluno.nome_exibicao,
                aluno.turma,
                aluno.turma.classe if aluno.turma else '',
                aluno.presencas,
                aluno.total_freq,
                aluno.freq_percent if aluno.freq_percent is not None else '-',
            ])
        return response
    return render(request, 'escola_biblica/relatorio_frequencia.html', {
        'turmas': turmas,
        'classes': classes,
        'alunos': alunos,
        **periodo_ctx,
    })

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

    if periodo_selecionado:
        mes_atual = periodo_selecionado.data_inicio.replace(day=1)
        limite = periodo_selecionado.data_fim.replace(day=1)
        meses = []
        while mes_atual <= limite:
            meses.append(mes_atual)
            mes_atual = (mes_atual + timezone.timedelta(days=32)).replace(day=1)
    elif ano_letivo_selecionado:
        meses = [timezone.datetime(ano_letivo_selecionado.ano, mes, 1).date() for mes in range(1, 13)]
    else:
        hoje = timezone.now().date()
        meses = [(hoje.replace(day=1) - timezone.timedelta(days=30 * i)).replace(day=1) for i in range(11, -1, -1)]

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

    matriculas_por_cadastro = defaultdict(list)
    for cadastro in cadastros:
        for matricula in cadastro.matriculas.all():
            matriculas_por_cadastro[cadastro.id].append(matricula)

    transferencias_por_cadastro = defaultdict(list)
    for transferencia in transferencias:
        transferencias_por_cadastro[transferencia.aluno.cadastro_id].append(transferencia)

    def _matricula_referencia_snapshot(cadastro_id, data_referencia):
        matriculas = matriculas_por_cadastro.get(cadastro_id, [])
        if not matriculas:
            return None

        matriculas_por_turma = defaultdict(list)
        for matricula in matriculas:
            matriculas_por_turma[matricula.turma_id].append(matricula)

        for turma_id in matriculas_por_turma:
            matriculas_por_turma[turma_id].sort(key=lambda item: (item.ativo, item.updated_at, item.id), reverse=True)

        transferencia_passada = None
        transferencia_futura = None
        for transferencia in transferencias_por_cadastro.get(cadastro_id, []):
            if transferencia.data_transferencia and transferencia.data_transferencia <= data_referencia:
                transferencia_passada = transferencia
            elif transferencia_futura is None:
                transferencia_futura = transferencia
                break

        if transferencia_passada is not None:
            candidatas = matriculas_por_turma.get(transferencia_passada.turma_destino_id)
            if candidatas:
                return candidatas[0]

        if transferencia_futura is not None:
            candidatas = matriculas_por_turma.get(transferencia_futura.turma_origem_id)
            if candidatas:
                return candidatas[0]

        matricula_ativa = next((matricula for matricula in sorted(matriculas, key=lambda item: (item.ativo, item.updated_at, item.id), reverse=True) if matricula.ativo), None)
        if matricula_ativa is not None:
            return matricula_ativa

        return sorted(matriculas, key=lambda item: (item.updated_at, item.id), reverse=True)[0]

    alunos_evolucao = defaultdict(lambda: [0] * len(meses))
    for idx, mes in enumerate(meses):
        referencia = ((mes + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1))
        for cadastro in cadastros:
            matricula = _matricula_referencia_snapshot(cadastro.id, referencia)
            if matricula is None or matricula.turma_id is None or matricula.turma.classe_id is None:
                continue
            if ano_letivo_selecionado and matricula.turma.ano_letivo_id != ano_letivo_selecionado.id:
                continue
            classe_nome = matricula.turma.classe.nome
            alunos_evolucao[classe_nome][idx] += 1

    ofertas_evolucao = defaultdict(lambda: [0] * len(meses))
    for idx, mes in enumerate(meses):
        prox_mes = (mes + timezone.timedelta(days=32)).replace(day=1)
        for classe in classes:
            total = filtrar_queryset_ebd(
                OfertaClasse.objects.filter(classe=classe, data__gte=mes, data__lt=prox_mes),
                request,
                'classe__turma__membros__igreja',
            ).aggregate(s=Sum('valor'))['s'] or 0
            ofertas_evolucao[classe.nome][idx] = float(total)

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
    departamentos = dict(Classe.DEPARTAMENTO_CHOICES)
    igrejas_escopo = get_ebd_scope_churches(request)
    alunos_por_departamento = {d: 0 for d in departamentos.values()}
    for dep_key, dep_label in departamentos.items():
        alunos_qs = Aluno.objects.filter(turma__classe__departamento=dep_key)
        if ano_letivo_selecionado:
            alunos_qs = alunos_qs.filter(turma__ano_letivo=ano_letivo_selecionado)
        alunos_por_departamento[dep_label] = filtrar_queryset_ebd(alunos_qs, request, 'turma__membros__igreja').count()

    ofertas_por_departamento = {d: 0 for d in departamentos.values()}
    for dep_key, dep_label in departamentos.items():
        ofertas_qs = OfertaClasse.objects.filter(
            Q(turma__classe__departamento=dep_key) | Q(turma__isnull=True, classe__departamento=dep_key)
        )
        if periodo_selecionado:
            ofertas_qs = ofertas_qs.filter(data__gte=periodo_selecionado.data_inicio, data__lte=periodo_selecionado.data_fim)
        elif ano_letivo_selecionado:
            ofertas_qs = ofertas_qs.filter(data__year=ano_letivo_selecionado.ano)
        ofertas_por_departamento[dep_label] = ofertas_qs.filter(
            Q(turma__igreja__in=igrejas_escopo) |
            Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas_escopo) |
            Q(turma__isnull=True, classe__igreja__in=igrejas_escopo) |
            Q(turma__isnull=True, classe__igreja__isnull=True, classe__turma__membros__igreja__in=igrejas_escopo)
        ).distinct().aggregate(total=Sum('valor'))['total'] or 0

    ofertas_por_classe = {}
    for classe in filtrar_queryset_ebd(Classe.objects.all(), request, 'turma__membros__igreja'):
        ofertas_qs = OfertaClasse.objects.filter(
            Q(turma__classe=classe) | Q(turma__isnull=True, classe=classe)
        )
        if periodo_selecionado:
            ofertas_qs = ofertas_qs.filter(data__gte=periodo_selecionado.data_inicio, data__lte=periodo_selecionado.data_fim)
        elif ano_letivo_selecionado:
            ofertas_qs = ofertas_qs.filter(data__year=ano_letivo_selecionado.ano)
        ofertas_por_classe[classe.nome] = ofertas_qs.filter(
            Q(turma__igreja__in=igrejas_escopo) |
            Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas_escopo) |
            Q(turma__isnull=True, classe__igreja__in=igrejas_escopo) |
            Q(turma__isnull=True, classe__igreja__isnull=True, classe__turma__membros__igreja__in=igrejas_escopo)
        ).distinct().aggregate(total=Sum('valor'))['total'] or 0

    alunos_por_classe = {}
    for classe in filtrar_queryset_ebd(Classe.objects.all(), request, 'turma__membros__igreja'):
        alunos_qs = Aluno.objects.filter(turma__classe=classe)
        if ano_letivo_selecionado:
            alunos_qs = alunos_qs.filter(turma__ano_letivo=ano_letivo_selecionado)
        alunos_por_classe[classe.nome] = filtrar_queryset_ebd(alunos_qs, request, 'turma__membros__igreja').count()

    context = {
        'alunos_por_departamento': json.dumps(alunos_por_departamento),
        'ofertas_por_departamento': json.dumps(ofertas_por_departamento),
        'ofertas_por_classe': json.dumps(ofertas_por_classe),
        'alunos_por_classe': json.dumps(alunos_por_classe),
        **periodo_ctx,
    }
    return render(request, 'escola_biblica/dashboard_graficos.html', context)

# --- OFERTAS POR CLASSE ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def oferta_classe_list(request):
    igrejas_escopo = get_ebd_scope_churches(request)
    ofertas = OfertaClasse.objects.select_related('turma', 'classe').order_by('-data').filter(
        Q(turma__igreja__in=igrejas_escopo) |
        Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas_escopo) |
        Q(turma__isnull=True, classe__igreja__in=igrejas_escopo) |
        Q(turma__isnull=True, classe__igreja__isnull=True, classe__turma__membros__igreja__in=igrejas_escopo)
    ).distinct()
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
    igrejas_escopo = get_ebd_scope_churches(request)
    oferta = get_object_or_404(
        OfertaClasse.objects.select_related('turma', 'classe').filter(
            Q(turma__igreja__in=igrejas_escopo) |
            Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas_escopo) |
            Q(turma__isnull=True, classe__igreja__in=igrejas_escopo) |
            Q(turma__isnull=True, classe__igreja__isnull=True, classe__turma__membros__igreja__in=igrejas_escopo)
        ).distinct(),
        pk=pk,
    )
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
    igrejas_escopo = get_ebd_scope_churches(request)
    oferta = get_object_or_404(
        OfertaClasse.objects.select_related('turma', 'classe').filter(
            Q(turma__igreja__in=igrejas_escopo) |
            Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas_escopo) |
            Q(turma__isnull=True, classe__igreja__in=igrejas_escopo) |
            Q(turma__isnull=True, classe__igreja__isnull=True, classe__turma__membros__igreja__in=igrejas_escopo)
        ).distinct(),
        pk=pk,
    )
    if request.method == 'POST':
        log_ebd_audit_event(
            request,
            'oferta_delete',
            oferta_id=oferta.id,
            turma_id=oferta.turma_id,
            data=oferta.data,
            valor=oferta.valor,
        )
        oferta.delete()
        messages.success(request, 'Oferta exclu├¡da com sucesso!')
        return redirect('escola_biblica:oferta_classe_list')
    return render(request, 'escola_biblica/oferta_classe_confirm_delete.html', {'oferta': oferta})

# --- RELAT├ôRIO DE ALUNOS ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def relatorio_alunos(request):
    turmas = filtrar_turmas_ebd(Turma.objects.all(), request)
    classes = filtrar_classes_ebd(Classe.objects.all(), request)
    alunos = filtrar_alunos_ebd(Aluno.objects.select_related('cadastro', 'turma', 'turma__classe').all(), request)
    periodo_ctx = get_ebd_periodo_filtro(request)
    turma_id = request.GET.get('turma')
    classe_id = request.GET.get('classe')
    inicio = parse_date(request.GET.get('inicio') or '')
    fim = parse_date(request.GET.get('fim') or '')
    alunos = consolidar_alunos_por_cadastro_periodo(
        alunos,
        inicio=inicio,
        fim=fim,
        turma_id=turma_id,
        classe_id=classe_id,
        periodo=periodo_ctx['periodo_selecionado'],
    )
    return render(request, 'escola_biblica/relatorio_alunos.html', {
        'turmas': turmas,
        'classes': classes,
        'alunos': alunos,
        **periodo_ctx,
    })
# --- LICOES ---
 
 # --- AVALIA├ç├òES ---
@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def avaliacao_list(request):
    avaliacoes = filtrar_avaliacoes_ebd(
        Avaliacao.objects.select_related('aluno', 'aluno__cadastro', 'aluno__turma', 'licao', 'licao__turma').all(),
        request,
    ).order_by('-licao__data', 'aluno__cadastro__nome')
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
    avaliacao = get_object_or_404(
        filtrar_avaliacoes_ebd(Avaliacao.objects.select_related('aluno', 'aluno__cadastro', 'licao'), request),
        pk=pk,
    )
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
def avaliacao_delete(request, pk):
    avaliacao = get_object_or_404(
        filtrar_avaliacoes_ebd(Avaliacao.objects.select_related('aluno', 'aluno__cadastro', 'licao'), request),
        pk=pk,
    )
    if request.method == 'POST':
        avaliacao.delete()
        messages.success(request, 'Avalia├º├úo exclu├¡da com sucesso!')
        return redirect('escola_biblica:avaliacao_list')
    return render(request, 'escola_biblica/avaliacao_confirm_delete.html', {'avaliacao': avaliacao})
@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def licao_list(request):
    from .models import PeriodoEBD, AnoLetivo
    from django.utils import timezone
    hoje = timezone.now().date()
    
    # Buscar li├º├Áes com escopo correto
    licoes_scope = filtrar_queryset_ebd(Licao.objects.all(), request, 'turma__membros__igreja')
    
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
    from .models import Turma
    turma_nomes = filtrar_queryset_ebd(Turma.objects.all(), request, 'membros__igreja').values_list('nome', flat=True).distinct().order_by('nome')
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
def licao_create(request):
    turmas = filtrar_queryset_ebd(Turma.objects.all(), request, 'membros__igreja')
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
    licao = get_object_or_404_ebd(Licao.objects.select_related('turma'), request, 'turma__membros__igreja', pk=pk)
    turmas = filtrar_queryset_ebd(Turma.objects.all(), request, 'membros__igreja')
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
    licao = get_object_or_404_ebd(Licao.objects.select_related('turma'), request, 'turma__membros__igreja', pk=pk)
    if request.method == 'POST':
        licao.delete()
        messages.success(request, 'Li├º├úo exclu├¡da com sucesso!')
        return redirect('escola_biblica:licao_list')
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
        igreja_filtro = request.GET.get('igreja_id')
        if igreja_filtro and 'igreja' in form.fields:
            try:
                igreja_id = int(igreja_filtro)
                if form.fields['igreja'].queryset.filter(pk=igreja_id).exists():
                    form.fields['igreja'].initial = igreja_id
            except ValueError:
                pass
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
        classe.delete()
        messages.success(request, 'Classe exclu├¡da com sucesso!')
        return redirect('escola_biblica:classe_list')
    return render(request, 'escola_biblica/classe_confirm_delete.html', {'classe': classe})






@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
@log_ebd_endpoint('dashboard')
def dashboard(request):
    auto_sync_ebd_periodos_e_licoes(request)
    turmas = filtrar_turmas_ebd(Turma.objects.all(), request)
    alunos = filtrar_alunos_ebd(Aluno.objects.all(), request)
    classes = filtrar_classes_ebd(Classe.objects.all(), request)
    licoes = filtrar_queryset_ebd(Licao.objects.all(), request, 'turma__igreja')
    avaliacoes = filtrar_queryset_ebd(Avaliacao.objects.all(), request, 'aluno__turma__igreja')
    igrejas_escopo = get_ebd_scope_churches(request)

    igreja = getattr(request, 'igreja_ativa', None)
    if igreja is None and igrejas_escopo.count() == 1:
        igreja = igrejas_escopo.first()

    hoje = date.today()
    ano_atual = hoje.year

    periodo_ctx = get_ebd_periodo_filtro(request)
    ebd_config_source_info = get_ebd_config_source_info(request)
    ebd_pontos_config = get_ebd_pontos_config_com_fallback(request)
    tipo_periodo = periodo_ctx['tipo_periodo']
    ano_letivo_qs = periodo_ctx['anos_letivos']
    ano_letivo_selecionado = periodo_ctx['ano_letivo_selecionado']
    periodos_disponiveis = periodo_ctx['periodos_disponiveis']
    periodo_selecionado = periodo_ctx['periodo_selecionado']
    from configuracao.models import ConfiguracaoSistema
    periodo_tipo_label = dict(ConfiguracaoSistema.EBD_PERIODO_CHOICES).get(tipo_periodo, tipo_periodo.title())

    cache_version = cache.get('ebd:dashboard:version') or 1
    cache_key = (
        f"ebd:dashboard:v{cache_version}:u{request.user.pk}:ig{getattr(igreja, 'pk', 'all')}"
        f":tp:{tipo_periodo}:a:{request.GET.get('ano_letivo', '')}:p:{request.GET.get('periodo', '')}:r:{request.GET.get('data_relatorio', '')}"
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

    ebd_config_igreja_link = None
    from configuracao.utils import pode_editar_configuracao_org
    if pode_editar_configuracao_org(request.user):
        if igreja is not None:
            ebd_config_igreja_link = reverse('configuracao:editar_igreja_config', args=[igreja.pk])
        else:
            ebd_config_igreja_link = reverse('configuracao:lista_igrejas')

    if periodo_selecionado:
        data_inicio_periodo = periodo_selecionado.data_inicio
        data_fim_periodo = periodo_selecionado.data_fim
    else:
        data_inicio_periodo = hoje.replace(day=1)
        data_fim_periodo = hoje

    periodo_anterior_obj = PeriodoEBD.objects.filter(
        tipo=tipo_periodo,
        data_fim__lt=data_inicio_periodo,
    ).order_by('-data_fim').first()

    if periodo_anterior_obj:
        data_inicio_periodo_anterior = periodo_anterior_obj.data_inicio
        data_fim_periodo_anterior = periodo_anterior_obj.data_fim
    else:
        dias_periodo = max((data_fim_periodo - data_inicio_periodo).days + 1, 1)
        data_fim_periodo_anterior = data_inicio_periodo - timedelta(days=1)
        data_inicio_periodo_anterior = data_fim_periodo_anterior - timedelta(days=dias_periodo - 1)

    total_oferta = OfertaClasse.objects.filter(
        Q(turma__igreja__in=igrejas_escopo)
        | Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas_escopo)
        | Q(turma__isnull=True, classe__igreja__in=igrejas_escopo)
        | Q(turma__isnull=True, classe__igreja__isnull=True, classe__turma__membros__igreja__in=igrejas_escopo)
    ).distinct().aggregate(total=Sum('valor'))['total'] or 0

    meses = [(hoje.replace(day=1) - timedelta(days=30 * i)).replace(day=1) for i in range(11, -1, -1)]
    alunos_evolucao = []
    for m in meses:
        prox_mes = (m + timedelta(days=32)).replace(day=1)
        qs = Aluno.objects.filter(
            turma__isnull=False,
            ativo=True,
            turma__ano_letivo__ativo=True,
            turma__ano_letivo__ano__contains=str(m.year),
            turma__classe__isnull=False,
            turma__classe__departamento__in=[c[0] for c in Classe.DEPARTAMENTO_CHOICES],
            data_nascimento__isnull=False,
            data_nascimento__lte=prox_mes,
        )
        if igreja:
            qs = qs.filter(turma__membros__igreja=igreja).distinct()
        alunos_evolucao.append(qs.count())

    alunos_ids = list(alunos.values_list('id', flat=True))

    def _media_frequencia(alunos_ids_base, data_inicio, data_fim):
        if not alunos_ids_base:
            return 0
        freq_periodo = Frequencia.objects.filter(
            aluno_id__in=alunos_ids_base,
            data__gte=data_inicio,
            data__lte=data_fim,
        )
        if igreja:
            freq_periodo = freq_periodo.filter(aluno__turma__membros__igreja=igreja).distinct()

        resumo = freq_periodo.values('aluno_id').annotate(
            total=Count('id'),
            presencas=Count('id', filter=Q(presente=True)),
        )
        if not resumo:
            return 0

        soma_percentuais = 0
        qtd_alunos = 0
        for item in resumo:
            total = item['total'] or 0
            if total > 0:
                soma_percentuais += (item['presencas'] / total)
                qtd_alunos += 1
        return round((soma_percentuais / qtd_alunos) * 100, 1) if qtd_alunos else 0

    freq_geral = _media_frequencia(alunos_ids, data_inicio_periodo, data_fim_periodo)
    freq_mes_anterior = _media_frequencia(alunos_ids, data_inicio_periodo_anterior, data_fim_periodo_anterior)

    freq_mes = Frequencia.objects.filter(data__gte=data_inicio_periodo, data__lte=data_fim_periodo)
    if igreja:
        freq_mes = freq_mes.filter(aluno__turma__membros__igreja=igreja).distinct()
    engajados = 0
    for aluno_id in alunos_ids:
        freq_aluno = freq_mes.filter(aluno_id=aluno_id)
        total = freq_aluno.count()
        presencas = freq_aluno.filter(presente=True).count()
        if total > 0 and presencas / total >= 0.75:
            engajados += 1
    engajamento_percent = round((engajados / len(alunos_ids)) * 100, 1) if alunos_ids else 0

    evasao_qs = Aluno.objects.filter(ativo=False, turma__ano_letivo__ano__contains=str(ano_atual))
    if igreja:
        evasao_qs = evasao_qs.filter(turma__membros__igreja=igreja).distinct()
    evasao = evasao_qs.count()

    ranking_classes = []
    base_frequencia_classe = Frequencia.objects.filter(
        aluno__turma__classe__in=classes,
        aluno__ativo=True,
        data__gte=data_inicio_periodo,
        data__lte=data_fim_periodo,
    )
    if igreja:
        base_frequencia_classe = base_frequencia_classe.filter(aluno__turma__membros__igreja=igreja).distinct()

    resumo_classes = base_frequencia_classe.values('aluno__turma__classe_id', 'aluno__turma__classe__nome').annotate(
        total=Count('id'),
        presentes=Count('id', filter=Q(presente=True)),
    )

    for item in resumo_classes:
        total = int(item.get('total') or 0)
        presentes = int(item.get('presentes') or 0)
        frequencia_media = round((presentes / total) * 100, 1) if total else 0
        ranking_classes.append({'classe': item['aluno__turma__classe__nome'], 'frequencia_media': frequencia_media})

    ranking_classes = sorted(ranking_classes, key=lambda x: x['frequencia_media'], reverse=True)

    ranking_alunos_pontos = []
    frequencias_pontos_qs = Frequencia.objects.filter(
        aluno__turma__in=turmas,
        data__gte=data_inicio_periodo,
        data__lte=data_fim_periodo,
    )
    if ano_letivo_selecionado:
        frequencias_pontos_qs = frequencias_pontos_qs.filter(aluno__turma__ano_letivo=ano_letivo_selecionado)

    pontos_por_cadastro = list(
        frequencias_pontos_qs.values('aluno__cadastro_id').annotate(
            total_pontos=Sum(Coalesce('pontos_total', _get_expr_pontos_frequencia(ebd_pontos_config))),
            presencas=Count('id', filter=Q(presente=True)),
        )
    )

    cadastro_ids_ranking = [item['aluno__cadastro_id'] for item in pontos_por_cadastro if item['aluno__cadastro_id']]
    referencia_por_cadastro = {}
    if cadastro_ids_ranking:
        alunos_referencia_qs = filtrar_alunos_ebd(
            Aluno.objects.filter(cadastro_id__in=cadastro_ids_ranking).select_related('cadastro', 'turma', 'turma__classe', 'turma__ano_letivo'),
            request,
        )
        if ano_letivo_selecionado:
            alunos_referencia_qs = alunos_referencia_qs.filter(turma__ano_letivo=ano_letivo_selecionado)

        for aluno_ref in alunos_referencia_qs.order_by('cadastro_id', '-ativo', '-updated_at', '-id'):
            referencia_por_cadastro.setdefault(aluno_ref.cadastro_id, aluno_ref)

    for item in pontos_por_cadastro:
        cadastro_id = item['aluno__cadastro_id']
        if not cadastro_id:
            continue
        aluno_ref = referencia_por_cadastro.get(cadastro_id)
        if aluno_ref is None:
            continue

        ranking_alunos_pontos.append({
            'nome': aluno_ref.cadastro.nome,
            'turma': aluno_ref.turma.nome if aluno_ref.turma_id else '-',
            'classe': aluno_ref.turma.classe.nome if aluno_ref.turma_id and aluno_ref.turma.classe_id else '-',
            'total_pontos': int(item.get('total_pontos') or 0),
            'presencas': int(item.get('presencas') or 0),
        })

    ranking_alunos_pontos.sort(key=lambda r: (-r['total_pontos'], -r['presencas'], r['nome'].casefold()))
    for pos, item in enumerate(ranking_alunos_pontos, start=1):
        item['posicao'] = pos

    ranking_ofertas = []
    for classe in classes:
        oferta_qs = OfertaClasse.objects.filter(
            Q(turma__classe=classe) | Q(turma__isnull=True, classe=classe),
            data__year=ano_atual,
        )
        if igreja:
            oferta_qs = oferta_qs.filter(
                Q(turma__igreja=igreja)
                | Q(turma__igreja__isnull=True, turma__membros__igreja=igreja)
                | Q(turma__isnull=True, classe__igreja=igreja)
                | Q(turma__isnull=True, classe__igreja__isnull=True, classe__turma__membros__igreja=igreja)
            ).distinct()
        total_oferta_classe = oferta_qs.aggregate(s=Sum('valor'))['s'] or 0
        ranking_ofertas.append({'classe': classe.nome, 'total_oferta': float(total_oferta_classe)})
    ranking_ofertas = sorted(ranking_ofertas, key=lambda x: x['total_oferta'], reverse=True)

    alunos_novos_qs = Aluno.objects.filter(
        turma__isnull=False,
        ativo=True,
        turma__ano_letivo__ativo=True,
        created_at__date__gte=data_inicio_periodo,
        created_at__date__lte=data_fim_periodo,
    )
    if igreja:
        alunos_novos_qs = alunos_novos_qs.filter(turma__membros__igreja=igreja).distinct()
    alunos_novos = alunos_novos_qs.count()

    alunos_novos_mes_anterior_qs = Aluno.objects.filter(
        turma__isnull=False,
        ativo=True,
        turma__ano_letivo__ativo=True,
        created_at__date__gte=data_inicio_periodo_anterior,
        created_at__date__lte=data_fim_periodo_anterior,
    )
    if igreja:
        alunos_novos_mes_anterior_qs = alunos_novos_mes_anterior_qs.filter(turma__membros__igreja=igreja).distinct()
    alunos_novos_mes_anterior = alunos_novos_mes_anterior_qs.count()

    transferidos_mes_qs = TransferenciaAluno.objects.filter(
        data_transferencia__gte=data_inicio_periodo,
        data_transferencia__lte=data_fim_periodo,
    )
    if igreja:
        transferidos_mes_qs = transferidos_mes_qs.filter(
            Q(turma_origem__membros__igreja=igreja) | Q(turma_destino__membros__igreja=igreja)
        ).distinct()
    transferidos_mes = transferidos_mes_qs.count()

    ofertas_mes_qs = OfertaClasse.objects.filter(data__gte=data_inicio_periodo, data__lte=data_fim_periodo)
    ofertas_mes_anterior_qs = OfertaClasse.objects.filter(
        data__gte=data_inicio_periodo_anterior,
        data__lte=data_fim_periodo_anterior,
    )
    if igreja:
        filtro_igreja_oferta = (
            Q(turma__igreja=igreja)
            | Q(turma__igreja__isnull=True, turma__membros__igreja=igreja)
            | Q(turma__isnull=True, classe__igreja=igreja)
            | Q(turma__isnull=True, classe__igreja__isnull=True, classe__turma__membros__igreja=igreja)
        )
        ofertas_mes_qs = ofertas_mes_qs.filter(filtro_igreja_oferta).distinct()
        ofertas_mes_anterior_qs = ofertas_mes_anterior_qs.filter(filtro_igreja_oferta).distinct()

    total_ofertas_mes = float(ofertas_mes_qs.aggregate(total=Sum('valor'))['total'] or 0)
    total_ofertas_mes_anterior = float(ofertas_mes_anterior_qs.aggregate(total=Sum('valor'))['total'] or 0)

    faixas = [
        ('0-5', 0, 5),
        ('6-12', 6, 12),
        ('13-17', 13, 17),
        ('18-29', 18, 29),
        ('30-59', 30, 59),
        ('60+', 60, 200),
    ]
    faixas_etarias_labels = [f[0] for f in faixas]
    faixas_etarias_counts = []
    for _label, min_idade, max_idade in faixas:
        count = 0
        for aluno in alunos:
            if aluno.data_nascimento:
                idade = (hoje - aluno.data_nascimento).days // 365
                if min_idade <= idade <= max_idade:
                    count += 1
        faixas_etarias_counts.append(count)

    def _comparativo_card(label, atual, anterior, melhora_quando='up', formato='int'):
        diferenca = atual - anterior
        subiu = diferenca > 0
        melhorou = subiu if melhora_quando == 'up' else not subiu
        if diferenca == 0:
            tone = 'is-neutral'
            icon = 'fas fa-minus'
        else:
            tone = 'is-positive' if melhorou else 'is-warning'
            icon = 'fas fa-arrow-up' if subiu else 'fas fa-arrow-down'

        if formato == 'currency':
            diferenca_label = f"{diferenca:+.2f}"
        elif formato == 'percent':
            diferenca_label = f"{diferenca:+.1f}"
        else:
            diferenca_label = f"{int(diferenca):+d}"

        return {
            'label': label,
            'atual': atual,
            'anterior': anterior,
            'diferenca': diferenca,
            'diferenca_label': diferenca_label,
            'tone': tone,
            'icon': icon,
            'format': formato,
        }

    comparativo_periodo_cards = [
        _comparativo_card('Novos alunos', alunos_novos, alunos_novos_mes_anterior, 'up', 'int'),
        _comparativo_card('Frequência média (%)', freq_geral, freq_mes_anterior, 'up', 'percent'),
        _comparativo_card('Ofertas do período (R$)', total_ofertas_mes, total_ofertas_mes_anterior, 'up', 'currency'),
    ]

    data_relatorio_str = request.GET.get('data_relatorio')
    if data_relatorio_str:
        data_relatorio_dia = parse_date(data_relatorio_str) or hoje
    else:
        ultima_licao = licoes.order_by('-data').first()
        data_relatorio_dia = ultima_licao.data if ultima_licao else hoje

    turmas_relatorio_qs = turmas
    if ano_letivo_selecionado:
        turmas_relatorio_qs = turmas_relatorio_qs.filter(ano_letivo=ano_letivo_selecionado)
    turmas_relatorio_qs = turmas_relatorio_qs.select_related('classe').annotate(
        matriculados_ativos=Count('alunos', filter=Q(alunos__ativo=True), distinct=True)
    ).order_by('nome')

    frequencias_relatorio = Frequencia.objects.filter(
        aluno__turma__in=turmas_relatorio_qs,
        data=data_relatorio_dia,
    )
    frequencias_relatorio_map = {
        item['aluno__turma_id']: item
        for item in frequencias_relatorio.values('aluno__turma_id').annotate(
            chamadas=Count('id'),
            presentes=Count('id', filter=Q(presente=True)),
            biblias=Count('id', filter=Q(trouxe_biblia=True)),
            ofertas_individuais=Count('id', filter=Q(trouxe_oferta=True)),
        )
    }

    ofertas_turma_map = {
        item['turma_id']: item['total'] or 0
        for item in OfertaClasse.objects.filter(
            turma__in=turmas_relatorio_qs,
            data=data_relatorio_dia,
        ).values('turma_id').annotate(total=Sum('valor'))
    }

    classes_ids_relatorio = list(turmas_relatorio_qs.values_list('classe_id', flat=True).distinct())
    ofertas_classe_map = {
        item['classe_id']: item['total'] or 0
        for item in OfertaClasse.objects.filter(
            turma__isnull=True,
            classe_id__in=classes_ids_relatorio,
            data=data_relatorio_dia,
        ).values('classe_id').annotate(total=Sum('valor'))
    }

    relatorio_instantaneo_turmas = []
    for turma in turmas_relatorio_qs:
        resumo_frequencia = frequencias_relatorio_map.get(turma.id, {})
        matriculados = turma.matriculados_ativos or 0
        presentes = resumo_frequencia.get('presentes', 0)
        ausentes = max(matriculados - presentes, 0)
        biblias = resumo_frequencia.get('biblias', 0)
        alunos_ofertantes = resumo_frequencia.get('ofertas_individuais', 0)
        chamada_realizada = (resumo_frequencia.get('chamadas', 0) or 0) > 0

        oferta_turma_valor = ofertas_turma_map.get(turma.id, 0) or 0
        oferta_classe_valor = ofertas_classe_map.get(turma.classe_id, 0) or 0
        oferta_total = oferta_turma_valor + oferta_classe_valor

        if not chamada_realizada:
            status_label = 'Pendente'
            status_tone = 'is-pending'
        elif oferta_total > 0:
            status_label = 'Completo'
            status_tone = 'is-complete'
        else:
            status_label = 'Parcial'
            status_tone = 'is-partial'

        relatorio_instantaneo_turmas.append({
            'turma_id': turma.id,
            'turma_nome': turma.nome,
            'segmento_nome': turma.classe.nome if turma.classe_id else '-',
            'matriculados': matriculados,
            'presentes': presentes,
            'ausentes': ausentes,
            'biblias': biblias,
            'alunos_ofertantes': alunos_ofertantes,
            'oferta_total': oferta_total,
            'chamada_realizada': chamada_realizada,
            'status_label': status_label,
            'status_tone': status_tone,
        })

    status_prioridade = {'is-pending': 0, 'is-partial': 1, 'is-complete': 2}
    relatorio_instantaneo_turmas.sort(
        key=lambda item: (status_prioridade.get(item['status_tone'], 9), item['turma_nome'].casefold())
    )

    turmas_pendentes_relatorio = sum(1 for item in relatorio_instantaneo_turmas if item['status_tone'] == 'is-pending')
    turmas_parciais_relatorio = sum(1 for item in relatorio_instantaneo_turmas if item['status_tone'] == 'is-partial')
    turmas_completas_relatorio = sum(1 for item in relatorio_instantaneo_turmas if item['status_tone'] == 'is-complete')

    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    janela_inicio_semana = max(inicio_semana, data_inicio_periodo)
    janela_fim_semana = min(hoje, fim_semana, data_fim_periodo)
    dia_semana_ebd = get_ebd_dia_semana(request)
    houve_janela_operacional = hoje.weekday() >= dia_semana_ebd and janela_inicio_semana <= janela_fim_semana

    turmas_ids = list(turmas.values_list('id', flat=True))
    turmas_previstas_semana = len(turmas_ids) if houve_janela_operacional else 0
    turmas_com_chamada_semana = 0
    turmas_sem_chamada_semana = 0

    if turmas_previstas_semana > 0:
        turmas_com_chamada_semana = Frequencia.objects.filter(
            aluno__turma_id__in=turmas_ids,
            data__gte=janela_inicio_semana,
            data__lte=janela_fim_semana,
        ).values_list('aluno__turma_id', flat=True).distinct().count()
        turmas_sem_chamada_semana = max(turmas_previstas_semana - turmas_com_chamada_semana, 0)

    insights_dashboard = []
    if freq_geral >= 80:
        insights_dashboard.append({
            'tone': 'is-positive',
            'icon': 'fas fa-circle-check',
            'title': 'Frequência saudável',
            'message': f'Frequência média do período em {freq_geral:.1f}%. Mantenha o ritmo das turmas com melhor presença.',
            'cta_label': 'Ver frequência',
            'cta_url': reverse('escola_biblica:frequencia_list'),
        })
    elif freq_geral < 65:
        insights_dashboard.append({
            'tone': 'is-warning',
            'icon': 'fas fa-triangle-exclamation',
            'title': 'Atenção na presença',
            'message': f'Frequência média do período em {freq_geral:.1f}%. Vale reforçar contato com responsáveis e líderes de turma.',
            'cta_label': 'Abrir turmas',
            'cta_url': reverse('escola_biblica:turma_list'),
        })

    if evasao > 0:
        insights_dashboard.append({
            'tone': 'is-danger',
            'icon': 'fas fa-user-minus',
            'title': 'Evasão no ano letivo',
            'message': f'Há {evasao} aluno(s) inativos no ano. Priorize o acompanhamento das turmas com maior queda.',
            'cta_label': 'Ver alunos',
            'cta_url': reverse('escola_biblica:aluno_list'),
        })

    if total_ofertas_mes > total_ofertas_mes_anterior:
        insights_dashboard.append({
            'tone': 'is-info',
            'icon': 'fas fa-hand-holding-dollar',
            'title': 'Evolução nas ofertas',
            'message': 'As ofertas cresceram em relação ao período anterior. Bom sinal de participação comunitária.',
            'cta_label': 'Abrir ofertas',
            'cta_url': reverse('escola_biblica:oferta_classe_list'),
        })

    if not insights_dashboard:
        insights_dashboard.append({
            'tone': 'is-neutral',
            'icon': 'fas fa-circle-info',
            'title': 'Painel estável no período',
            'message': 'Sem alertas críticos neste recorte. Mantenha a rotina de chamada, ensino e acompanhamento.',
            'cta_label': 'Ver turmas',
            'cta_url': reverse('escola_biblica:turma_list'),
        })

    if igreja:
        scope_label = f'Igreja: {igreja.nome_igreja}'
    else:
        total_igrejas = igrejas_escopo.count()
        scope_label = f'Consolidado EBD ({total_igrejas} igrejas)'

    response = render(request, 'escola_biblica/dashboard.html', {
        'turmas': turmas,
        'alunos': alunos,
        'classes': classes,
        'licoes': licoes,
        'avaliacoes': avaliacoes,
        'total_turmas': turmas.count(),
        'total_alunos': alunos.count(),
        'total_classes': classes.count(),
        'total_licoes': licoes.count(),
        'total_oferta': total_oferta,
        'total_ofertas_mes': total_ofertas_mes,
        'total_ofertas_mes_anterior': total_ofertas_mes_anterior,
        'alunos_evolucao': alunos_evolucao,
        'engajamento_percent': engajamento_percent,
        'evasao': evasao,
        'ranking_classes': ranking_classes,
        'ranking_alunos_pontos': ranking_alunos_pontos,
        'freq_geral': freq_geral,
        'freq_mes_anterior': freq_mes_anterior,
        'ranking_ofertas': ranking_ofertas,
        'alunos_novos': alunos_novos,
        'alunos_novos_mes_anterior': alunos_novos_mes_anterior,
        'transferidos_mes': transferidos_mes,
        'meses': [m.strftime('%m/%Y') for m in meses],
        'faixas_etarias_labels': faixas_etarias_labels,
        'faixas_etarias_counts': faixas_etarias_counts,
        'comparativo_periodo_cards': comparativo_periodo_cards,
        'data_relatorio_dia': data_relatorio_dia,
        'relatorio_instantaneo_turmas': relatorio_instantaneo_turmas,
        'turmas_pendentes_relatorio': turmas_pendentes_relatorio,
        'turmas_parciais_relatorio': turmas_parciais_relatorio,
        'turmas_completas_relatorio': turmas_completas_relatorio,
        'turmas_previstas_semana': turmas_previstas_semana,
        'turmas_com_chamada_semana': turmas_com_chamada_semana,
        'turmas_sem_chamada_semana': turmas_sem_chamada_semana,
        'houve_janela_operacional': houve_janela_operacional,
        'insights_dashboard': insights_dashboard[:3],
        'periodo_anterior_label': f"{data_inicio_periodo_anterior.strftime('%d/%m/%Y')} a {data_fim_periodo_anterior.strftime('%d/%m/%Y')}",
        'periodo_selecionado_label': f"{data_inicio_periodo.strftime('%d/%m/%Y')} a {data_fim_periodo.strftime('%d/%m/%Y')}",
        'periodo_tipo_label': periodo_tipo_label,
        'tipo_periodo': tipo_periodo,
        'anos_letivos': ano_letivo_qs,
        'ano_letivo_selecionado': ano_letivo_selecionado,
        'periodos_disponiveis': periodos_disponiveis,
        'periodo_selecionado': periodo_selecionado,
        'scope_label': scope_label,
        'ebd_config_igreja_link': ebd_config_igreja_link,
        'ebd_config_source': ebd_config_source_info['ebd_config_source'],
        'ebd_config_source_label': ebd_config_source_info['ebd_config_source_label'],
        'ebd_config_source_hint': ebd_config_source_info['ebd_config_source_hint'],
        'ebd_pontos_config': ebd_pontos_config,
    })
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
    from .models import AnoLetivo

    # Verifica se ├® secretaria EBD (acesso total)
    is_secretaria = (
        request.user.is_superuser or 
        request.user.groups.filter(name__in=['Secretaria EBD', 'Superintendente EBD']).exists()
    )

    nome_filtro = request.GET.get('nome', '').strip()
    turma_filtro = request.GET.get('turma', '').strip()
    ativo_filtro = request.GET.get('ativo', '').strip()
    vinculo_filtro = request.GET.get('vinculo', '').strip()
    historico = request.GET.get('historico') == '1'

    ano_atual = date.today().year
    ano_filtro_raw = request.GET.get('ano', '').strip()
    try:
        ano_filtro = int(ano_filtro_raw) if ano_filtro_raw else ano_atual
    except ValueError:
        ano_filtro = ano_atual
    
    if is_secretaria:
        # Secretaria v├¬ todos os alunos
        alunos_list = Aluno.objects.all().order_by('nome')
        alunos_list = filtrar_alunos_ebd(alunos_list, request)
    else:
        # Professor v├¬ apenas alunos de suas turmas
        turmas_professor = get_turmas_professor(request.user)
        alunos_list = filtrar_alunos_ebd(Aluno.objects.filter(turma__in=turmas_professor).order_by('nome').distinct(), request)

    if not historico:
        alunos_list = alunos_list.filter(turma__ano_letivo__ano=ano_filtro)

    if nome_filtro:
        alunos_list = alunos_list.filter(nome__icontains=nome_filtro)

    if turma_filtro:
        alunos_list = alunos_list.filter(turma_id=turma_filtro)

    if ativo_filtro in ('True', 'False'):
        alunos_list = alunos_list.filter(ativo=(ativo_filtro == 'True'))

    if vinculo_filtro == 'vinculado':
        alunos_list = alunos_list.filter(cadastro__pessoa__isnull=False)
    elif vinculo_filtro == 'sem_vinculo':
        alunos_list = alunos_list.filter(cadastro__pessoa__isnull=True)

    if request.method == 'POST' and is_secretaria and request.POST.get('acao') == 'tentar_vinculo_lote':
        cadastro_ids = alunos_list.values_list('cadastro_id', flat=True).distinct()
        cadastros_sem_vinculo = CadastroAluno.objects.filter(
            id__in=cadastro_ids,
            pessoa__isnull=True,
        )
        vinculados = 0
        sem_correspondencia = 0
        vinculados_detalhes = []

        for cadastro in cadastros_sem_vinculo:
            pessoa = cadastro.tentar_vincular_pessoa(force=True)
            if pessoa is None:
                sem_correspondencia += 1
                continue
            cadastro.save()
            vinculados += 1
            nome_cadastro = (cadastro.nome or '').strip() or 'Sem nome'
            nome_pessoa = (pessoa.nome or '').strip()
            if nome_pessoa and nome_pessoa != nome_cadastro:
                vinculados_detalhes.append(f'{nome_cadastro} -> {nome_pessoa}')
            else:
                vinculados_detalhes.append(nome_cadastro)

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

    if not historico:
        alunos_list = colapsar_alunos_por_cadastro(alunos_list)

    alunos_list = alunos_list.select_related('cadastro', 'cadastro__pessoa', 'turma', 'turma__ano_letivo').order_by('nome', '-turma__ano_letivo__ano')

    total_alunos = alunos_list.count()

    turmas_filtro = filtrar_turmas_ebd(Turma.objects.all(), request).order_by('nome')
    if not historico:
        turmas_filtro = turmas_filtro.filter(ano_letivo__ano=ano_filtro)

    anos_letivos = AnoLetivo.objects.order_by('-ano')

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()
    
    paginator = Paginator(alunos_list, 20)  # 20 alunos por p├ígina
    page = request.GET.get('page')
    try:
        alunos = paginator.page(page)
    except PageNotAnInteger:
        alunos = paginator.page(1)
    except EmptyPage:
        alunos = paginator.page(paginator.num_pages)
    return render(request, 'escola_biblica/aluno_list.html', {
        'alunos': alunos,
        'total_alunos': total_alunos,
        'turmas': turmas_filtro,
        'anos_letivos': anos_letivos,
        'ano_filtro': ano_filtro,
        'historico': historico,
        'vinculo_filtro': vinculo_filtro,
        'querystring': querystring,
        'usuario_pode_vincular': is_secretaria,
    })

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
    anos_letivos = AnoLetivo.objects.order_by('-ano')
    ano_letivo_filtro = request.GET.get('ano_letivo')
    periodo_filtro = request.GET.get('periodo')
    igreja_filtro = request.GET.get('igreja_id')
    turma_filtro = request.GET.get('turma', '').strip()
    nome_filtro = request.GET.get('nome', '').strip()
    classe_filtro = request.GET.get('classe', '').strip()
    ano_atual = now.year

    # Sele├º├úo do ano letivo
    if ano_letivo_filtro:
        try:
            # Garante que o valor do ano seja inteiro, mesmo se vier como string com ponto ou milhar
            ano_letivo_str = str(ano_letivo_filtro).replace('.', '').replace(',', '').strip()
            ano_letivo_int = int(ano_letivo_str)
            ano_letivo_selecionado = AnoLetivo.objects.get(ano=ano_letivo_int)
        except (AnoLetivo.DoesNotExist, ValueError):
            ano_letivo_selecionado, _ = AnoLetivo.objects.get_or_create(ano=ano_atual, defaults={'ativo': True})
    else:
        ano_letivo_selecionado, _ = AnoLetivo.objects.get_or_create(ano=ano_atual, defaults={'ativo': True})

    # Sugerir c├│pia de turmas/classes/alunos do ano anterior se o ano letivo acabou de ser criado e n├úo h├í turmas
    sugerir_copiar = False
    ano_anterior = ano_letivo_selecionado.ano - 1 if ano_letivo_selecionado else None
    turmas_ano_atual = Turma.objects.filter(ano_letivo=ano_letivo_selecionado).count() if ano_letivo_selecionado else 0
    turmas_ano_anterior = Turma.objects.filter(ano_letivo__ano=ano_anterior).count() if ano_anterior else 0
    if ano_letivo_selecionado and turmas_ano_atual == 0 and turmas_ano_anterior > 0:
        sugerir_copiar = True

    tipo_periodo = get_ebd_tipo_periodo(request)
    periodos = PeriodoEBD.objects.filter(ano_letivo=ano_letivo_selecionado, tipo=tipo_periodo).order_by('numero')
    periodo_atual = periodos.filter(data_inicio__lte=now, data_fim__gte=now).first()
    periodo_selecionado = None
    if periodo_filtro:
        try:
            periodo_selecionado = periodos.get(numero=periodo_filtro)
        except PeriodoEBD.DoesNotExist:
            periodo_selecionado = periodo_atual or periodos.first()
    else:
        periodo_selecionado = periodo_atual or periodos.first()

    periodo_filtro_chip = None
    if periodo_selecionado and periodo_atual and periodo_selecionado.id != periodo_atual.id:
        periodo_filtro_chip = periodo_selecionado

    mostrar_banner_abrir_periodo = (ano_letivo_selecionado and ano_letivo_selecionado.ano == ano_atual and (not periodos or not periodo_selecionado))

    # Base de turmas do ano letivo (considerando escopo/permissão)
    turmas_base = Turma.objects.filter(ano_letivo=ano_letivo_selecionado)
    if igreja_filtro:
        try:
            turmas_base = turmas_base.filter(igreja_id=int(igreja_filtro))
        except ValueError:
            pass
    
    # Verifica se ├® secretaria EBD (acesso total) ou professor (acesso limitado)
    is_secretaria = usuario_pode_gerenciar_ebd(request.user)
    
    if not is_secretaria:
        # Professores veem apenas suas turmas
        turmas_professor = get_turmas_professor(request.user)
        turmas_base = turmas_base.filter(id__in=turmas_professor.values_list('id', flat=True))

    turma_filtro_id = None
    classe_filtro_id = None
    try:
        turma_filtro_id = int(turma_filtro) if turma_filtro else None
    except ValueError:
        turma_filtro_id = None
    try:
        classe_filtro_id = int(classe_filtro) if classe_filtro else None
    except ValueError:
        classe_filtro_id = None

    turmas_disponiveis = turmas_base
    if classe_filtro_id:
        turmas_disponiveis = turmas_disponiveis.filter(classe_id=classe_filtro_id)
    turmas_disponiveis = turmas_disponiveis.order_by('nome')

    classes_disponiveis = Classe.objects.filter(
        id__in=turmas_base.values_list('classe_id', flat=True)
    )
    if turma_filtro_id:
        classes_disponiveis = classes_disponiveis.filter(
            id__in=turmas_base.filter(id=turma_filtro_id).values_list('classe_id', flat=True)
        )
    classes_disponiveis = classes_disponiveis.distinct().order_by('nome')

    # Filtro unificado de turmas
    turmas_list = turmas_base

    if turma_filtro_id:
        turmas_list = turmas_list.filter(id=turma_filtro_id)
    elif turma_filtro:
        turmas_list = turmas_list.filter(nome__icontains=turma_filtro)
    elif nome_filtro:
        # Compatibilidade com filtro antigo baseado em texto
        turmas_list = turmas_list.filter(nome__icontains=nome_filtro)

    if classe_filtro_id:
        turmas_list = turmas_list.filter(classe_id=classe_filtro_id)
    elif classe_filtro:
        # Compatibilidade com filtro antigo baseado em texto
        turmas_list = turmas_list.filter(classe__nome__icontains=classe_filtro)

    if periodo_selecionado:
        turmas_list = turmas_list.filter(
            licao__data__gte=periodo_selecionado.data_inicio,
            licao__data__lte=periodo_selecionado.data_fim,
        )
    turmas_list = turmas_list.distinct().order_by('nome')
    turmas_list = filtrar_turmas_ebd(turmas_list, request)
    turmas_total = turmas_list.count()

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    paginator = Paginator(turmas_list, 20)
    page = request.GET.get('page')
    try:
        turmas = paginator.page(page)
    except PageNotAnInteger:
        turmas = paginator.page(1)
    except EmptyPage:
        turmas = paginator.page(paginator.num_pages)
    # Banner do per├¡odo EBD atual
    from .models import Licao
    ebd_periodo_atual = periodo_atual or periodo_selecionado
    ebd_aulas_total = None
    ebd_aulas_realizadas = None
    ebd_percentual = None
    ebd_status_label = 'Em andamento'
    ebd_status_bg = '#0d8281'
    ebd_status_color = '#fff'
    ebd_status_tone = 'is-active'
    if ebd_periodo_atual:
        from .utils import gerar_domingos_periodo
        domingos = gerar_domingos_periodo(ebd_periodo_atual.data_inicio, ebd_periodo_atual.data_fim)
        ebd_aulas_total = len(domingos)
        # Aula atual: quantos domingos j├í passaram (incluindo hoje se for domingo)
        ebd_aulas_realizadas = sum(1 for d in domingos if d <= now)
        ebd_percentual = int((ebd_aulas_realizadas / ebd_aulas_total) * 100) if ebd_aulas_total else 0
        if now > ebd_periodo_atual.data_fim:
            ebd_status_label = 'Encerrado'
            ebd_status_bg = '#6c757d'
            ebd_status_tone = 'is-closed'
            if ebd_aulas_total:
                ebd_aulas_realizadas = ebd_aulas_total
                ebd_percentual = 100
        elif now < ebd_periodo_atual.data_inicio:
            ebd_status_label = 'Programado'
            ebd_status_bg = '#0d6efd'
            ebd_status_tone = 'is-planned'
            ebd_aulas_realizadas = 0
            ebd_percentual = 0
    context = {
        'turmas': turmas,
        'turmas_total': turmas_total,
        'anos_letivos': anos_letivos,
        'ano_letivo_selecionado': ano_letivo_selecionado,
        'turmas_disponiveis': turmas_disponiveis,
        'classes_disponiveis': classes_disponiveis,
        'turma_filtro': turma_filtro,
        'classe_filtro': classe_filtro,
        'periodos': periodos,
        'periodo_selecionado': periodo_selecionado,
        'periodo_filtro_chip': periodo_filtro_chip,
        'tipo_periodo': tipo_periodo,
        'now': now,
        'request': request,
        'mostrar_banner_abrir_periodo': mostrar_banner_abrir_periodo,
        'sugerir_copiar': sugerir_copiar,
        'ebd_periodo_atual': ebd_periodo_atual,
        'ebd_aulas_total': ebd_aulas_total,
        'ebd_aulas_realizadas': ebd_aulas_realizadas,
        'ebd_percentual': ebd_percentual,
        'ebd_status_label': ebd_status_label,
        'ebd_status_bg': ebd_status_bg,
        'ebd_status_color': ebd_status_color,
        'ebd_status_tone': ebd_status_tone,
        'ebd_config_source': ebd_config_source_info['ebd_config_source'],
        'ebd_config_source_label': ebd_config_source_info['ebd_config_source_label'],
        'ebd_config_source_hint': ebd_config_source_info['ebd_config_source_hint'],
        'querystring': querystring,
    }
    return render(request, 'escola_biblica/turma_list.html', context)

# --- EDITAR TURMA ---
from .forms import TurmaForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

@page_access_required('escola_biblica')
@verificar_assinatura_valida
def turma_edit(request, pk):
    turma = get_object_or_404_ebd(Turma.objects.all(), request, 'membros__igreja', pk=pk)
    if request.method == 'POST':
        form = TurmaForm(request.POST, instance=turma, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma atualizada com sucesso!')
            return redirect('escola_biblica:turma_list')
    else:
        form = TurmaForm(instance=turma, request=request)
    return render(request, 'escola_biblica/turma_form.html', {'form': form, 'turma': turma})

# --- EXCLUIR TURMA ---
@login_required
@superintendente_required
@verificar_assinatura_valida
def turma_delete(request, pk):
    turma = get_object_or_404_ebd(Turma.objects.all(), request, 'membros__igreja', pk=pk)
    if request.method == 'POST':
        turma.delete()
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
    paginator = Paginator(frequencias_list, 30)
    page = request.GET.get('page')
    try:
        frequencias = paginator.page(page)
    except PageNotAnInteger:
        frequencias = paginator.page(1)
    except EmptyPage:
        frequencias = paginator.page(paginator.num_pages)
    return render(request, 'escola_biblica/frequencia_list.html', {'frequencias': frequencias})


# --- NOVA VIEW: Gera├º├úo autom├ítica de per├¡odos e li├º├Áes em lote ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def gerar_cronograma(request):
    from django.contrib import messages
    from datetime import date
    from .models import Licao
    ano_atual = date.today().year
    turmas = filtrar_queryset_ebd(Turma.objects.filter(ano_letivo__ano=ano_atual, ano_letivo__ativo=True), request, 'membros__igreja')
    turma_selecionada = None
    tipo_periodo = get_ebd_tipo_periodo(request)
    if request.method == 'POST':
        form = GerarCronogramaForm(request.POST, request=request)
        if form.is_valid():
            turma_id = form.cleaned_data.get('turma')
            turma_selecionada = Turma.objects.filter(id=turma_id.id if hasattr(turma_id, 'id') else turma_id).first()
            material = form.cleaned_data.get('material', '')
            observacoes = form.cleaned_data.get('observacoes', '')
            horario = form.cleaned_data.get('horario', None)
            status = form.cleaned_data.get('status', 'ativa')
            # Gera li├º├Áes para todos os per├¡odos e domingos do ano
            licoes = gerar_licoes_periodos(
                ano=ano_atual,
                tipo_periodo=tipo_periodo,
                turmas=[turma_selecionada] if turma_selecionada else turmas,
                material=material,
                observacoes=observacoes,
                horario=horario,
                status=status
            )
            # Salva as li├º├Áes no banco
            from .models import Licao
            criadas = 0
            for licao_data in licoes:
                # Evita duplicidade: s├│ cria se n├úo existir para turma/data/tema
                if not Licao.objects.filter(turma=licao_data['turma'], data=licao_data['data'], tema=licao_data['tema']).exists():
                    Licao.objects.create(
                        turma=licao_data['turma'],
                        data=licao_data['data'],
                        tema=licao_data['tema'],
                        material=licao_data['material'],
                        observacoes=licao_data['observacoes'],
                        horario=licao_data['horario'],
                        status=licao_data['status'],
                        professor=licao_data['professor']
                    )
                    criadas += 1
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
        form = GerarCronogramaForm(request=request)
        turma_id = request.GET.get('turma')
        if turma_id:
            turma_selecionada = Turma.objects.filter(id=turma_id).first()
    aulas = Licao.objects.filter(turma=turma_selecionada).order_by('-data') if turma_selecionada else Licao.objects.none()
    aulas_count = aulas.count()
    return render(request, 'escola_biblica/gerar_cronograma_form.html', {
        'form': form,
        'turmas': turmas,
        'aulas': aulas,
        'aulas_count': aulas_count,
        'turma_selecionada': turma_selecionada,
        'tipo_periodo': tipo_periodo,
        'ano_atual': ano_atual,
    })
