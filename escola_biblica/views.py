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
from django.db.models import Avg, Count, Q, Sum
from django.db import transaction
from .models import Licao, Aluno, Turma, Frequencia, Classe, Avaliacao, OfertaClasse, TransferenciaAluno, Departamento, DEPARTAMENTOS_SUGERIDOS
from .forms import LicaoForm, AlunoForm, TurmaForm, FrequenciaForm, ClasseForm, AvaliacaoForm, OfertaClasseForm, TransferenciaAlunoForm, ChamadaPresencaFormSet, DepartamentoForm, GerarCronogramaForm


@require_GET
def get_professor_nome(request):
    turma_id = request.GET.get('turma_id')
    nome = ''
    if turma_id:
        try:
            turma = Turma.objects.get(pk=turma_id)
            nome = turma.get_professor_nome() or ''
        except Turma.DoesNotExist:
            nome = ''
    return JsonResponse({'professor': nome})

@login_required
@secretaria_ebd_required
@verificar_assinatura_valida
def turma_create(request):
    from datetime import date
    from .models import AnoLetivo
    ano_atual = date.today().year
    ano_letivo, created = AnoLetivo.objects.get_or_create(ano=ano_atual, defaults={'ativo': True})
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma cadastrada com sucesso!')
            return redirect('escola_biblica:turma_list')
    else:
        form = TurmaForm(initial={'ano_letivo': ano_letivo.pk})
    return render(request, 'escola_biblica/turma_form.html', {'form': form})
@login_required
@secretaria_ebd_required
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

@login_required
@secretaria_ebd_required
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

# --- CHAMADA DE PRESENÇA POR TURMA ---
@login_required
@secretaria_ebd_required
@verificar_assinatura_valida
@transaction.atomic
def chamada_presenca(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    alunos = turma.alunos.filter(ativo=True).order_by('nome')
    print(f"DEBUG: Turma {turma.id} - Alunos ativos encontrados: {alunos.count()}")
    data = request.POST.get('data') or request.GET.get('data') or timezone.now().date().isoformat()
    if not alunos.exists():
        messages.warning(request, 'Não há alunos ativos nesta turma para realizar a chamada de presença.')
        return render(request, 'escola_biblica/chamada_presenca.html', {
            'turma': turma,
            'formset': None,
            'data': data,
        })
    if request.method == 'POST':
        formset = ChamadaPresencaFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                aluno_id = form.cleaned_data['aluno_id']
                presente = form.cleaned_data.get('presente', False)
                Frequencia.objects.update_or_create(
                    aluno_id=aluno_id,
                    data=data,
                    defaults={'presente': presente}
                )
            messages.success(request, f'Chamada de presença registrada para {turma} em {data}.')
            return redirect('escola_biblica:turma_list')
        else:
            messages.error(request, 'Erro ao registrar chamada de presença. Verifique os dados e tente novamente.')
    else:
        initial = [
            {
                'aluno_id': aluno.id,
                'nome': aluno.nome,
                'presente': Frequencia.objects.filter(aluno=aluno, data=data, presente=True).exists()
            }
            for aluno in alunos
        ]
        formset = ChamadaPresencaFormSet(initial=initial)
    return render(request, 'escola_biblica/chamada_presenca.html', {
        'turma': turma,
        'formset': formset,
        'data': data,
    })

# --- PERFIL DO ALUNO E HISTÓRICO DE TRANSFERÊNCIAS ---


@login_required
@verificar_assinatura_valida
def aluno_detail(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    transferencias = aluno.transferencias.select_related('turma_origem', 'turma_destino', 'usuario_responsavel').all()
    return render(request, 'escola_biblica/aluno_detail.html', {
        'aluno': aluno,
        'transferencias': transferencias,
    })

# --- TRANSFERÊNCIA DE ALUNO ENTRE TURMAS/CLASSES ---
@login_required
@secretaria_ebd_required
@verificar_assinatura_valida
@transaction.atomic
def transferir_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    turma_origem = aluno.turma
    if request.method == 'POST':
        form = TransferenciaAlunoForm(request.POST)
        if form.is_valid():
            transferencia = form.save(commit=False)
            transferencia.aluno = aluno
            transferencia.turma_origem = turma_origem
            transferencia.usuario_responsavel = request.user
            transferencia.save()
            # Atualiza turma do aluno
            aluno.turma = transferencia.turma_destino
            aluno.save()
            messages.success(request, f'Transferência realizada com sucesso para {transferencia.turma_destino}!')
            return redirect('escola_biblica:aluno_list')
    else:
        form = TransferenciaAlunoForm(initial={'aluno': aluno})
    return render(request, 'escola_biblica/transferir_aluno.html', {
        'form': form,
        'aluno': aluno,
        'turma_origem': turma_origem,
    })



# --- RELATÓRIO DE FREQUÊNCIA DETALHADO ---
@login_required
@secretaria_ebd_required
@verificar_assinatura_valida
def relatorio_frequencia(request):
    turmas = Turma.objects.all()
    classes = Classe.objects.all()
    alunos = Aluno.objects.select_related('turma', 'turma__classe').all()
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        turmas = turmas.filter(membros__igreja=request.igreja_ativa).distinct()
        classes = classes.filter(turma__membros__igreja=request.igreja_ativa).distinct()
        alunos = alunos.filter(turma__membros__igreja=request.igreja_ativa).distinct()
    turma_id = request.GET.get('turma')
    classe_id = request.GET.get('classe')
    inicio = request.GET.get('inicio')
    fim = request.GET.get('fim')
    if turma_id:
        alunos = alunos.filter(turma_id=turma_id)
    if classe_id:
        alunos = alunos.filter(turma__classe_id=classe_id)
    # Cálculo de frequência detalhada
    for aluno in alunos:
        freq_qs = Frequencia.objects.filter(aluno=aluno)
        if inicio:
            freq_qs = freq_qs.filter(data__gte=inicio)
        if fim:
            freq_qs = freq_qs.filter(data__lte=fim)
        total_freq = freq_qs.count()
        presencas = freq_qs.filter(presente=True).count()
        aluno.freq_percent = round((presencas/total_freq)*100, 1) if total_freq else None
        aluno.total_freq = total_freq
        aluno.presencas = presencas
    # Exportação CSV
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="relatorio_frequencia.csv"'
        writer = csv.writer(response)
        writer.writerow(['Aluno', 'Turma', 'Classe', 'Presenças', 'Total Aulas', 'Frequência (%)'])
        for aluno in alunos:
            writer.writerow([
                aluno.nome,
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
@login_required
@verificar_assinatura_valida
def cargos_ebd_list(request):
    from secretaria.models import MembroCargo, Cargo
    cargo_nome = request.GET.get('cargo')
    cargos_disponiveis = Cargo.objects.filter(is_ebd=True).values_list('nome', flat=True).distinct()
    colaboradores = MembroCargo.objects.select_related('membro', 'cargo').filter(cargo__is_ebd=True)
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        colaboradores = colaboradores.filter(membro__igreja=request.igreja_ativa)
    if cargo_nome:
        colaboradores = colaboradores.filter(cargo__nome__iexact=cargo_nome)
    return render(request, 'escola_biblica/cargos_ebd_list.html', {
        'colaboradores': colaboradores,
        'cargos_disponiveis': cargos_disponiveis,
        'cargo_selecionado': cargo_nome,
    })

# --- GRÁFICOS DE EVOLUÇÃO ---
@login_required
@verificar_assinatura_valida
def graficos_evolucao(request):
    hoje = timezone.now().date()
    meses = [(hoje.replace(day=1) - timezone.timedelta(days=30*i)).replace(day=1) for i in range(11, -1, -1)]
    meses_fmt = [m.strftime('%m/%Y') for m in meses]

    alunos_evolucao = defaultdict(lambda: [0]*12)
    for idx, mes in enumerate(meses):
        prox_mes = (mes + timezone.timedelta(days=32)).replace(day=1)
        for turma in Turma.objects.filter(ano_letivo__ativo=True, classe__isnull=False):
            classe_nome = turma.classe.nome
            count = Aluno.objects.filter(turma=turma, data_matricula__lte=prox_mes, data_saida__isnull=True).count()
            alunos_evolucao[classe_nome][idx] += count

    ofertas_evolucao = defaultdict(lambda: [0]*12)
    for idx, mes in enumerate(meses):
        prox_mes = (mes + timezone.timedelta(days=32)).replace(day=1)
        for classe in Classe.objects.all():
            total = OfertaClasse.objects.filter(classe=classe, data__gte=mes, data__lt=prox_mes).aggregate(s=Sum('valor'))['s'] or 0
            ofertas_evolucao[classe.nome][idx] = float(total)

    context = {
        'meses': json.dumps(meses_fmt),
        'alunos_evolucao': json.dumps(alunos_evolucao),
        'ofertas_evolucao': json.dumps(ofertas_evolucao),
    }
    return render(request, 'escola_biblica/graficos_evolucao.html', context)

# --- DASHBOARD GRÁFICOS ---
@login_required
@verificar_assinatura_valida
def dashboard_graficos(request):
    departamentos = dict(Classe.DEPARTAMENTO_CHOICES)
    alunos_por_departamento = {d: 0 for d in departamentos.values()}
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        for dep_key, dep_label in departamentos.items():
            alunos_por_departamento[dep_label] = Aluno.objects.filter(turma__classe__departamento=dep_key, turma__membros__igreja=request.igreja_ativa).distinct().count()
    else:
        for dep_key, dep_label in departamentos.items():
            alunos_por_departamento[dep_label] = Aluno.objects.filter(turma__classe__departamento=dep_key).count()

    ofertas_por_departamento = {d: 0 for d in departamentos.values()}
    for dep_key, dep_label in departamentos.items():
        ofertas_por_departamento[dep_label] = OfertaClasse.objects.filter(classe__departamento=dep_key).aggregate(total=Sum('valor'))['total'] or 0

    ofertas_por_classe = {}
    for classe in Classe.objects.all():
        ofertas_por_classe[classe.nome] = OfertaClasse.objects.filter(classe=classe).aggregate(total=Sum('valor'))['total'] or 0

    alunos_por_classe = {}
    for classe in Classe.objects.all():
        alunos_por_classe[classe.nome] = Aluno.objects.filter(turma__classe=classe).count()

    context = {
        'alunos_por_departamento': json.dumps(alunos_por_departamento),
        'ofertas_por_departamento': json.dumps(ofertas_por_departamento),
        'ofertas_por_classe': json.dumps(ofertas_por_classe),
        'alunos_por_classe': json.dumps(alunos_por_classe),
    }
    return render(request, 'escola_biblica/dashboard_graficos.html', context)

# --- OFERTAS POR CLASSE ---
@login_required
@secretaria_ebd_required
@verificar_assinatura_valida
def oferta_classe_list(request):
    ofertas = OfertaClasse.objects.select_related('classe').order_by('-data')
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        ofertas = ofertas.filter(classe__turma__membros__igreja=request.igreja_ativa).distinct()
    return render(request, 'escola_biblica/oferta_classe_list.html', {'ofertas': ofertas})

@login_required
@secretaria_ebd_required
@verificar_assinatura_valida
def oferta_classe_create(request):
    if request.method == 'POST':
        form = OfertaClasseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Oferta registrada com sucesso!')
            return redirect('escola_biblica:oferta_classe_list')
    else:
        form = OfertaClasseForm()
    return render(request, 'escola_biblica/oferta_classe_form.html', {'form': form})

@login_required
@secretaria_ebd_required
@verificar_assinatura_valida
def oferta_classe_edit(request, pk):
    oferta = get_object_or_404(OfertaClasse, pk=pk)
    if request.method == 'POST':
        form = OfertaClasseForm(request.POST, instance=oferta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Oferta atualizada com sucesso!')
            return redirect('escola_biblica:oferta_classe_list')
    else:
        form = OfertaClasseForm(instance=oferta)
    return render(request, 'escola_biblica/oferta_classe_form.html', {'form': form, 'oferta': oferta})

@login_required
@superintendente_required
@verificar_assinatura_valida
def oferta_classe_delete(request, pk):
    oferta = get_object_or_404(OfertaClasse, pk=pk)
    if request.method == 'POST':
        oferta.delete()
        messages.success(request, 'Oferta excluída com sucesso!')
        return redirect('escola_biblica:oferta_classe_list')
    return render(request, 'escola_biblica/oferta_classe_confirm_delete.html', {'oferta': oferta})

# --- RELATÓRIO DE ALUNOS ---
@login_required
@verificar_assinatura_valida
def relatorio_alunos(request):
    turmas = Turma.objects.all()
    classes = Classe.objects.all()
    alunos = Aluno.objects.select_related('turma', 'turma__classe').all()
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        turmas = turmas.filter(membros__igreja=request.igreja_ativa).distinct()
        classes = classes.filter(turma__membros__igreja=request.igreja_ativa).distinct()
        alunos = alunos.filter(turma__membros__igreja=request.igreja_ativa).distinct()
    turma_id = request.GET.get('turma')
    classe_id = request.GET.get('classe')
    inicio = request.GET.get('inicio')
    fim = request.GET.get('fim')
    if turma_id:
        alunos = alunos.filter(turma_id=turma_id)
    if classe_id:
        alunos = alunos.filter(turma__classe_id=classe_id)
    # Cálculo de frequência, média de nota e participação
    for aluno in alunos:
        freq_qs = Frequencia.objects.filter(aluno=aluno)
        if inicio:
            freq_qs = freq_qs.filter(data__gte=inicio)
        if fim:
            freq_qs = freq_qs.filter(data__lte=fim)
        total_freq = freq_qs.count()
        presencas = freq_qs.filter(presente=True).count()
        aluno.freq_percent = round((presencas/total_freq)*100, 1) if total_freq else None
        aval_qs = Avaliacao.objects.filter(aluno=aluno)
        if inicio:
            aval_qs = aval_qs.filter(licao__data__gte=inicio)
        if fim:
            aval_qs = aval_qs.filter(licao__data__lte=fim)
        aluno.media_nota = round(aval_qs.aggregate(m=Avg('nota'))['m'] or 0, 2) if aval_qs.exists() else None
        aluno.participacao = aval_qs.filter(participacao=True).count()
    return render(request, 'escola_biblica/relatorio_alunos.html', {
        'turmas': turmas,
        'classes': classes,
        'alunos': alunos,
    })
# --- LICOES ---
 
 # --- AVALIAÇÕES ---
@login_required
@verificar_assinatura_valida
def avaliacao_list(request):
    avaliacoes = Avaliacao.objects.select_related('aluno', 'licao').all()
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        avaliacoes = avaliacoes.filter(aluno__turma__membros__igreja=request.igreja_ativa).distinct()
    return render(request, 'escola_biblica/avaliacao_list.html', {'avaliacoes': avaliacoes})

@login_required
@secretaria_ebd_required
@verificar_assinatura_valida
def avaliacao_create(request):
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Avaliação cadastrada com sucesso!')
            return redirect('escola_biblica:avaliacao_list')
    else:
        form = AvaliacaoForm()
    return render(request, 'escola_biblica/avaliacao_form.html', {'form': form})

@login_required
@secretaria_ebd_required
@verificar_assinatura_valida
def avaliacao_edit(request, pk):
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=avaliacao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Avaliação atualizada com sucesso!')
            return redirect('escola_biblica:avaliacao_list')
    else:
        form = AvaliacaoForm(instance=avaliacao)
    return render(request, 'escola_biblica/avaliacao_form.html', {'form': form, 'avaliacao': avaliacao})

@login_required
@superintendente_required
def avaliacao_delete(request, pk):
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    if request.method == 'POST':
        avaliacao.delete()
        messages.success(request, 'Avaliação excluída com sucesso!')
        return redirect('escola_biblica:avaliacao_list')
    return render(request, 'escola_biblica/avaliacao_confirm_delete.html', {'avaliacao': avaliacao})
@login_required
@verificar_assinatura_valida
def licao_list(request):
    licoes = Licao.objects.all()
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        licoes = licoes.filter(turma__membros__igreja=request.igreja_ativa).distinct()
    return render(request, 'escola_biblica/licao_list.html', {'licoes': licoes})

@login_required
@secretaria_ebd_required
def licao_create(request):
    turmas = Turma.objects.all()
    if request.method == 'POST':
        form = LicaoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lição cadastrada com sucesso!')
            return redirect('escola_biblica:licao_list')
    else:
        form = LicaoForm()
    return render(request, 'escola_biblica/licao_form.html', {'form': form, 'turmas': turmas})

@login_required
@secretaria_ebd_required
def licao_edit(request, pk):
    licao = get_object_or_404(Licao, pk=pk)
    turmas = Turma.objects.all()
    if request.method == 'POST':
        form = LicaoForm(request.POST, request.FILES, instance=licao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lição atualizada com sucesso!')
            return redirect('escola_biblica:licao_list')
    else:
        form = LicaoForm(instance=licao)
    return render(request, 'escola_biblica/licao_form.html', {'form': form, 'licao': licao, 'turmas': turmas})

@login_required
@superintendente_required
def licao_delete(request, pk):
    licao = get_object_or_404(Licao, pk=pk)
    if request.method == 'POST':
        licao.delete()
        messages.success(request, 'Lição excluída com sucesso!')
        return redirect('escola_biblica:licao_list')
# --- CLASSES ---
# --- CLASSES ---
@login_required
@verificar_assinatura_valida
def classe_list(request):
    classes = Classe.objects.all()
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        classes = classes.filter(turma__membros__igreja=request.igreja_ativa).distinct()
    return render(request, 'escola_biblica/classe_list.html', {'classes': classes})

@login_required
@secretaria_ebd_required
def classe_create(request):
    if request.method == 'POST':
        form = ClasseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Classe cadastrada com sucesso!')
            return redirect('escola_biblica:classe_list')
    else:
        form = ClasseForm()
    return render(request, 'escola_biblica/classe_form.html', {'form': form})

@login_required
@secretaria_ebd_required
def classe_edit(request, pk):
    classe = get_object_or_404(Classe, pk=pk)
    if request.method == 'POST':
        form = ClasseForm(request.POST, instance=classe)
        if form.is_valid():
            form.save()
            messages.success(request, 'Classe atualizada com sucesso!')
            return redirect('escola_biblica:classe_list')
    else:
        form = ClasseForm(instance=classe)
    return render(request, 'escola_biblica/classe_form.html', {'form': form, 'classe': classe})

@login_required
@superintendente_required
def classe_delete(request, pk):
    classe = get_object_or_404(Classe, pk=pk)
    if request.method == 'POST':
        classe.delete()
        messages.success(request, 'Classe excluída com sucesso!')
        return redirect('escola_biblica:classe_list')
    return render(request, 'escola_biblica/classe_confirm_delete.html', {'classe': classe})






@login_required
@secretaria_ebd_required
@login_required
@verificar_assinatura_valida
def dashboard(request):
    turmas = Turma.objects.all()
    alunos = Aluno.objects.all()
    classes = Classe.objects.all()
    licoes = Licao.objects.all()
    avaliacoes = Avaliacao.objects.all()
    total_oferta = OfertaClasse.objects.aggregate(total=Sum('valor'))['total'] or 0

    # Filtro por igreja ativa
    igreja = getattr(request, 'igreja_ativa', None)
    if igreja:
        turmas = turmas.filter(membros__igreja=igreja).distinct()
        alunos = alunos.filter(turma__membros__igreja=igreja).distinct()
        classes = classes.filter(turma__membros__igreja=igreja).distinct()
        licoes = licoes.filter(turma__membros__igreja=igreja).distinct()
        avaliacoes = avaliacoes.filter(aluno__turma__membros__igreja=igreja).distinct()
        total_oferta = OfertaClasse.objects.filter(classe__turma__membros__igreja=igreja).aggregate(total=Sum('valor'))['total'] or 0

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
        oferta_qs = OfertaClasse.objects.filter(classe=classe, data__year=ano_atual)
        if igreja:
            oferta_qs = oferta_qs.filter(classe__turma__membros__igreja=igreja).distinct()
        total_oferta_classe = oferta_qs.aggregate(s=Sum('valor'))['s'] or 0
        ranking_ofertas.append({'classe': classe.nome, 'total_oferta': float(total_oferta_classe)})
    ranking_ofertas = sorted(ranking_ofertas, key=lambda x: x['total_oferta'], reverse=True)

    alunos_novos_qs = Aluno.objects.filter(turma__isnull=False, ativo=True, turma__ano_letivo__ativo=True, turma__ano_letivo__ano__contains=str(mes_atual.year), turma__classe__isnull=False, data_nascimento__isnull=False, data_nascimento__gte=mes_atual)
    if igreja:
        alunos_novos_qs = alunos_novos_qs.filter(turma__membros__igreja=igreja).distinct()
    alunos_novos = alunos_novos_qs.count()

    transferidos_mes_qs = TransferenciaAluno.objects.filter(data_transferencia__gte=mes_atual, data_transferencia__lt=hoje+timedelta(days=1))
    if igreja:
        transferidos_mes_qs = transferidos_mes_qs.filter(aluno__turma__membros__igreja=igreja).distinct()
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
@verificar_assinatura_valida
def aluno_list(request):
    alunos_list = Aluno.objects.all().order_by('nome')
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        alunos_list = alunos_list.filter(turma__membros__igreja=request.igreja_ativa).distinct()
    paginator = Paginator(alunos_list, 20)  # 20 alunos por página
    page = request.GET.get('page')
    try:
        alunos = paginator.page(page)
    except PageNotAnInteger:
        alunos = paginator.page(1)
    except EmptyPage:
        alunos = paginator.page(paginator.num_pages)
    return render(request, 'escola_biblica/aluno_list.html', {'alunos': alunos})

@login_required
@verificar_assinatura_valida
def aluno_create(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('escola_biblica:aluno_list')
    else:
        form = AlunoForm()
    return render(request, 'escola_biblica/aluno_form.html', {'form': form})

@login_required
@verificar_assinatura_valida
def turma_list(request):
    turmas_list = Turma.objects.all().order_by('nome')
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        turmas_list = turmas_list.filter(membros__igreja=request.igreja_ativa).distinct()
    paginator = Paginator(turmas_list, 20)
    page = request.GET.get('page')
    try:
        turmas = paginator.page(page)
    except PageNotAnInteger:
        turmas = paginator.page(1)
    except EmptyPage:
        turmas = paginator.page(paginator.num_pages)
    return render(request, 'escola_biblica/turma_list.html', {'turmas': turmas})

# --- EDITAR TURMA ---
from .forms import TurmaForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

@login_required
@secretaria_ebd_required
@verificar_assinatura_valida
def turma_edit(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    if request.method == 'POST':
        form = TurmaForm(request.POST, instance=turma)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma atualizada com sucesso!')
            return redirect('escola_biblica:turma_list')
    else:
        form = TurmaForm(instance=turma)
    return render(request, 'escola_biblica/turma_form.html', {'form': form, 'turma': turma})

# --- EXCLUIR TURMA ---
@login_required
@superintendente_required
def turma_delete(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    if request.method == 'POST':
        turma.delete()
        messages.success(request, 'Turma excluída com sucesso!')
        return redirect('escola_biblica:turma_list')
    return render(request, 'escola_biblica/turma_confirm_delete.html', {'turma': turma})

@login_required
@verificar_assinatura_valida
def frequencia_list(request):
    frequencias_list = Frequencia.objects.select_related('aluno', 'aluno__turma').all().order_by('-data')
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
def gerar_cronograma(request):
    from django.contrib import messages
    from datetime import date
    ano_atual = date.today().year
    turmas = Turma.objects.filter(ano_letivo__ano=ano_atual, ano_letivo__ativo=True)
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
        except Exception:
            pass
    if request.method == 'POST':
        form = GerarCronogramaForm(request.POST)
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
        form = GerarCronogramaForm()
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
