# --- RELATÓRIO GERAL DO DIA DA EBD ---
import logging
from django.db.models import Count, Sum, Q, OuterRef, Subquery
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from core.decorators import secretaria_ebd_required, user_passes_test_or_403, page_access_required
from django.core.exceptions import PermissionDenied, ValidationError
from core.utils import get_igrejas_permitidas, get_request_scoped_churches
from contas.constants import SECRETARIA_EBD, user_has_permission_level_or_higher
from secretaria.models import MembroCargo

logger = logging.getLogger(__name__)

# --- FUNÇÕES HELPER DE PERMISSÕES ---
def pode_acessar_chamada_turma(user, turma):
    """
    Verifica se usuário pode acessar a chamada de presença da turma.
    
    Permite acesso se:
    - É superuser
    - Está no grupo Secretaria EBD ou Superintendente EBD
    - É professor da turma específica
    """
    # Superuser sempre pode
    if user.is_superuser:
        return True
    
    # Secretaria/Superintendente EBD podem acessar todas as turmas
    if user_has_permission_level_or_higher(user, SECRETARIA_EBD):
        return True
    
    # Verifica se é professor da turma
    try:
        # Acessa o membro via related_name 'membro_secretaria' (Pessoa->User)
        membro = getattr(user, 'membro_secretaria', None)
        if membro:
            # Verifica se está nos membros da turma
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
    Retorna turmas onde o usuário é professor.
    """
    from .models import Turma
    
    try:
        # Acessa o membro via related_name 'membro_secretaria' (Pessoa->User)
        membro = getattr(user, 'membro_secretaria', None)
        if membro:
            # Busca turmas onde o membro está cadastrado
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
    Verifica se usuário pode ver detalhes do aluno.
    
    Permite se:
    - É superuser
    - É secretaria/superintendente EBD
    - É professor da turma do aluno
    """
    if user.is_superuser:
        return True
    
    # Secretaria/Superintendente EBD podem ver todos
    if user_has_permission_level_or_higher(user, SECRETARIA_EBD):
        return True
    
    # Verifica se é professor da turma do aluno
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


def consolidar_alunos_por_cadastro_periodo(queryset, inicio=None, fim=None, turma_id=None, classe_id=None):
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
def relatorio_ebd_dia(request):
    from .models import Turma, Frequencia, OfertaClasse, AnoLetivo, Licao
    from decimal import Decimal
    
    # Se data não for fornecida, busca a data da lição mais recente
    data_str = request.GET.get('data')
    if data_str:
        data = parse_date(data_str)
    else:
        # Busca a data da lição mais recente
        ultima_licao = filtrar_queryset_ebd(Licao.objects.all(), request, 'turma__membros__igreja').order_by('-data').first()
        data = ultima_licao.data if ultima_licao else timezone.now().date()
    
    # Filtra turmas apenas do ano letivo correspondente à data selecionada
    # E que tenham lições cadastradas na data selecionada
    ano_da_data = data.year
    ano_letivo = AnoLetivo.objects.filter(ano=ano_da_data).first()
    if ano_letivo:
        turmas_com_licao = filtrar_queryset_ebd(Licao.objects.filter(data=data), request, 'turma__membros__igreja').values_list('turma_id', flat=True)
        turmas = filtrar_queryset_ebd(Turma.objects.filter(ano_letivo=ano_letivo, id__in=turmas_com_licao), request, 'membros__igreja')
    else:
        turmas = Turma.objects.none()
    
    # Busca todas as datas com lições do ano letivo para o campo de seleção
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
# --- CHAMADA DE PRESENÇA POR TURMA ---
from django.shortcuts import render, get_object_or_404, redirect
from .models import Turma, Aluno, Licao, PeriodoEBD, Frequencia, OfertaClasse
from .forms import ChamadaPresencaFormSet
from django.utils import timezone
from django.contrib import messages

@login_required
@page_access_required('escola_biblica_professor')
def chamada_presenca(request, turma_id):
    """
    Chamada de presença da turma.
    
    Pode ser acessada por:
    - Secretaria EBD / Superintendente EBD (todas as turmas)
    - Professor da turma (apenas sua turma)
    """
    turma = get_object_or_404(filtrar_turmas_ebd(Turma.objects.all(), request), pk=turma_id)
    
    # Verifica permissão (secretaria EBD ou professor da turma)
    if not pode_acessar_chamada_turma(request.user, turma):
        raise PermissionDenied("Você não tem permissão para acessar a chamada desta turma.")
    # --- Busca a turma pelo ID e obtém alunos ativos ---
    alunos = turma.alunos.filter(ativo=True).order_by('nome')
    ano_letivo = turma.ano_letivo
    tipo_periodo = 'trimestre'
    # Descobrir período vigente

    # --- Descobre o período vigente (trimestre) para a turma ---
    periodo = PeriodoEBD.objects.filter(ano_letivo=ano_letivo, tipo=tipo_periodo).order_by('numero').first()
    datas_validas = []
    dia_ebd = 6  # domingo
    if periodo:
        data_atual = periodo.data_inicio
        while data_atual <= periodo.data_fim:
            if data_atual.weekday() == dia_ebd:
                datas_validas.append(data_atual)
            data_atual += timezone.timedelta(days=1)

    # --- Assistente: verifica se há datas sem lição cadastrada ---
    # Assistente de verificação de lições do trimestre
    licoes_faltantes = []
    for d in datas_validas:
        if not Licao.objects.filter(turma=turma, data=d).exists():
            licoes_faltantes.append(d)
    if licoes_faltantes:
        msg = f"Atenção: Existem {len(licoes_faltantes)} datas do trimestre sem lição cadastrada para esta turma. "
        url_cronograma = redirect('escola_biblica:gerar_cronograma_wizard').url
        msg += f"<a href='{url_cronograma}?turma_id={turma.id}' class='btn btn-sm btn-warning ms-2'>Criar lições em lote</a>"
        messages.warning(request, msg)

    # --- Repete busca da turma e alunos para garantir contexto atualizado ---
    turma = get_object_or_404(filtrar_turmas_ebd(Turma.objects.all(), request), pk=turma_id)
    alunos = turma.alunos.filter(ativo=True).order_by('nome')
    ano_letivo = turma.ano_letivo
    tipo_periodo = 'trimestre'

    # --- Descobre novamente o período vigente (trimestre) ---
    # Descobrir período vigente
    periodo = PeriodoEBD.objects.filter(ano_letivo=ano_letivo, tipo=tipo_periodo).order_by('numero').first()
    datas_validas = []
    dia_ebd = 6  # domingo
    if periodo:
        data_atual = periodo.data_inicio
        while data_atual <= periodo.data_fim:
            if data_atual.weekday() == dia_ebd:
                datas_validas.append(data_atual)

    # --- Seleção da data da chamada (automática ou manual) ---
            data_atual += timezone.timedelta(days=1)
    # Data selecionada
    data = request.POST.get('data') or request.GET.get('data')
    if not data or not any(str(d) == str(data) for d in datas_validas):
        hoje = timezone.now().date()
        data_hoje_ou_proxima = None
        for d in datas_validas:
            if d >= hoje:
                data_hoje_ou_proxima = d
                break
        if not data_hoje_ou_proxima and datas_validas:

    # --- Busca a lição cadastrada para a data selecionada ---
            data_hoje_ou_proxima = datas_validas[-1]

    # --- Busca valor da oferta da turma para a data ---
        data = data_hoje_ou_proxima.isoformat() if data_hoje_ou_proxima else timezone.now().date().isoformat()
    licao_do_dia = Licao.objects.filter(turma=turma, data=data).first()
    # Valor da oferta
    valor_oferta_atual = ''
    classe = turma.classe if hasattr(turma, 'classe') else None
    if classe:

    # --- Formulário de chamada de presença ---
        oferta_obj = oferta_queryset_por_turma_data(turma, data).first()
        if oferta_obj and oferta_obj.valor is not None:
            valor_oferta_atual = f"{oferta_obj.valor:.2f}"  # Mantém ponto para input type='number'
    # Formset de chamada
    if alunos.exists():
        if request.method == 'POST' and not request.POST.get('troca_data'):
            # --- Validação: impede salvar chamada se não houver lição cadastrada para a data ---
            licao_do_dia = Licao.objects.filter(turma=turma, data=data).first()
            if not licao_do_dia:
                messages.error(request, 'Não é possível registrar a chamada: não existe lição cadastrada para esta data. Cadastre a lição antes de registrar a presença.')
                return redirect(request.path + f'?data={data}')
            formset = ChamadaPresencaFormSet(request.POST)
            if formset.is_valid():
                erro_validacao = False
                for form in formset:
                    aluno_id = form.cleaned_data['aluno_id']
                    presente = form.cleaned_data.get('presente', False)
                    trouxe_biblia = form.cleaned_data.get('trouxe_biblia', False)
                    trouxe_revista = form.cleaned_data.get('trouxe_revista', False)
                    trouxe_visitante = form.cleaned_data.get('trouxe_visitante', False)
                    trouxe_oferta = form.cleaned_data.get('trouxe_oferta', False)
                    freq, created = Frequencia.objects.get_or_create(
                        aluno_id=aluno_id,
                        data=data,
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
                    try:
                        freq.full_clean()
                        freq.save()
                    except Exception as e:
                        erro_validacao = True
                        messages.error(request, f'Erro ao registrar chamada para {freq.aluno.nome}: {e}')
                # Salvar/atualizar valor da oferta
                valor_oferta = request.POST.get('valor_oferta')
                if valor_oferta is not None and classe:
                    try:
                        valor_str = str(valor_oferta).replace(',', '.').strip()
                        valor_float = float(valor_str) if valor_str else 0.0
                        oferta_obj, created = OfertaClasse.objects.get_or_create(
                            turma=turma,
                            data=data,
                            defaults={'classe': classe, 'valor': valor_float}
                        )
                        if not created:
                            oferta_obj.valor = valor_float
                            oferta_obj.save()
                    except Exception as e:
                        messages.error(request, f'Erro ao registrar valor da oferta: {e}')
                if not erro_validacao:
                    messages.success(request, f'Chamada de presença registrada para {turma} em {data}.')
                    return redirect('escola_biblica:turma_list')
            else:
                messages.error(request, 'Erro ao registrar chamada de presença. Verifique os dados e tente novamente.')
        else:
            initial = [
                {
                    'aluno_id': aluno.id,
                    'nome': aluno.nome,
                    'presente': Frequencia.objects.filter(aluno=aluno, data=data, presente=True).exists(),
                    'trouxe_biblia': Frequencia.objects.filter(aluno=aluno, data=data, trouxe_biblia=True).exists(),
                    'trouxe_revista': Frequencia.objects.filter(aluno=aluno, data=data, trouxe_revista=True).exists(),
                    'trouxe_visitante': Frequencia.objects.filter(aluno=aluno, data=data, trouxe_visitante=True).exists(),
                    'trouxe_oferta': Frequencia.objects.filter(aluno=aluno, data=data, trouxe_oferta=True).exists(),
                }
                for aluno in alunos
            ]
            formset = ChamadaPresencaFormSet(initial=initial)
    else:
        formset = None
    return render(request, 'escola_biblica/chamada_presenca.html', {
        'turma': turma,
        'formset': formset,

    # --- Renderiza o template passando todos os dados necessários ---
        'data': data,
        'datas_validas': datas_validas,
        'valor_oferta_atual': valor_oferta_atual,
        'licao_do_dia': licao_do_dia,
    })
# --- IMPORTS NECESSÁRIOS PARA DECORADORES ---
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from core.decorators import secretaria_ebd_required
# --- WIZARD: Geração de lições em etapas ---
@page_access_required('escola_biblica')
@csrf_exempt
def gerar_cronograma_wizard(request):
    from .models import AnoLetivo, PeriodoEBD, Turma, Licao
    from datetime import date
    from django.utils import timezone
    etapa = int(request.POST.get('etapa', request.GET.get('etapa', 1)))
    hoje = timezone.now().date()
    ano_atual = hoje.year
    # Ano letivo: apenas atual e próximo (se existir)
    anos_letivos = AnoLetivo.objects.filter(ano__gte=ano_atual).order_by('ano')
    # Turmas: únicas, ordem alfabética
    turmas = filtrar_queryset_ebd(Turma.objects.filter(ano_letivo__ano__gte=ano_atual).order_by('nome').distinct(), request, 'membros__igreja')
    # Períodos: só do ano letivo selecionado, abertos/futuros
    periodo_ano_raw = request.POST.get('ano_letivo', ano_atual)
    periodo_ano = int(str(periodo_ano_raw).replace('.', '').replace(' ', ''))
    periodos = PeriodoEBD.objects.filter(ano_letivo__ano=periodo_ano, data_fim__gte=hoje).order_by('numero')
    context = {'etapa': etapa}

    # Etapa 1: Seleção
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
            # Buscar horário padrão da configuração do sistema
            horario_inicial = ''
            perfil = getattr(request.user, 'perfil', None)
            if perfil and hasattr(perfil, 'ministerio'):
                from configuracao.models import ConfiguracaoSistema
                config = ConfiguracaoSistema.objects.filter(ministerio=perfil.ministerio).first()
                if config and config.ebd_horario:
                    if isinstance(config.ebd_horario, str):
                        horario_inicial = config.ebd_horario[:5]
                    else:
                        horario_inicial = config.ebd_horario.strftime('%H:%M')
            # Inicializa periodo_nome corretamente
            periodo_obj = PeriodoEBD.objects.filter(ano_letivo__ano=ano_letivo, numero=periodo).first()
            periodo_nome = f"{periodo_obj.get_tipo_display()} {periodo_obj.numero}" if periodo_obj else "Período"
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
                'nome_licao_padrao': request.POST.get('nome_licao_padrao', f'Lição {{n}} - {periodo_nome}'),
            })
            return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
        return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)

    # Etapa 2: Configuração
    if etapa == 2:
        ano_letivo_raw = request.POST.get('ano_letivo')
        ano_letivo = int(str(ano_letivo_raw).replace('.', '').replace(' ', ''))
        periodo = int(request.POST.get('periodo'))
        turmas_ids = request.POST.getlist('turmas')
        # Buscar horário padrão da configuração do sistema
        horario_inicial = ''
        perfil = getattr(request.user, 'perfil', None)
        if perfil and hasattr(perfil, 'ministerio'):
            from configuracao.models import ConfiguracaoSistema
            config = ConfiguracaoSistema.objects.filter(ministerio=perfil.ministerio).first()
            if config and config.ebd_horario:
                # Garante que o valor é string no formato HH:MM
                if isinstance(config.ebd_horario, str):
                    horario_inicial = config.ebd_horario[:5]
                else:
                    horario_inicial = config.ebd_horario.strftime('%H:%M')
        # Padrão de nome sugerido
        periodo_obj = PeriodoEBD.objects.filter(ano_letivo__ano=ano_letivo, numero=periodo).first()
        periodo_nome = f"{periodo_obj.get_tipo_display()} {periodo_obj.numero}" if periodo_obj else "Período"
        nome_licao_padrao = request.POST.get('nome_licao_padrao', f'Lição {{n}} - {periodo_nome}')
        # Se já veio do POST, prioriza o valor enviado, senão usa o padrão do sistema
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
                erro_wizard = 'Selecione ao menos uma turma e um período válido para continuar.'
                context['erro_wizard'] = erro_wizard
                return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
            context['etapa'] = 3
            # Pré-visualização das lições
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
            # Garante que o horário padrão seja preenchido ao voltar
            if not horario:
                horario = horario_inicial
            context['etapa'] = 1
            context['anos_letivos'] = anos_letivos
            context['periodos'] = periodos
            context['turmas'] = turmas
            context['horario'] = horario
            return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)
        return render(request, 'escola_biblica/gerar_cronograma_wizard.html', context)

    # Etapa 3: Confirmação e geração
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
        periodo_nome = f"{periodo_obj.get_tipo_display()} {periodo_obj.numero}" if periodo_obj else "Período"
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
            resultado_msg = f'{licoes_geradas} lições geradas com sucesso!' if licoes_geradas else 'Nenhuma nova lição foi gerada (já existiam para este período/turma).'
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
        # Pré-visualização
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

# --- SELEÇÃO DE DADOS PARA CÓPIA DO PERÍODO ANTERIOR ---
@page_access_required('escola_biblica')
@require_http_methods(["GET", "POST"])
def copiar_periodo_selecao(request):
    from .models import AnoLetivo, Turma, Classe, Aluno
    ano_destino = request.GET.get('ano_destino') or request.POST.get('ano_destino')
    try:
        ano_destino_int = int(float(str(ano_destino).replace('.', '')))
    except Exception:
        messages.error(request, 'Ano destino inválido.')
        return redirect('escola_biblica:turma_list')
    ano_origem = ano_destino_int - 1
    ano_letivo_origem = AnoLetivo.objects.filter(ano=ano_origem).first()
    if not ano_letivo_origem:
        messages.error(request, f'Não existe ano letivo anterior ({ano_origem}) para copiar.')
        return redirect('escola_biblica:turma_list')
    turmas = filtrar_queryset_ebd(Turma.objects.filter(ano_letivo=ano_letivo_origem), request, 'membros__igreja')
    classes = Classe.objects.filter(turma__in=turmas).distinct()
    alunos = filtrar_queryset_ebd(Aluno.objects.filter(turma__ano_letivo=ano_letivo_origem, ativo=True), request, 'turma__membros__igreja')
    if request.method == 'POST':
        turmas_ids = request.POST.getlist('turmas_selecionadas')
        classes_ids = request.POST.getlist('classes_selecionadas')
        alunos_ids = request.POST.getlist('alunos_selecionados')
        ano_letivo_dest, _ = AnoLetivo.objects.get_or_create(ano=ano_destino_int, defaults={'ativo': True})

        # Copiar classes (só cria se não existir)
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
                # Evita duplicidade: só matricula se não houver aluno com mesmo nome e data_nascimento na turma_dest
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
            messages.warning(request, 'Nenhum dado novo foi criado. Todos os dados selecionados já existiam para o ano/período de destino.')
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
        messages.error(request, 'Ano destino inválido.')
        return redirect('escola_biblica:turma_list')
    ano_letivo_dest, _ = AnoLetivo.objects.get_or_create(ano=ano_destino_int, defaults={'ativo': True})
    ano_origem = ano_letivo_dest.ano - 1
    ano_letivo_origem = AnoLetivo.objects.filter(ano=ano_origem).first()
    if not ano_letivo_origem:
        messages.error(request, f'Não existe ano letivo anterior ({ano_origem}) para copiar.')
        return redirect('escola_biblica:turma_list')
    # Copiar classes se não existirem
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

# --- ABRIR NOVO PERÍODO EBD ---
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
        messages.error(request, 'Ano letivo e tipo de período são obrigatórios.')
        return redirect('escola_biblica:turma_list')
    try:
        ano_letivo_int = int(float(str(ano_letivo).replace('.', '')))
    except ValueError:
        messages.error(request, f'Ano letivo inválido: {ano_letivo}')
        return redirect('escola_biblica:turma_list')
    ano_letivo_obj, _ = AnoLetivo.objects.get_or_create(ano=ano_letivo_int, defaults={'ativo': True})
    # Descobre períodos já existentes
    periodos_existentes = PeriodoEBD.objects.filter(ano_letivo=ano_letivo_obj, tipo=tipo_periodo).order_by('numero')
    # Gera todos os períodos possíveis para o ano
    periodos_gerados = gerar_periodos_ebd(ano_letivo_int, tipo_periodo)
    # Lógica: cria só o próximo período (ou o primeiro do ano, se nenhum existir)
    if not periodos_existentes.exists():
        proximo = periodos_gerados[0]
        PeriodoEBD.objects.create(
            ano_letivo=ano_letivo_obj,
            numero=proximo['numero'],
            tipo=tipo_periodo,
            data_inicio=proximo['data_inicio'],
            data_fim=proximo['data_fim']
        )
        messages.success(request, f'Período {proximo["numero"]} criado para {ano_letivo}/{tipo_periodo}.')
        # Redireciona para seleção de cópia
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
            messages.success(request, f'Próximo período ({proximo["numero"]}) criado para {ano_letivo}/{tipo_periodo}.')
            return redirect(f'/escola_biblica/copiar_periodo_selecao/?ano_destino={ano_letivo_int}')
        else:
            # Todos os períodos do ano já existem, criar novo ano e 1º período do próximo ano
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
            messages.success(request, f'Ano {proximo_ano} criado com o 1º período ({primeiro_prox_ano["numero"]}) de {tipo_periodo}.')
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
from django.db import transaction
from .models import Licao, Aluno, CadastroAluno, Turma, Frequencia, Classe, Avaliacao, OfertaClasse, TransferenciaAluno, Departamento, DEPARTAMENTOS_SUGERIDOS
from .forms import LicaoForm, AlunoForm, TurmaForm, FrequenciaForm, ClasseForm, AvaliacaoForm, OfertaClasseForm, TransferenciaAlunoForm, ChamadaPresencaFormSet, DepartamentoForm, GerarCronogramaForm
from secretaria.models import Pessoa


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

# --- PERFIL DO ALUNO E HISTÓRICO DE TRANSFERÊNCIAS ---


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
    
    # Verifica permissão
    if not pode_ver_aluno(request.user, aluno):
        raise PermissionDenied("Você não tem permissão para ver detalhes deste aluno.")
    
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
        messages.warning(request, 'Aluno não encontrado no escopo atual. Abra o histórico pela lista de alunos.')
        return redirect('escola_biblica:aluno_list')

    if not pode_ver_aluno(request.user, aluno):
        raise PermissionDenied("Você não tem permissão para ver detalhes deste aluno.")

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
            messages.success(request, 'Vínculo com a Secretaria removido com sucesso.')
            return redirect('escola_biblica:aluno_vinculo_secretaria', pk=aluno.pk)

        pessoa_id = request.POST.get('pessoa_id')
        if not pessoa_id:
            messages.error(request, 'Selecione uma pessoa da Secretaria para vincular.')
        else:
            pessoa = get_object_or_404(pessoas_base, pk=pessoa_id)
            cadastro.pessoa = pessoa
            cadastro.save()
            messages.success(request, f'Aluno vinculado com sucesso à pessoa {pessoa.nome}.')
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
        raise PermissionDenied('Você não tem permissão para gerenciar vínculos em lote.')

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
            messages.success(request, f'Vínculos aplicados: {exibicao}{sufixo}.')
        else:
            messages.info(request, 'Nenhum vínculo foi selecionado para aplicar.')

        querystring_pos_post = request.GET.urlencode()
        redirect_url = reverse('escola_biblica:aluno_vinculo_secretaria_lote')
        if querystring_pos_post:
            redirect_url = f'{redirect_url}?{querystring_pos_post}'
        return redirect(redirect_url)

    return render(request, 'escola_biblica/aluno_vinculo_secretaria_lote.html', {
        'linhas': linhas,
        'total_cadastros': len(cadastros),
    })

# --- TRANSFERÊNCIA DE ALUNO ENTRE TURMAS/CLASSES ---
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
                messages.success(request, f'Transferência realizada com sucesso para {transferencia.turma_destino}!')
                return redirect('escola_biblica:aluno_detail', pk=matricula_destino.pk)
    else:
        form = TransferenciaAlunoForm(request=request)
    return render(request, 'escola_biblica/transferir_aluno.html', {
        'form': form,
        'aluno': aluno,
        'turma_origem': turma_origem,
    })



# --- RELATÓRIO DE FREQUÊNCIA DETALHADO ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def relatorio_frequencia(request):
    turmas = filtrar_turmas_ebd(Turma.objects.all(), request)
    classes = filtrar_classes_ebd(Classe.objects.all(), request)
    alunos = filtrar_alunos_ebd(Aluno.objects.select_related('cadastro', 'turma', 'turma__classe').all(), request)
    turma_id = request.GET.get('turma')
    classe_id = request.GET.get('classe')
    inicio = parse_date(request.GET.get('inicio') or '')
    fim = parse_date(request.GET.get('fim') or '')
    alunos = consolidar_alunos_por_cadastro_periodo(alunos, inicio=inicio, fim=fim, turma_id=turma_id, classe_id=classe_id)
    # Exportação CSV
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="relatorio_frequencia.csv"'
        writer = csv.writer(response)
        writer.writerow(['Cadastro', 'Turma de Referência', 'Classe', 'Presenças', 'Total Aulas', 'Frequência (%)'])
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
    })

# --- LISTAGEM DINÂMICA DE CARGOS/FUNÇÕES ---
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

# --- GRÁFICOS DE EVOLUÇÃO ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def graficos_evolucao(request):
    hoje = timezone.now().date()
    meses = [(hoje.replace(day=1) - timezone.timedelta(days=30*i)).replace(day=1) for i in range(11, -1, -1)]
    meses_fmt = [m.strftime('%m/%Y') for m in meses]

    alunos_evolucao = defaultdict(lambda: [0]*12)
    for idx, mes in enumerate(meses):
        prox_mes = (mes + timezone.timedelta(days=32)).replace(day=1)
        for turma in filtrar_queryset_ebd(Turma.objects.filter(ano_letivo__ativo=True, classe__isnull=False), request, 'membros__igreja'):
            classe_nome = turma.classe.nome
            count = Aluno.objects.filter(turma=turma, data_matricula__lte=prox_mes, data_saida__isnull=True).count()
            alunos_evolucao[classe_nome][idx] += count

    ofertas_evolucao = defaultdict(lambda: [0]*12)
    for idx, mes in enumerate(meses):
        prox_mes = (mes + timezone.timedelta(days=32)).replace(day=1)
        for classe in filtrar_queryset_ebd(Classe.objects.all(), request, 'turma__membros__igreja'):
            total = filtrar_queryset_ebd(OfertaClasse.objects.filter(classe=classe, data__gte=mes, data__lt=prox_mes), request, 'classe__turma__membros__igreja').aggregate(s=Sum('valor'))['s'] or 0
            ofertas_evolucao[classe.nome][idx] = float(total)

    context = {
        'meses': json.dumps(meses_fmt),
        'alunos_evolucao': json.dumps(alunos_evolucao),
        'ofertas_evolucao': json.dumps(ofertas_evolucao),
    }
    return render(request, 'escola_biblica/graficos_evolucao.html', context)

# --- DASHBOARD GRÁFICOS ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def dashboard_graficos(request):
    departamentos = dict(Classe.DEPARTAMENTO_CHOICES)
    igrejas_escopo = get_ebd_scope_churches(request)
    alunos_por_departamento = {d: 0 for d in departamentos.values()}
    for dep_key, dep_label in departamentos.items():
        alunos_por_departamento[dep_label] = filtrar_queryset_ebd(Aluno.objects.filter(turma__classe__departamento=dep_key), request, 'turma__membros__igreja').count()

    ofertas_por_departamento = {d: 0 for d in departamentos.values()}
    for dep_key, dep_label in departamentos.items():
        ofertas_por_departamento[dep_label] = OfertaClasse.objects.filter(
            Q(turma__classe__departamento=dep_key) | Q(turma__isnull=True, classe__departamento=dep_key)
        ).filter(
            Q(turma__igreja__in=igrejas_escopo) |
            Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas_escopo) |
            Q(turma__isnull=True, classe__igreja__in=igrejas_escopo) |
            Q(turma__isnull=True, classe__igreja__isnull=True, classe__turma__membros__igreja__in=igrejas_escopo)
        ).distinct().aggregate(total=Sum('valor'))['total'] or 0

    ofertas_por_classe = {}
    for classe in filtrar_queryset_ebd(Classe.objects.all(), request, 'turma__membros__igreja'):
        ofertas_por_classe[classe.nome] = OfertaClasse.objects.filter(
            Q(turma__classe=classe) | Q(turma__isnull=True, classe=classe)
        ).filter(
            Q(turma__igreja__in=igrejas_escopo) |
            Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas_escopo) |
            Q(turma__isnull=True, classe__igreja__in=igrejas_escopo) |
            Q(turma__isnull=True, classe__igreja__isnull=True, classe__turma__membros__igreja__in=igrejas_escopo)
        ).distinct().aggregate(total=Sum('valor'))['total'] or 0

    alunos_por_classe = {}
    for classe in filtrar_queryset_ebd(Classe.objects.all(), request, 'turma__membros__igreja'):
        alunos_por_classe[classe.nome] = filtrar_queryset_ebd(Aluno.objects.filter(turma__classe=classe), request, 'turma__membros__igreja').count()

    context = {
        'alunos_por_departamento': json.dumps(alunos_por_departamento),
        'ofertas_por_departamento': json.dumps(ofertas_por_departamento),
        'ofertas_por_classe': json.dumps(ofertas_por_classe),
        'alunos_por_classe': json.dumps(alunos_por_classe),
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
            form.save()
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
            form.save()
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
        oferta.delete()
        messages.success(request, 'Oferta excluída com sucesso!')
        return redirect('escola_biblica:oferta_classe_list')
    return render(request, 'escola_biblica/oferta_classe_confirm_delete.html', {'oferta': oferta})

# --- RELATÓRIO DE ALUNOS ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def relatorio_alunos(request):
    turmas = filtrar_turmas_ebd(Turma.objects.all(), request)
    classes = filtrar_classes_ebd(Classe.objects.all(), request)
    alunos = filtrar_alunos_ebd(Aluno.objects.select_related('cadastro', 'turma', 'turma__classe').all(), request)
    turma_id = request.GET.get('turma')
    classe_id = request.GET.get('classe')
    inicio = parse_date(request.GET.get('inicio') or '')
    fim = parse_date(request.GET.get('fim') or '')
    alunos = consolidar_alunos_por_cadastro_periodo(alunos, inicio=inicio, fim=fim, turma_id=turma_id, classe_id=classe_id)
    return render(request, 'escola_biblica/relatorio_alunos.html', {
        'turmas': turmas,
        'classes': classes,
        'alunos': alunos,
    })
# --- LICOES ---
 
 # --- AVALIAÇÕES ---
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
            messages.success(request, 'Avaliação cadastrada com sucesso!')
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
            messages.success(request, 'Avaliação atualizada com sucesso!')
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
        messages.success(request, 'Avaliação excluída com sucesso!')
        return redirect('escola_biblica:avaliacao_list')
    return render(request, 'escola_biblica/avaliacao_confirm_delete.html', {'avaliacao': avaliacao})
@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def licao_list(request):
    from .models import PeriodoEBD, AnoLetivo
    from django.utils import timezone
    hoje = timezone.now().date()
    
    # Buscar lições com escopo correto
    licoes_scope = filtrar_queryset_ebd(Licao.objects.all(), request, 'turma__membros__igreja')
    
    # Buscar períodos que têm lições no escopo do usuário (evitar vazamento de dados)
    periodos_ids = licoes_scope.values_list('data__year', flat=True).distinct()
    periodos = PeriodoEBD.objects.select_related('ano_letivo').filter(
        data_inicio__year__in=periodos_ids
    ).order_by('-ano_letivo__ano', '-numero')
    
    # Identificar período atual
    periodo_atual = periodos.filter(data_inicio__lte=hoje, data_fim__gte=hoje).first()
    
    # Filtro por GET
    periodo_id = request.GET.get('periodo')
    if periodo_id:
        periodo_selecionado = periodos.filter(id=periodo_id).first()
    else:
        periodo_selecionado = periodo_atual
    
    licoes = licoes_scope
    if periodo_selecionado:
        licoes = licoes.filter(data__gte=periodo_selecionado.data_inicio, data__lte=periodo_selecionado.data_fim)
    
    # Buscar turmas para o filtro (apenas do escopo do usuário)
    from .models import Turma
    turma_nomes = filtrar_queryset_ebd(Turma.objects.all(), request, 'membros__igreja').values_list('nome', flat=True).distinct().order_by('nome')
    turma_nome = request.GET.get('turma')
    if turma_nome:
        licoes = licoes.filter(turma__nome=turma_nome)

    # Filtro de professor (apenas do escopo do usuário)
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
            messages.success(request, 'Lição cadastrada com sucesso!')
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
            messages.success(request, 'Lição atualizada com sucesso!')
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
        messages.success(request, 'Lição excluída com sucesso!')
        return redirect('escola_biblica:licao_list')
# --- CLASSES ---
# --- CLASSES ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def classe_list(request):
    classes = filtrar_classes_ebd(Classe.objects.all(), request)
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
        messages.success(request, 'Classe excluída com sucesso!')
        return redirect('escola_biblica:classe_list')
    return render(request, 'escola_biblica/classe_confirm_delete.html', {'classe': classe})






@page_access_required('escola_biblica_professor')
@verificar_assinatura_valida
def dashboard(request):
    turmas = filtrar_turmas_ebd(Turma.objects.all(), request)
    alunos = filtrar_alunos_ebd(Aluno.objects.all(), request)
    classes = filtrar_classes_ebd(Classe.objects.all(), request)
    licoes = filtrar_queryset_ebd(Licao.objects.all(), request, 'turma__igreja')
    avaliacoes = filtrar_queryset_ebd(Avaliacao.objects.all(), request, 'aluno__turma__igreja')
    igrejas_escopo = get_ebd_scope_churches(request)
    total_oferta = OfertaClasse.objects.filter(
        Q(turma__igreja__in=igrejas_escopo) |
        Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas_escopo) |
        Q(turma__isnull=True, classe__igreja__in=igrejas_escopo) |
        Q(turma__isnull=True, classe__igreja__isnull=True, classe__turma__membros__igreja__in=igrejas_escopo)
    ).distinct().aggregate(total=Sum('valor'))['total'] or 0

    igreja = getattr(request, 'igreja_ativa', None)
    if igreja is None and igrejas_escopo.count() == 1:
        igreja = igrejas_escopo.first()

    hoje = date.today()
    mes_atual = hoje.replace(day=1)
    ano_atual = hoje.year

    meses = [(hoje.replace(day=1) - timedelta(days=30*i)).replace(day=1) for i in range(11, -1, -1)]
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
            data_nascimento__lte=prox_mes
        )
        if igreja:
            qs = qs.filter(turma__membros__igreja=igreja).distinct()
        count = qs.count()
        alunos_evolucao.append(count)

    freq_mes = Frequencia.objects.filter(data__gte=mes_atual, data__lt=hoje+timedelta(days=1))
    if igreja:
        freq_mes = freq_mes.filter(aluno__turma__membros__igreja=igreja).distinct()
    alunos_ids = alunos.values_list('id', flat=True)
    engajados = 0
    for aluno_id in alunos_ids:
        freq_aluno = freq_mes.filter(aluno_id=aluno_id)
        total = freq_aluno.count()
        presencas = freq_aluno.filter(presente=True).count()
        if total > 0 and presencas/total >= 0.75:
            engajados += 1
    engajamento_percent = round((engajados/len(alunos_ids))*100, 1) if alunos_ids else 0

    evasao_qs = Aluno.objects.filter(ativo=False, turma__ano_letivo__ano__contains=str(ano_atual))
    if igreja:
        evasao_qs = evasao_qs.filter(turma__membros__igreja=igreja).distinct()
    evasao = evasao_qs.count()

    ranking_classes = []
    for classe in classes:
        alunos_classe = Aluno.objects.filter(turma__classe=classe, ativo=True)
        if igreja:
            alunos_classe = alunos_classe.filter(turma__membros__igreja=igreja).distinct()
        freq_total = 0
        freq_count = 0
        for aluno in alunos_classe:
            freq_aluno = Frequencia.objects.filter(aluno=aluno, data__gte=mes_atual, data__lt=hoje+timedelta(days=1))
            if igreja:
                freq_aluno = freq_aluno.filter(aluno__turma__membros__igreja=igreja).distinct()
            total = freq_aluno.count()
            presencas = freq_aluno.filter(presente=True).count()
            if total > 0:
                freq_total += presencas/total
                freq_count += 1
        freq_media = round((freq_total/freq_count)*100, 1) if freq_count else 0
        ranking_classes.append({'classe': classe.nome, 'frequencia_media': freq_media})
    ranking_classes = sorted(ranking_classes, key=lambda x: x['frequencia_media'], reverse=True)

    freq_geral_total = 0
    freq_geral_count = 0
    for aluno in alunos:
        freq_aluno = Frequencia.objects.filter(aluno=aluno, data__gte=mes_atual, data__lt=hoje+timedelta(days=1))
        if igreja:
            freq_aluno = freq_aluno.filter(aluno__turma__membros__igreja=igreja).distinct()
        total = freq_aluno.count()
        presencas = freq_aluno.filter(presente=True).count()
        if total > 0:
            freq_geral_total += presencas/total
            freq_geral_count += 1
    freq_geral = round((freq_geral_total/freq_geral_count)*100, 1) if freq_geral_count else 0

    ranking_ofertas = []
    for classe in classes:
        oferta_qs = OfertaClasse.objects.filter(
            Q(turma__classe=classe) | Q(turma__isnull=True, classe=classe),
            data__year=ano_atual,
        )
        if igreja:
            oferta_qs = oferta_qs.filter(
                Q(turma__igreja=igreja) |
                Q(turma__igreja__isnull=True, turma__membros__igreja=igreja) |
                Q(turma__isnull=True, classe__igreja=igreja) |
                Q(turma__isnull=True, classe__igreja__isnull=True, classe__turma__membros__igreja=igreja)
            ).distinct()
        total_oferta_classe = oferta_qs.aggregate(s=Sum('valor'))['s'] or 0
        ranking_ofertas.append({'classe': classe.nome, 'total_oferta': float(total_oferta_classe)})
    ranking_ofertas = sorted(ranking_ofertas, key=lambda x: x['total_oferta'], reverse=True)

    alunos_novos_qs = Aluno.objects.filter(turma__isnull=False, ativo=True, turma__ano_letivo__ativo=True, turma__ano_letivo__ano__contains=str(mes_atual.year), turma__classe__isnull=False, data_nascimento__isnull=False, data_nascimento__gte=mes_atual)
    if igreja:
        alunos_novos_qs = alunos_novos_qs.filter(turma__membros__igreja=igreja).distinct()
    alunos_novos = alunos_novos_qs.count()

    transferidos_mes_qs = TransferenciaAluno.objects.filter(data_transferencia__gte=mes_atual, data_transferencia__lt=hoje+timedelta(days=1))
    if igreja:
        transferidos_mes_qs = transferidos_mes_qs.filter(
            Q(turma_origem__membros__igreja=igreja) |
            Q(turma_destino__membros__igreja=igreja)
        ).distinct()
    transferidos_mes = transferidos_mes_qs.count()

    faixas = [
        ("0-5", 0, 5),
        ("6-12", 6, 12),
        ("13-17", 13, 17),
        ("18-29", 18, 29),
        ("30-59", 30, 59),
        ("60+", 60, 200),
    ]
    faixas_etarias_labels = [f[0] for f in faixas]
    faixas_etarias_counts = []
    for label, min_idade, max_idade in faixas:
        count = 0
        for aluno in alunos:
            if aluno.data_nascimento:
                idade = (hoje - aluno.data_nascimento).days // 365
                if min_idade <= idade <= max_idade:
                    count += 1
        faixas_etarias_counts.append(count)

    return render(request, 'escola_biblica/dashboard.html', {
        'turmas': turmas,
        'alunos': alunos,
        'classes': classes,
        'licoes': licoes,
        'avaliacoes': avaliacoes,
        'total_oferta': total_oferta,
        'alunos_evolucao': alunos_evolucao,
        'engajamento_percent': engajamento_percent,
        'evasao': evasao,
        'ranking_classes': ranking_classes,
        'freq_geral': freq_geral,
        'ranking_ofertas': ranking_ofertas,
        'alunos_novos': alunos_novos,
        'transferidos_mes': transferidos_mes,
        'meses': [m.strftime('%m/%Y') for m in meses],
        'faixas_etarias_labels': faixas_etarias_labels,
        'faixas_etarias_counts': faixas_etarias_counts,
    })

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

    # Verifica se é secretaria EBD (acesso total)
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
        # Secretaria vê todos os alunos
        alunos_list = Aluno.objects.all().order_by('nome')
        alunos_list = filtrar_alunos_ebd(alunos_list, request)
    else:
        # Professor vê apenas alunos de suas turmas
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
                f'{vinculados} cadastro(s) vinculados automaticamente à Secretaria. Vinculados: {exibicao}{sufixo}.',
            )
        if sem_correspondencia:
            messages.warning(request, f'{sem_correspondencia} cadastro(s) continuam sem correspondência segura.')
        if not vinculados and not sem_correspondencia:
            messages.info(request, 'Nenhum cadastro elegível para tentativa de vínculo automático.')

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
    
    paginator = Paginator(alunos_list, 20)  # 20 alunos por página
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
    now = date.today()
    anos_letivos = AnoLetivo.objects.order_by('-ano')
    ano_letivo_filtro = request.GET.get('ano_letivo')
    periodo_filtro = request.GET.get('periodo')
    nome_filtro = request.GET.get('nome', '').strip()
    classe_filtro = request.GET.get('classe', '').strip()
    ano_atual = now.year

    # Seleção do ano letivo
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

    # Sugerir cópia de turmas/classes/alunos do ano anterior se o ano letivo acabou de ser criado e não há turmas
    sugerir_copiar = False
    ano_anterior = ano_letivo_selecionado.ano - 1 if ano_letivo_selecionado else None
    turmas_ano_atual = Turma.objects.filter(ano_letivo=ano_letivo_selecionado).count() if ano_letivo_selecionado else 0
    turmas_ano_anterior = Turma.objects.filter(ano_letivo__ano=ano_anterior).count() if ano_anterior else 0
    if ano_letivo_selecionado and turmas_ano_atual == 0 and turmas_ano_anterior > 0:
        sugerir_copiar = True

    config = None
    tipo_periodo = 'trimestre'
    if hasattr(request, 'user') and request.user.is_authenticated:
        perfil = getattr(request.user, 'perfil', None)
        if perfil and hasattr(perfil, 'ministerio'):
            config = ConfiguracaoSistema.objects.filter(ministerio=perfil.ministerio).first()
            if config:
                tipo_periodo = config.ebd_periodo
    periodos = PeriodoEBD.objects.filter(ano_letivo=ano_letivo_selecionado, tipo=tipo_periodo).order_by('numero')
    periodo_selecionado = None
    if periodo_filtro:
        try:
            periodo_selecionado = periodos.get(numero=periodo_filtro)
        except PeriodoEBD.DoesNotExist:
            periodo_selecionado = periodos.first()
    else:
        periodo_selecionado = periodos.first()

    mostrar_banner_abrir_periodo = (ano_letivo_selecionado and ano_letivo_selecionado.ano == ano_atual and (not periodos or not periodo_selecionado))

    # Filtro unificado de turmas
    turmas_list = Turma.objects.filter(ano_letivo=ano_letivo_selecionado)
    
    # Verifica se é secretaria EBD (acesso total) ou professor (acesso limitado)
    is_secretaria = usuario_pode_gerenciar_ebd(request.user)
    
    if not is_secretaria:
        # Professores veem apenas suas turmas
        turmas_professor = get_turmas_professor(request.user)
        turmas_list = turmas_list.filter(id__in=turmas_professor.values_list('id', flat=True))
    
    if nome_filtro:
        turmas_list = turmas_list.filter(nome__icontains=nome_filtro)
    if classe_filtro:
        turmas_list = turmas_list.filter(classe__nome__icontains=classe_filtro)
    if periodo_selecionado:
        # Se quiser filtrar por período, adicione lógica aqui (exemplo: turmas_list = turmas_list.filter(periodo=periodo_selecionado))
        pass
    turmas_list = turmas_list.order_by('nome')
    turmas_list = filtrar_turmas_ebd(turmas_list, request)
    paginator = Paginator(turmas_list, 20)
    page = request.GET.get('page')
    try:
        turmas = paginator.page(page)
    except PageNotAnInteger:
        turmas = paginator.page(1)
    except EmptyPage:
        turmas = paginator.page(paginator.num_pages)
    # Banner do período EBD atual
    from .models import Licao
    ebd_periodo_atual = periodo_selecionado
    ebd_aulas_total = None
    ebd_aulas_realizadas = None
    ebd_percentual = None
    if ebd_periodo_atual:
        from .utils import gerar_domingos_periodo
        domingos = gerar_domingos_periodo(ebd_periodo_atual.data_inicio, ebd_periodo_atual.data_fim)
        ebd_aulas_total = len(domingos)
        # Aula atual: quantos domingos já passaram (incluindo hoje se for domingo)
        ebd_aulas_realizadas = sum(1 for d in domingos if d <= now)
        ebd_percentual = int((ebd_aulas_realizadas / ebd_aulas_total) * 100) if ebd_aulas_total else 0
    context = {
        'turmas': turmas,
        'anos_letivos': anos_letivos,
        'ano_letivo_selecionado': ano_letivo_selecionado,
        'periodos': periodos,
        'periodo_selecionado': periodo_selecionado,
        'tipo_periodo': tipo_periodo,
        'now': now,
        'request': request,
        'mostrar_banner_abrir_periodo': mostrar_banner_abrir_periodo,
        'sugerir_copiar': sugerir_copiar,
        'ebd_periodo_atual': ebd_periodo_atual,
        'ebd_aulas_total': ebd_aulas_total,
        'ebd_aulas_realizadas': ebd_aulas_realizadas,
        'ebd_percentual': ebd_percentual,
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
        messages.success(request, 'Turma excluída com sucesso!')
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


# --- NOVA VIEW: Geração automática de períodos e lições em lote ---
@page_access_required('escola_biblica')
@verificar_assinatura_valida
def gerar_cronograma(request):
    from django.contrib import messages
    from datetime import date
    from .models import Licao
    ano_atual = date.today().year
    turmas = filtrar_queryset_ebd(Turma.objects.filter(ano_letivo__ano=ano_atual, ano_letivo__ativo=True), request, 'membros__igreja')
    turma_selecionada = None
    config = None
    tipo_periodo = 'trimestre'
    # Busca configuração do período da EBD
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            # Supondo que o usuário tem perfil/ministério
            perfil = getattr(request.user, 'perfil', None)
            if perfil and hasattr(perfil, 'ministerio'):
                config = ConfiguracaoSistema.objects.filter(ministerio=perfil.ministerio).first()
                if config:
                    tipo_periodo = config.ebd_periodo
        except Exception as exc:
            logger.warning('Falha ao carregar configuração de período EBD para user=%s: %s', request.user.pk, exc)
    if request.method == 'POST':
        form = GerarCronogramaForm(request.POST, request=request)
        if form.is_valid():
            turma_id = form.cleaned_data.get('turma')
            turma_selecionada = Turma.objects.filter(id=turma_id.id if hasattr(turma_id, 'id') else turma_id).first()
            material = form.cleaned_data.get('material', '')
            observacoes = form.cleaned_data.get('observacoes', '')
            horario = form.cleaned_data.get('horario', None)
            status = form.cleaned_data.get('status', 'ativa')
            # Gera lições para todos os períodos e domingos do ano
            licoes = gerar_licoes_periodos(
                ano=ano_atual,
                tipo_periodo=tipo_periodo,
                turmas=[turma_selecionada] if turma_selecionada else turmas,
                material=material,
                observacoes=observacoes,
                horario=horario,
                status=status
            )
            # Salva as lições no banco
            from .models import Licao
            criadas = 0
            for licao_data in licoes:
                # Evita duplicidade: só cria se não existir para turma/data/tema
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
                messages.success(request, f'{criadas} lições geradas com sucesso!')
            else:
                messages.info(request, 'Nenhuma nova lição foi gerada (já existem para este período/turma).')
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
