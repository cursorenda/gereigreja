from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from .forms import ConfiguracaoSistemaForm
from .models import ConfiguracaoSistema
from contas.constants import (
    ADMIN_MINISTERIO,
    PASTOR_LOCAL,
    SECRETARIO_LOCAL,
    user_is_admin,
)
from core.decorators import user_passes_test_or_403, admin_ministerio_required, verificar_assinatura_valida  # Importar decorator que lança 403 e assinatura
from configuracao.services_assinatura import (
    contar_pessoas_ativas,
    dias_restantes_graca,
    dias_restantes_trial,
    iniciar_trial,
    is_trial_ativo,
    listar_planos_para_ministerio,
    ministerio_pode_contratar_plano,
    ministerio_pode_criar_igreja,
    obter_limite_pessoas_ativas,
    obter_plano_efetivo_ministerio,
)

# --- NOVA VIEW: Perfil de qualquer usuário (admin/gestor pode ver o perfil de outro usuário) ---
def _usuario_pode_ver_perfil(viewer, target_user):
    if viewer.is_superuser or viewer.groups.filter(name__in=[ADMIN_MINISTERIO, 'Gestor']).exists():
        return True
    if viewer == target_user:
        return True

    try:
        from secretaria.models import MembroCargo

        membro_logado = getattr(viewer, 'membro_secretaria', None)
        if membro_logado:
            return MembroCargo.objects.filter(
                membro=membro_logado,
                cargo__is_ebd=True,
                data_fim__isnull=True,
            ).exists()
    except Exception:
        return False

    return False


def _montar_contexto_hub_perfil(request, usuario_alvo, perfil_usuario_obj, titulo_pagina):
    from collections import defaultdict
    from django.db.models import Avg, ExpressionWrapper, IntegerField
    from django.utils import timezone
    from escola_biblica.models import Aluno, Avaliacao, Frequencia, Licao, TransferenciaAluno, Turma
    from escola_biblica.utils import is_professor_ebd

    aba_ativa = request.GET.get('aba', 'resumo')
    abas_validas = {'resumo', 'acesso', 'secretaria', 'ebd-aluno', 'ebd-professor'}
    if aba_ativa not in abas_validas:
        aba_ativa = 'resumo'

    membro = getattr(usuario_alvo, 'membro_secretaria', None)
    hoje = timezone.now().date()
    secretaria_detalhe_url = None
    if membro:
        try:
            from secretaria.utils import get_allowed_churches_for_membros

            allowed_churches = get_allowed_churches_for_membros(request.user, perfil_usuario_obj.ministerio)
            if request.user.is_superuser or allowed_churches.filter(pk=membro.igreja_id).exists():
                secretaria_detalhe_url = reverse('secretaria:detalhe_membro', args=[membro.pk])
        except Exception:
            secretaria_detalhe_url = None

    is_professor = is_professor_ebd(membro) if membro else False
    licoes_ministradas = []
    turmas_professor = []
    stats_professor = {}
    proximas_licoes = []
    historico_licoes_ministradas = []
    if is_professor and membro:
        ano_atual = hoje.year
        licoes_ministradas = Licao.objects.filter(professor=membro, turma__ano_letivo__ano=ano_atual).order_by('-data')
        turmas_professor_qs = Turma.objects.filter(membros=membro, ano_letivo__ano=ano_atual)
        nomes_unicos = set()
        for turma in turmas_professor_qs:
            nome_normalizado = turma.nome.strip().lower()
            if nome_normalizado not in nomes_unicos:
                turmas_professor.append(turma)
                nomes_unicos.add(nome_normalizado)
        total_licoes = licoes_ministradas.count()
        avaliacoes = Avaliacao.objects.filter(licao__in=licoes_ministradas)
        media_nota = avaliacoes.aggregate(Avg('nota'))['nota__avg'] if avaliacoes.exists() else None
        freq_media = None
        if total_licoes > 0 and avaliacoes.exists():
            avaliacoes_com_cast = avaliacoes.annotate(
                participacao_int=ExpressionWrapper(models.F('participacao'), output_field=IntegerField())
            )
            freq_media = avaliacoes_com_cast.aggregate(freq=Avg('participacao_int'))['freq']
        proximas_licoes = licoes_ministradas.filter(data__gte=hoje).order_by('data')[:5]
        historico_licoes_ministradas = licoes_ministradas.filter(data__lte=hoje).order_by('-data')[:10]
        stats_professor = {
            'total_licoes': total_licoes,
            'media_nota': media_nota,
            'freq_media': freq_media,
        }

    cadastros_ebd = []
    cadastro_ebd = None
    matricula_referencia_ebd = None
    turmas_aluno = []
    proximas_licoes_aluno = []
    frequencia_aluno = None
    historico_licoes_aluno = []
    professores_turmas = {}
    total_transferencias_ebd = 0
    total_avaliacoes_ebd = 0
    ebd_vinculo_legado = False
    perfil_ebd_url = None
    historico_ebd_url = None
    if membro:
        alunos = Aluno.objects.select_related(
            'cadastro',
            'cadastro__pessoa',
            'turma',
            'turma__ano_letivo',
            'turma__classe',
        ).filter(cadastro__pessoa_id=membro.pk).order_by(
            '-ativo', '-turma__ano_letivo__ano', '-updated_at', '-id'
        )

        if not alunos.exists():
            alunos = Aluno.objects.select_related(
                'cadastro',
                'cadastro__pessoa',
                'turma',
                'turma__ano_letivo',
                'turma__classe',
            ).filter(
                cadastro__pessoa__isnull=True,
                cadastro__igreja_id=membro.igreja_id,
                nome__iexact=membro.nome,
            ).order_by('-ativo', '-turma__ano_letivo__ano', '-updated_at', '-id')
            ebd_vinculo_legado = alunos.exists()

        matriculas_ebd = list(alunos)
        if matriculas_ebd:
            matriculas_por_cadastro = defaultdict(list)
            for matricula in matriculas_ebd:
                matriculas_por_cadastro[matricula.cadastro_id].append(matricula)

            for matriculas_cadastro in matriculas_por_cadastro.values():
                cadastro_atual = matriculas_cadastro[0].cadastro
                matricula_referencia = cadastro_atual.get_matricula_referencia(
                    data_referencia=hoje,
                    matriculas=matriculas_cadastro,
                ) or matriculas_cadastro[0]
                cadastros_ebd.append({
                    'cadastro': cadastro_atual,
                    'matricula_referencia': matricula_referencia,
                    'matriculas': matriculas_cadastro,
                    'total_matriculas': len(matriculas_cadastro),
                    'possui_matricula_ativa': any(m.ativo for m in matriculas_cadastro),
                })

            cadastros_ebd.sort(
                key=lambda item: (
                    1 if item['matricula_referencia'] and item['matricula_referencia'].ativo else 0,
                    getattr(getattr(item['matricula_referencia'].turma, 'ano_letivo', None), 'ano', 0) if item['matricula_referencia'] else 0,
                    item['matricula_referencia'].id if item['matricula_referencia'] else 0,
                ),
                reverse=True,
            )

            cadastro_ebd = cadastros_ebd[0]['cadastro']
            matricula_referencia_ebd = cadastros_ebd[0]['matricula_referencia']

            turma_ids_ativas = []
            for matricula in matriculas_ebd:
                if matricula.ativo and matricula.turma_id not in turma_ids_ativas:
                    turma_ids_ativas.append(matricula.turma_id)
                    turmas_aluno.append(matricula.turma)

            if not turmas_aluno:
                for item in cadastros_ebd:
                    matricula_referencia = item['matricula_referencia']
                    if matricula_referencia and matricula_referencia.turma_id not in turma_ids_ativas:
                        turma_ids_ativas.append(matricula_referencia.turma_id)
                        turmas_aluno.append(matricula_referencia.turma)

            if turma_ids_ativas:
                proximas_licoes_aluno = list(
                    Licao.objects.filter(turma_id__in=turma_ids_ativas, data__gte=hoje)
                    .select_related('turma')
                    .order_by('data', 'id')[:5]
                )
                historico_licoes_aluno = list(
                    Licao.objects.filter(turma_id__in=turma_ids_ativas, data__lte=hoje)
                    .select_related('turma')
                    .order_by('-data', '-id')[:10]
                )
                professores_turmas = {turma.id: turma.get_professor_nome() for turma in turmas_aluno}

            cadastro_ids = [item['cadastro'].id for item in cadastros_ebd]
            frequencias_qs = Frequencia.objects.filter(aluno__cadastro_id__in=cadastro_ids)
            total_frequencias = frequencias_qs.count()
            if total_frequencias:
                presencas = frequencias_qs.filter(presente=True).count()
                frequencia_aluno = {
                    'total': total_frequencias,
                    'presentes': presencas,
                    'percentual': (presencas / total_frequencias * 100),
                }

            total_transferencias_ebd = TransferenciaAluno.objects.filter(aluno__cadastro_id__in=cadastro_ids).count()
            total_avaliacoes_ebd = Avaliacao.objects.filter(aluno__cadastro_id__in=cadastro_ids).count()

            if matricula_referencia_ebd:
                perfil_ebd_url = reverse('escola_biblica:aluno_detail', args=[matricula_referencia_ebd.pk])
                historico_ebd_url = reverse('escola_biblica:aluno_historico_consolidado', args=[matricula_referencia_ebd.pk])

    cargos_ativos = []
    if membro:
        try:
            from secretaria.models import MembroCargo
            cargos_ativos = MembroCargo.objects.filter(membro=membro, data_fim__isnull=True).select_related('cargo')
        except Exception:
            cargos_ativos = []

    return {
        'perfil_usuario': perfil_usuario_obj,
        'usuario': usuario_alvo,
        'titulo_pagina': titulo_pagina,
        'ministerio': perfil_usuario_obj.ministerio,
        'is_professor_ebd': is_professor,
        'licoes_ministradas': licoes_ministradas,
        'historico_licoes_ministradas': historico_licoes_ministradas,
        'turmas_professor': turmas_professor,
        'stats_professor': stats_professor,
        'proximas_licoes': proximas_licoes,
        'cargos_ativos': cargos_ativos,
        'turmas_aluno': turmas_aluno,
        'proximas_licoes_aluno': proximas_licoes_aluno,
        'frequencia_aluno': frequencia_aluno,
        'historico_licoes_aluno': historico_licoes_aluno,
        'professores_turmas': professores_turmas,
        'aba_ativa': aba_ativa,
        'cadastros_ebd': cadastros_ebd,
        'cadastro_ebd': cadastro_ebd,
        'matricula_referencia_ebd': matricula_referencia_ebd,
        'total_transferencias_ebd': total_transferencias_ebd,
        'total_avaliacoes_ebd': total_avaliacoes_ebd,
        'ebd_vinculo_legado': ebd_vinculo_legado,
        'perfil_ebd_url': perfil_ebd_url,
        'historico_ebd_url': historico_ebd_url,
        'membro_secretaria_obj': membro,
        'secretaria_detalhe_url': secretaria_detalhe_url,
    }


@login_required
def perfil_usuario(request, user_id):
    User = get_user_model()
    user = User.objects.filter(id=user_id).first()
    if not user or not hasattr(user, 'perfil'):
        from django.contrib import messages
        messages.error(request, 'Usuário ou perfil não encontrado.')
        return redirect('configuracao:configuracao')

    if not _usuario_pode_ver_perfil(request.user, user):
        from django.contrib import messages
        messages.error(request, 'Você não tem permissão para visualizar o perfil deste usuário.')
        return redirect('configuracao:configuracao')

    context = _montar_contexto_hub_perfil(
        request=request,
        usuario_alvo=user,
        perfil_usuario_obj=user.perfil,
        titulo_pagina=f"Perfil de {user.get_full_name() or user.username}",
    )
    return render(request, 'configuracao/perfil/meu_perfil.html', context)
from django.contrib.auth.decorators import login_required
from .forms import ConfiguracaoSistemaForm

# --- NOVA VIEW: Editar Configurações do Sistema (Notificações) ---
from django.contrib.auth.decorators import user_passes_test
from .models import ConfiguracaoSistema

def is_admin_ministerio(user):
    return user.is_authenticated and user.groups.filter(name=ADMIN_MINISTERIO).exists()


@login_required
@verificar_assinatura_valida
@admin_ministerio_required
def configuracoes_ministerio(request):
    # Buscar o ministério do usuário logado
    perfil = getattr(request.user, 'perfil', None)
    ministerio = getattr(perfil, 'ministerio', None)

    categorias = []
    fornecedores = []
    contas_bancarias = []
    can_edit_finance = False
    notificacoes_form = None
    ebd_form = None
    portal_form = None
    carteirinha_form = None
    url_personalizar_carteirinha = None
    aba_ativa = request.POST.get('aba_ativa') or request.GET.get('aba') or 'fornecedores'
    if ministerio:
        from financeiro.models import CategoriaDespesa, Fornecedor, ContaBancaria
        from financeiro.utils import has_finance_edit_permission
        categorias = CategoriaDespesa.objects.filter(ministerio=ministerio)
        fornecedores = Fornecedor.objects.filter(ministerio=ministerio)
        igrejas = Igreja.objects.filter(ministerio=ministerio)
        contas_bancarias = ContaBancaria.objects.filter(igreja__in=igrejas)
        can_edit_finance = has_finance_edit_permission(request.user)
        config, _ = ConfiguracaoSistema.objects.get_or_create(ministerio=ministerio)


        import logging
        from .forms import ConfiguracaoNotificacoesForm, ConfiguracaoEBDForm, ConfiguracaoPortalForm, MinisterioCarteirinhaPoliticaForm
        logger = logging.getLogger("django")
        carteirinha_form = MinisterioCarteirinhaPoliticaForm(instance=ministerio)
        url_personalizar_carteirinha = reverse('configuracao:carteirinha_ministerio')
        # Notificações
        if request.method == 'POST' and request.POST.get('aba_ativa') == 'notificacoes':
            logger.info(f"POST recebido: {request.POST}")
            notificacoes_form = ConfiguracaoNotificacoesForm(request.POST, instance=config)
            if notificacoes_form.is_valid():
                notificacoes_form.save()
                config.refresh_from_db()
                messages.success(request, "Configurações de notificações atualizadas com sucesso!")
            else:
                logger.warning(f"Erros no formulário de notificações: {notificacoes_form.errors}")
                messages.error(request, f"Erros ao salvar: {notificacoes_form.errors}")
            notificacoes_form = ConfiguracaoNotificacoesForm(instance=config)
        else:
            notificacoes_form = ConfiguracaoNotificacoesForm(instance=config)

        # EBD
        if request.method == 'POST' and request.POST.get('aba_ativa') == 'ebd':
            ebd_form = ConfiguracaoEBDForm(request.POST, instance=config)
            if ebd_form.is_valid():
                ebd_form.save()
                messages.success(request, "Configuração da Escola Bíblica atualizada com sucesso!")
        else:
            ebd_form = ConfiguracaoEBDForm(instance=config)

        # Portal do Membro
        if request.method == 'POST' and request.POST.get('aba_ativa') == 'portal':
            portal_form = ConfiguracaoPortalForm(request.POST, instance=config)
            if portal_form.is_valid():
                portal_form.save()
                messages.success(request, "Links devocionais do portal atualizados com sucesso!")
        else:
            portal_form = ConfiguracaoPortalForm(instance=config)

        # Carteirinha Premium (política de emissão)
        if request.method == 'POST' and request.POST.get('aba_ativa') == 'carteirinha':
            carteirinha_form = MinisterioCarteirinhaPoliticaForm(request.POST, instance=ministerio)
            if carteirinha_form.is_valid():
                carteirinha_form.save()
                messages.success(request, "Política da carteirinha atualizada com sucesso!")
            else:
                messages.error(request, f"Erros ao salvar política da carteirinha: {carteirinha_form.errors}")

    context = {
        'categorias': categorias,
        'fornecedores': fornecedores,
        'contas_bancarias': contas_bancarias,
        'ministerio': ministerio,
        'can_edit_finance': can_edit_finance,
        'notificacoes_form': notificacoes_form,
        'ebd_form': ebd_form,
        'portal_form': portal_form,
        'carteirinha_form': carteirinha_form,
        'url_personalizar_carteirinha': url_personalizar_carteirinha,
        'aba_ativa': aba_ativa,
    }
    return render(request, 'configuracao/configuracoes_sistema.html', context)


@login_required
@verificar_assinatura_valida
@admin_ministerio_required
def configuracoes_sistema_legacy_redirect(request):
    messages.info(request, 'As configurações foram movidas para Meu Ministério > Configurações do Ministério.')
    return redirect('configuracao:configuracoes_ministerio')
# configuracao/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Importar User e login
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponseRedirect # Adicionado HttpResponseRedirect
from django.db.models import Prefetch, Q # Para buscas
import logging
from .models import Departamento, DepartamentoCapacidade, DepartamentoMinisterial, DepartamentoVinculo, Igreja, Ministerio, PerfilUsuario, Plano, AssinaturaMinisterio, ProgramacaoPadraoIgreja # Adicionado Plano e AssinaturaMinisterio
from contas.page_permissions import user_can_access_page
from django.conf import settings # Para pegar as chaves do Stripe
import stripe # Importar a biblioteca do Stripe
import django.db.utils # Import django utils
from decimal import Decimal
from datetime import date, timedelta
from .forms import IgrejaForm, MinisterioEditForm, IgrejaEditForm, MinisterioLogosForm, MinisterioCarteirinhaPoliticaForm, ProgramacaoPadraoIgrejaForm, DepartamentoCapacidadesForm, DepartamentoForm, DepartamentoMinisterialForm, DepartamentoVinculoForm # Adicionado IgrejaEditForm
from .utils import pode_editar_configuracao_org # Importa a função
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
# Ajuste o import de get_allowed_churches_for_user se você a moveu para core.utils
from financeiro.utils import get_allowed_churches_for_user # Importar para set_active_church

from core.utils import get_igrejas_selecionaveis, get_ministerio_or_error # Importar de core.utils
from .models import AtualizacaoSistema


from django.utils import timezone # Movido para o topo do arquivo ou garantir que está importado
from datetime import timedelta # Movido para o topo do arquivo ou garantir que está importado

from core.decorators import verificar_assinatura_valida # Ou o caminho correto
from .forms import UserEditForm, PerfilUsuarioEditForm
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.utils.http import url_has_allowed_host_and_scheme
import json

from django.contrib.admin.views.decorators import staff_member_required
from configuracao.models import PerfilUsuario
import boto3
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PerfilUsuario

# Configurar a chave da API do Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
@verificar_assinatura_valida # Nosso novo decorator
def minha_view_protegida(request):
    ministerio = get_ministerio_or_error(request) # Ainda chama para obter o ministério e verificar ministerio.ativo
    # ... resto da view ...


logger = logging.getLogger(__name__)


# Função de teste de permissão (exemplo, adapte à sua lógica)
def pode_editar_configuracao_org(user):
    if not user.is_authenticated:
        return False
    # Exemplo: Admin da Ministério ou um grupo específico pode editar
    return user_is_admin(user) # ou outra lógica


## A função get_ministerio_or_error foi movida para core.utils.py ##


# --- View Principal de Configuração (Lista Igrejas) ---
@login_required
def configuracao_view(request):
    """
    View principal de configuração. Lista as igrejas do ministério do usuário logado.
    """
    try:
        perfil = request.user.perfil
        ministerio = perfil.ministerio
        if not ministerio:
            messages.error(request, "Seu usuário não está associado a nenhuma ministério.")
            # Se for superuser, talvez redirecionar para uma visão geral?
            if request.user.is_superuser:
                return redirect('admin:index') # Ex: para o admin do Django
            return redirect('secretaria:index')

        # Verifica se a ministério está ativa (opcional, mas recomendado)
        if not ministerio.ativo and not request.user.is_superuser:
            messages.warning(request, f'Seu ministério "{ministerio.nome}" ainda não foi aprovado. Algumas funcionalidades podem estar limitadas.')
            # Você pode decidir se limita o acesso aqui ou apenas mostra a mensagem

        igrejas = Igreja.objects.filter(ministerio=ministerio).order_by('tipo_igreja', 'nome_igreja')

        context = {
            'ministerio': ministerio,
            'igrejas': igrejas,
            'ministerio_ativo': ministerio.ativo # Passa o status para o template
        }
        return render(request, 'configuracao/lista_igrejas.html', context)

    except PerfilUsuario.DoesNotExist:
        if request.user.is_superuser:
            messages.info(request, "Como Superusuário, você não tem uma ministério padrão. Use o painel Admin para gerenciar organizações.")
            return redirect('admin:index') # Redireciona superuser para o admin
        else:
            # Situação inesperada: usuário logado sem perfil.
            messages.error(request, "Erro crítico: Perfil de usuário não encontrado. Contate o suporte.")
            # Talvez deslogar o usuário? Ou redirecionar para uma página de erro?
            return redirect('secretaria:index') # Ou para o login?

    except Exception as e:
        messages.error(request, f"Ocorreu um erro inesperado ao carregar as configurações: {e}")
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Erro em configuracao_view") # Corrigido o nome da função no log
        return redirect('secretaria:index')

# --- Views Adicionais (CRUD de Igrejas) ---
@login_required
def lista_igrejas(request):
    """ Lista as igrejas do ministério do usuário logado. """
    ministerio = get_ministerio_or_error(request)
# --- NOVA VERIFICAÇÃO DE GRUPO ---
    grupos_usuario = list(request.user.groups.values_list('name', flat=True))
    logger.debug(f"Usuário {request.user.username} pertence aos grupos: {grupos_usuario}")
    if not user_is_admin(request.user):
        messages.error(request, "Você não tem permissão para gerenciar igrejas.")
        return redirect('secretaria:index') # Ou 'dashboard'
        # --- FIM DA VERIFICAÇÃO ---
    
    
    try:
        igrejas_qs = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')

        # Filtro de busca (opcional)
        query = request.GET.get('q', '')
        if query:
            igrejas_qs = igrejas_qs.filter(
                Q(nome_igreja__icontains=query) |
                Q(cidade__icontains=query) |
                Q(pastor_local__icontains=query)
            )
        
        # Verificar se há membros cadastrados no ministério
        from secretaria.models import Membro
        tem_membros = Membro.objects.filter(igreja__ministerio=ministerio).exists()

        context = {
            'igrejas': igrejas_qs,
            'ministerio': ministerio,
            'current_q': query,
            'tem_membros': tem_membros,  # Adicionar flag
        }
        return render(request, 'configuracao/igrejas/lista_igrejas.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar igrejas para ministério {ministerio.id}")
        messages.error(request, f"Ocorreu um erro ao listar as igrejas: {e}")
        return redirect('secretaria:dashboard')


@login_required
@admin_ministerio_required
def gestao_departamentos_ministeriais(request):
    """Gestão mínima das definições departamentais do ministério em contexto."""
    from django.db.models import Count

    ministerio = get_ministerio_or_error(request)

    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()
        if action == 'criar_departamento_ministerial':
            form = DepartamentoMinisterialForm(request.POST, ministerio=ministerio)
            if form.is_valid():
                from configuracao.services_gestao_departamentos import DepartamentoGestaoService

                try:
                    DepartamentoGestaoService.criar_definicao_ministerial(
                        ministerio=ministerio,
                        dados=form.cleaned_data,
                    )
                except ValidationError as exc:
                    messages.error(request, '; '.join(exc.messages))
                else:
                    messages.success(request, 'Departamento ministerial criado com sucesso.')
            else:
                messages.error(request, 'Não foi possível criar o departamento ministerial. Revise os campos informados.')
        elif action == 'editar_departamento_ministerial':
            departamento = get_object_or_404(
                DepartamentoMinisterial,
                pk=request.POST.get('departamento_ministerial_id'),
                ministerio=ministerio,
            )
            form = DepartamentoMinisterialForm(request.POST, instance=departamento, ministerio=ministerio)
            if form.is_valid():
                from configuracao.services_gestao_departamentos import DepartamentoGestaoService

                try:
                    DepartamentoGestaoService.atualizar_definicao_ministerial(
                        definicao=departamento,
                        ministerio=ministerio,
                        dados=form.cleaned_data,
                    )
                except ValidationError as exc:
                    messages.error(request, '; '.join(exc.messages))
                else:
                    messages.success(request, 'Departamento ministerial atualizado com sucesso.')
            else:
                messages.error(request, 'Não foi possível atualizar o departamento ministerial. Revise os campos informados.')
        return redirect('configuracao:gestao_departamentos_ministeriais')

    departamentos = DepartamentoMinisterial.objects.filter(ministerio=ministerio).annotate(
        total_igrejas_vinculadas=Count('departamentos_locais__igreja', distinct=True),
    ).order_by('ordem', 'nome')
    return render(
        request,
        'configuracao/departamentos/gestao_departamentos_ministeriais.html',
        {
            'ministerio': ministerio,
            'departamentos_ministeriais': departamentos,
            'departamento_ministerial_form': DepartamentoMinisterialForm(ministerio=ministerio),
        },
    )


def _usuario_pode_gerir_departamentos_locais(user):
    """Autoriza somente a gestao estrutural ministerial ou local de departamentos."""
    return user_is_admin(user) or user.groups.filter(
        name__in=[PASTOR_LOCAL, SECRETARIO_LOCAL],
    ).exists()


def _igrejas_para_gestao_departamentos(request, ministerio):
    """Reutiliza o escopo canônico de igrejas, limitado ao Ministério em contexto."""
    igrejas_permitidas = getattr(request, 'igrejas_permitidas', None)
    if igrejas_permitidas is None:
        igrejas_permitidas = get_igrejas_selecionaveis(
            request.user,
            ministerio=ministerio,
        )
    return igrejas_permitidas.filter(ministerio=ministerio)


def _usuario_pode_operar_equipe_departamento(user):
    """Operacao local explicita; administracao ministerial permanece readonly."""
    if user_is_admin(user):
        return False
    return user.groups.filter(name__in=[PASTOR_LOCAL, SECRETARIO_LOCAL]).exists()

@login_required
@user_passes_test_or_403(_usuario_pode_gerir_departamentos_locais)
def gestao_departamentos(request):
    """Tela operacional para gerir departamentos da igreja e habilitacao financeira por departamento."""
    ministerio = get_ministerio_or_error(request)

    allowed_churches = _igrejas_para_gestao_departamentos(request, ministerio)

    if not allowed_churches.exists():
        messages.error(request, 'Nenhuma igreja encontrada para gerenciar departamentos.')
        return redirect('configuracao:lista_igrejas')

    igreja_id = request.GET.get('igreja_id') or request.POST.get('igreja_id')
    igreja_contexto = None

    if igreja_id:
        try:
            igreja_contexto = allowed_churches.filter(pk=int(igreja_id)).first()
        except (TypeError, ValueError):
            igreja_contexto = None
        if igreja_contexto is None:
            raise Http404('Igreja fora do escopo permitido.')

    if igreja_contexto is None and getattr(request, 'igreja_ativa', None):
        igreja_ativa = request.igreja_ativa
        if allowed_churches.filter(pk=igreja_ativa.pk).exists():
            igreja_contexto = igreja_ativa

    if igreja_contexto is None:
        igreja_contexto = allowed_churches.order_by('nome_igreja').first()

    if igreja_contexto is None:
        messages.error(request, 'Nao foi possivel determinar a igreja para gerenciamento de departamentos.')
        return redirect('configuracao:lista_igrejas')

    action_requisitada = (request.POST.get('action') or '').strip()
    from financeiro.models import (
        ContaBancaria,
        DepartamentoCaixa,
        DepartamentoFinanceiro,
        Despesas,
        FechamentoCaixa,
        Receitas,
        FundoDepartamental,
        PoliticaDepartamentoFinanceiro,
    )
    from django.db.models import Sum
    pode_gerir_financeiro_departamentos = user_is_admin(request.user)
    pode_operar_equipe_departamento = _usuario_pode_operar_equipe_departamento(request.user)
    if (
        pode_gerir_financeiro_departamentos
        and action_requisitada not in {
            'ativar_departamento_ministerial',
            'desativar_departamento_ministerial',
        }
    ):
        from financeiro.services import DepartamentoFinanceiroService

        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(igreja_contexto)

    if request.method == 'POST':
        action = action_requisitada

        if action == 'criar_departamento':
            raise PermissionDenied('Departamentos estruturais devem ser criados na Gestao Ministerial.')

        elif action == 'adicionar_vinculo_departamento':
            if not pode_operar_equipe_departamento:
                raise PermissionDenied('A operacao da equipe exige autorizacao local explicita.')
            departamento = get_object_or_404(
                Departamento,
                pk=request.POST.get('departamento_id'),
                igreja=igreja_contexto,
                ativo=True,
            )
            form_vinculo = DepartamentoVinculoForm(request.POST, igreja=igreja_contexto)
            if not form_vinculo.is_valid():
                if 'membro' in form_vinculo.errors or 'cargo' in form_vinculo.errors:
                    raise Http404('Membro ou cargo fora do escopo permitido.')
                messages.error(request, 'Nao foi possivel adicionar o membro. Revise a data informada.')
            else:
                from configuracao.services_departamentos import DepartamentoVinculoService

                try:
                    DepartamentoVinculoService.adicionar(
                        departamento=departamento,
                        membro=form_vinculo.cleaned_data['membro'],
                        cargo=form_vinculo.cleaned_data.get('cargo'),
                        usuario=request.user,
                        data_inicio=form_vinculo.cleaned_data.get('data_inicio'),
                    )
                except ValidationError as exc:
                    messages.error(request, '; '.join(exc.messages))
                else:
                    messages.success(request, 'Membro adicionado a equipe do departamento.')

        elif action == 'encerrar_vinculo_departamento':
            if not pode_operar_equipe_departamento:
                raise PermissionDenied('A operacao da equipe exige autorizacao local explicita.')
            vinculo = get_object_or_404(
                DepartamentoVinculo.objects.select_related('departamento'),
                pk=request.POST.get('vinculo_id'),
                departamento__igreja=igreja_contexto,
                departamento__ativo=True,
                data_fim__isnull=True,
            )
            from configuracao.services_departamentos import DepartamentoVinculoService

            try:
                DepartamentoVinculoService.encerrar(vinculo=vinculo, usuario=request.user)
            except ValidationError as exc:
                messages.error(request, '; '.join(exc.messages))
            else:
                messages.success(request, 'Vinculo encerrado e mantido no historico.')

        elif action == 'editar_departamento':
            departamento_id = request.POST.get('departamento_id')
            departamento = Departamento.objects.filter(pk=departamento_id, igreja=igreja_contexto).first()
            if not departamento:
                messages.error(request, 'Departamento nao encontrado para edicao.')
            elif departamento.departamento_ministerial_id:
                form_capacidades = DepartamentoCapacidadesForm(request.POST)
                if form_capacidades.is_valid():
                    from configuracao.services_gestao_departamentos import DepartamentoGestaoService

                    try:
                        DepartamentoGestaoService.atualizar_capacidades(
                            departamento=departamento,
                            igreja=igreja_contexto,
                            capacidades=form_capacidades.cleaned_data['capacidades'],
                        )
                    except ValidationError as exc:
                        messages.error(request, '; '.join(exc.messages))
                    else:
                        messages.success(request, f'Capacidades locais de "{departamento.nome_exibicao}" atualizadas com sucesso.')
                else:
                    messages.error(request, 'Nao foi possivel atualizar as capacidades locais.')
            else:
                form_edit = DepartamentoForm(
                    request.POST,
                    instance=departamento,
                    igreja=igreja_contexto,
                    permitir_editar_codigo=False,
                )
                if form_edit.is_valid():
                    atualizado = form_edit.save()
                    from configuracao.services_gestao_departamentos import DepartamentoGestaoService

                    try:
                        DepartamentoGestaoService.atualizar_capacidades(
                            departamento=atualizado,
                            igreja=igreja_contexto,
                            capacidades=form_edit.cleaned_data['capacidades'],
                        )
                    except ValidationError as exc:
                        messages.error(request, '; '.join(exc.messages))
                    else:
                        messages.success(request, f'Departamento "{atualizado.nome_exibicao}" atualizado com sucesso.')
                else:
                    messages.error(request, 'Nao foi possivel atualizar o departamento. Revise os campos informados.')

        elif action == 'confirmar_legado_departamento':
            departamento_id = request.POST.get('departamento_id')
            departamento = Departamento.objects.filter(
                pk=departamento_id,
                igreja=igreja_contexto,
                classificacao=Departamento.CLASSIFICACAO_LEGADO_SUGERIDO,
                departamento_ministerial__isnull=True,
            ).first()
            if not departamento:
                messages.error(request, 'Departamento legado nao encontrado para confirmacao.')
            else:
                from configuracao.services_gestao_departamentos import DepartamentoGestaoService

                try:
                    DepartamentoGestaoService.confirmar_legado(
                        departamento=departamento,
                        igreja=igreja_contexto,
                    )
                except ValidationError as exc:
                    messages.error(request, '; '.join(exc.messages))
                else:
                    messages.success(
                        request,
                        f'Departamento "{departamento.nome_exibicao}" confirmado como departamento da igreja.',
                    )

        elif action == 'ativar_departamento_ministerial':
            definicao = get_object_or_404(
                DepartamentoMinisterial.objects.exclude(codigo__in=['LOCAL', 'EVENTOS']),
                pk=request.POST.get('departamento_ministerial_id'),
                ministerio=igreja_contexto.ministerio,
                ativo=True,
            )
            from configuracao.services_gestao_departamentos import DepartamentoGestaoService

            try:
                departamento, _ = DepartamentoGestaoService.ativar_na_igreja(
                    definicao=definicao,
                    igreja=igreja_contexto,
                )
            except ValidationError as exc:
                messages.error(request, '; '.join(exc.messages))
            else:
                messages.success(request, f'Departamento "{departamento.nome_exibicao}" ativado na igreja.')

        elif action == 'desativar_departamento_ministerial':
            departamento = get_object_or_404(
                Departamento,
                pk=request.POST.get('departamento_id'),
                igreja=igreja_contexto,
                departamento_ministerial__isnull=False,
            )
            from configuracao.services_gestao_departamentos import DepartamentoGestaoService

            try:
                DepartamentoGestaoService.desativar_na_igreja(
                    departamento=departamento,
                    igreja=igreja_contexto,
                )
            except ValidationError as exc:
                messages.error(request, '; '.join(exc.messages))
            else:
                messages.success(request, f'Departamento "{departamento.nome_exibicao}" desativado na igreja.')

        elif action == 'salvar_financeiro_departamento':
            if not pode_gerir_financeiro_departamentos:
                raise PermissionDenied('Voce nao tem permissao para configurar o financeiro do departamento.')
            departamento_id = request.POST.get('departamento_id')
            departamento = Departamento.objects.filter(pk=departamento_id, igreja=igreja_contexto).first()
            if not departamento:
                messages.error(request, 'Departamento nao encontrado para configuracao financeira.')
            else:
                habilitar_financeiro = request.POST.get('habilitar_financeiro') == 'on'
                caixa_padrao_id = (request.POST.get('caixa_padrao_id') or '').strip()

                codigo = (departamento.codigo_interno or '').strip().upper()
                padroes = {
                    FundoDepartamental.CODIGO_LOCAL,
                    FundoDepartamental.CODIGO_EVENTOS,
                    FundoDepartamental.CODIGO_MISSOES,
                    FundoDepartamental.CODIGO_ASSISTENCIA,
                }

                fundo_departamental = None
                if codigo in padroes:
                    fundo_departamental, _ = FundoDepartamental.objects.get_or_create(
                        igreja=igreja_contexto,
                        codigo=codigo,
                        defaults={'nome_exibicao': departamento.nome_exibicao, 'ativo': True},
                    )

                dept_financeiro, _ = DepartamentoFinanceiro.objects.get_or_create(
                    igreja=igreja_contexto,
                    codigo_interno=codigo,
                    defaults={
                        'nome_exibicao': departamento.nome_exibicao,
                        'tipo_departamento': DepartamentoFinanceiro.TIPO_PADRAO
                        if departamento.tipo_departamento == Departamento.TIPO_PADRAO
                        else DepartamentoFinanceiro.TIPO_PERSONALIZADO,
                        'ordem_exibicao': departamento.ordem_exibicao,
                        'ativo': True,
                        'departamento': departamento,
                        'fundo_departamental': fundo_departamental,
                    },
                )

                dept_financeiro.nome_exibicao = departamento.nome_exibicao
                dept_financeiro.departamento = departamento
                dept_financeiro.ordem_exibicao = departamento.ordem_exibicao
                dept_financeiro.tipo_departamento = (
                    DepartamentoFinanceiro.TIPO_PADRAO
                    if departamento.tipo_departamento == Departamento.TIPO_PADRAO
                    else DepartamentoFinanceiro.TIPO_PERSONALIZADO
                )
                dept_financeiro.fundo_departamental = fundo_departamental
                dept_financeiro.ativo = habilitar_financeiro
                dept_financeiro.save()

                if caixa_padrao_id:
                    caixa_padrao = ContaBancaria.objects.filter(pk=caixa_padrao_id, igreja=igreja_contexto).first()
                    if caixa_padrao:
                        DepartamentoCaixa.objects.filter(
                            departamento=dept_financeiro,
                            is_padrao=True,
                        ).update(is_padrao=False)

                        vinculo_caixa, _ = DepartamentoCaixa.objects.get_or_create(
                            departamento=dept_financeiro,
                            conta_bancaria=caixa_padrao,
                            defaults={'is_padrao': True, 'ativo': True},
                        )
                        if not vinculo_caixa.ativo or not vinculo_caixa.is_padrao:
                            vinculo_caixa.ativo = True
                            vinculo_caixa.is_padrao = True
                            vinculo_caixa.save(update_fields=['ativo', 'is_padrao'])
                    else:
                        messages.warning(request, 'Caixa padrao informado nao pertence a igreja em contexto.')
                elif request.POST.get('limpar_caixa_padrao') == 'on':
                    DepartamentoCaixa.objects.filter(
                        departamento=dept_financeiro,
                        is_padrao=True,
                    ).update(is_padrao=False)

                politica, _ = PoliticaDepartamentoFinanceiro.objects.get_or_create(
                    departamento=dept_financeiro,
                    defaults={
                        'exige_nota_fiscal': False,
                        'exige_envio_contabilidade': False,
                        'permite_prestacao_local_simplificada': True,
                        'exige_aprovacao_para_saida': False,
                    },
                )

                politica.exige_nota_fiscal = request.POST.get('exige_nota_fiscal') == 'on'
                politica.exige_envio_contabilidade = request.POST.get('exige_envio_contabilidade') == 'on'
                politica.permite_prestacao_local_simplificada = request.POST.get('permite_prestacao_local_simplificada') == 'on'
                politica.exige_aprovacao_para_saida = request.POST.get('exige_aprovacao_para_saida') == 'on'
                politica.save()

                status = 'habilitada' if habilitar_financeiro else 'desabilitada'
                messages.success(
                    request,
                    f'Configuracao financeira do departamento "{departamento.nome_exibicao}" {status} com sucesso.',
                )

        return redirect(f"{reverse('configuracao:gestao_departamentos')}?igreja_id={igreja_contexto.id}")

    departamentos = list(
        Departamento.objects.filter(igreja=igreja_contexto)
        .exclude(classificacao=Departamento.CLASSIFICACAO_CONTEXTO_FINANCEIRO_SISTEMA)
        .prefetch_related('capacidades')
        .order_by('-ativo', 'ordem_exibicao', 'nome_exibicao')
    )
    departamentos_ministeriais_disponiveis = DepartamentoMinisterial.objects.filter(
        ministerio=igreja_contexto.ministerio,
        ativo=True,
    ).exclude(codigo__in=['LOCAL', 'EVENTOS']).exclude(
        pk__in=Departamento.objects.filter(
            igreja=igreja_contexto,
            departamento_ministerial__isnull=False,
        ).values('departamento_ministerial_id')
    ).order_by('ordem', 'nome')
    financeiros_qs = DepartamentoFinanceiro.objects.filter(igreja=igreja_contexto).select_related('departamento', 'politica')
    financeiros_map = {item.departamento_id: item for item in financeiros_qs if item.departamento_id}

    vinculos_equipe_qs = DepartamentoVinculo.objects.filter(
        departamento__in=departamentos,
        data_fim__isnull=True,
    ).select_related('membro', 'cargo').order_by('membro__nome')
    vinculos_equipe_map = {}
    for vinculo_equipe in vinculos_equipe_qs:
        vinculos_equipe_map.setdefault(vinculo_equipe.departamento_id, []).append(vinculo_equipe)

    contas_bancarias_disponiveis = list(
        ContaBancaria.objects.filter(igreja=igreja_contexto).order_by('nome_identificacao')
    )
    vinculos_caixa_qs = DepartamentoCaixa.objects.filter(
        departamento__igreja=igreja_contexto,
        ativo=True,
    ).select_related('conta_bancaria', 'departamento')

    caixas_por_departamento = {}
    caixa_padrao_por_departamento = {}
    for vinculo in vinculos_caixa_qs:
        caixas_por_departamento.setdefault(vinculo.departamento_id, []).append(vinculo)
        if vinculo.is_padrao:
            caixa_padrao_por_departamento[vinculo.departamento_id] = vinculo.conta_bancaria_id

    departamentos_detalhados = []
    departamentos_sem_movimentacao_recente = 0
    for departamento in departamentos:
        capacidades_ativas = {
            capacidade.capacidade
            for capacidade in departamento.capacidades.all()
            if capacidade.ativa
        }
        departamento_financeiro = financeiros_map.get(departamento.id)
        departamento_financeiro_id = departamento_financeiro.id if departamento_financeiro else None
        pendencias_aprovacao_count = 0
        pendencias_aprovacao_total = None
        receitas_total = Decimal('0')
        despesas_total = Decimal('0')
        saldo_departamento = Decimal('0')
        fechamentos_count = 0
        ultimo_fechamento = None
        fechamentos_igreja_count = 0
        ultimo_fechamento_igreja = None
        ultima_movimentacao_em = None
        status_saude = 'neutro'
        status_saude_label = 'Sem financeiro ativo'
        fechamentos_igreja_qs = FechamentoCaixa.objects.filter(igreja=igreja_contexto)
        fechamentos_igreja_count = fechamentos_igreja_qs.count()
        ultimo_fechamento_igreja = fechamentos_igreja_qs.order_by('-data_fechamento').first()
        if departamento_financeiro and departamento_financeiro.fundo_departamental_id:
            receitas_qs = Receitas.objects.filter(
                igreja=igreja_contexto,
                fundo_departamental=departamento_financeiro.fundo_departamental,
            )
            despesas_qs = Despesas.objects.filter(
                igreja=igreja_contexto,
                fundo_departamental=departamento_financeiro.fundo_departamental,
            )
            pendencias_qs = Despesas.objects.filter(
                igreja=igreja_contexto,
                fundo_departamental=departamento_financeiro.fundo_departamental,
                fechado=False,
                aprovacao_status=Despesas.APROVACAO_PENDENTE,
            )
            pendencias_aprovacao_count = pendencias_qs.count()
            pendencias_aprovacao_total = pendencias_qs.aggregate(total=Sum('valor'))['total'] or Decimal('0')
            receitas_total = receitas_qs.aggregate(total=Sum('valor'))['total'] or Decimal('0')
            despesas_total = despesas_qs.aggregate(total=Sum('valor'))['total'] or Decimal('0')
            saldo_departamento = receitas_total - despesas_total
            fechamentos_qs = FechamentoCaixa.objects.filter(
                igreja=igreja_contexto,
                fundo_departamental=departamento_financeiro.fundo_departamental,
            )
            fechamentos_count = fechamentos_qs.count()
            ultimo_fechamento = fechamentos_qs.order_by('-data_fechamento').first()
            ultima_receita = receitas_qs.order_by('-data', '-id').first()
            ultima_despesa = despesas_qs.order_by('-data', '-id').first()
            datas_movimentacao = [item.data for item in [ultima_receita, ultima_despesa] if item and item.data]
            ultima_movimentacao_em = max(datas_movimentacao) if datas_movimentacao else None

            hoje_contexto = date.today()
            if pendencias_aprovacao_count > 0:
                status_saude = 'critico'
                status_saude_label = 'Crítico'
            elif ultima_movimentacao_em and ultima_movimentacao_em < (hoje_contexto - timedelta(days=60)):
                status_saude = 'atencao'
                status_saude_label = 'Atenção'
                departamentos_sem_movimentacao_recente += 1
            elif ultima_movimentacao_em:
                status_saude = 'saudavel'
                status_saude_label = 'Saudável'
            else:
                status_saude = 'atencao'
                status_saude_label = 'Sem movimentação'
                departamentos_sem_movimentacao_recente += 1
        departamentos_detalhados.append(
            {
                'departamento': departamento,
                'capacidades_ativas': capacidades_ativas,
                'departamento_financeiro': departamento_financeiro,
                'caixas_vinculados': caixas_por_departamento.get(departamento_financeiro_id, []),
                'caixa_padrao_id': caixa_padrao_por_departamento.get(departamento_financeiro_id),
                'pendencias_aprovacao_count': pendencias_aprovacao_count,
                'pendencias_aprovacao_total': pendencias_aprovacao_total,
                'receitas_total': receitas_total,
                'despesas_total': despesas_total,
                'saldo_departamento': saldo_departamento,
                'fechamentos_count': fechamentos_count,
                'ultimo_fechamento': ultimo_fechamento,
                'fechamentos_igreja_count': fechamentos_igreja_count,
                'ultimo_fechamento_igreja': ultimo_fechamento_igreja,
                'ultima_movimentacao_em': ultima_movimentacao_em,
                'status_saude': status_saude,
                'status_saude_label': status_saude_label,
                'vinculos_equipe_ativos': vinculos_equipe_map.get(departamento.id, []),
            }
        )

    context = {
        'ministerio': ministerio,
        'igrejas_disponiveis': allowed_churches.order_by('nome_igreja'),
        'igreja_contexto': igreja_contexto,
        'departamentos_detalhados': departamentos_detalhados,
        'departamento_form': DepartamentoForm(igreja=igreja_contexto),
        'contas_bancarias_disponiveis': contas_bancarias_disponiveis,
        'departamentos_sem_movimentacao_recente': departamentos_sem_movimentacao_recente,
        'departamentos_ministeriais_disponiveis': departamentos_ministeriais_disponiveis,
        'pode_gerir_financeiro_departamentos': pode_gerir_financeiro_departamentos,
        'pode_operar_equipe_departamento': pode_operar_equipe_departamento,
        'departamento_vinculo_form': DepartamentoVinculoForm(igreja=igreja_contexto),
        'pode_acessar_pessoas': user_can_access_page(request.user, 'dashboard_secretaria', request=request, igreja=igreja_contexto),
        'pode_acessar_agenda': user_can_access_page(request.user, 'agenda', request=request, igreja=igreja_contexto),
        'pode_acessar_eventos': user_can_access_page(request.user, 'eventos', request=request, igreja=igreja_contexto),
        'pode_acessar_comunicacao': user_can_access_page(request.user, 'comunicacao', request=request, igreja=igreja_contexto),
        'pode_acessar_financeiro': user_can_access_page(request.user, 'financeiro', request=request, igreja=igreja_contexto),
    }
    return render(request, 'configuracao/departamentos/gestao_departamentos.html', context)


@login_required
@admin_ministerio_required
def adicionar_igreja(request):
    """ Cria uma nova igreja para a ministério do usuário. """
    ministerio = get_ministerio_or_error(request)

    if request.method == 'POST' and not ministerio_pode_criar_igreja(ministerio):
        plano = obter_plano_efetivo_ministerio(ministerio)
        limite = plano.limite_igrejas if plano else 1
        messages.error(request, f"Limite de igrejas do seu plano foi atingido ({limite}). Faça upgrade para adicionar mais igrejas.")
        return redirect('configuracao:gerenciar_assinatura')

    if request.method == 'POST':
        form = IgrejaForm(request.POST)
        if form.is_valid():
            igreja = form.save(commit=False)
            igreja.ministerio = ministerio # Associa ao ministério do usuário
            igreja.save()
            
            # Verificar se é a primeira igreja deste ministério
            total_igrejas = Igreja.objects.filter(ministerio=ministerio).count()
            
            if total_igrejas == 1:
                # Primeira igreja: redirecionar para cadastro de membro
                messages.success(request, f'✅ Igreja "{igreja.nome_igreja}" criada com sucesso! Agora cadastre seu primeiro membro para começar a usar o sistema.')
                return redirect('secretaria:cadastrar_membro')
            else:
                # Igrejas subsequentes: volta para lista
                messages.success(request, f'Igreja "{igreja.nome_igreja}" adicionada com sucesso!')
                return redirect('configuracao:lista_igrejas')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            # print("ERROS NO FORMULÁRIO:", form.errors.as_json()) # Removido para produção
    else:
        form = IgrejaForm()

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Adicionar Nova Igreja',
    }
    return render(request, 'configuracao/igrejas/form_igreja.html', context)

@login_required
@admin_ministerio_required
def excluir_igreja(request, pk):
    """ Exclui uma igreja (requer POST e confirmação). """
    ministerio = get_ministerio_or_error(request)
    igreja = get_object_or_404(Igreja, pk=pk, ministerio=ministerio)

    # --- VERIFICAÇÃO IMPORTANTE: Impedir exclusão se tiver dependências ---
    # Verificar se há membros, receitas, despesas, contas a pagar, etc. associados
    if igreja.membros.exists() or \
       igreja.receitas.exists() or \
       igreja.despesas.exists() or \
       igreja.contas_a_pagar_financeiro.exists() or \
       igreja.fechamentos_caixa.exists():
        messages.error(request, f'Não é possível excluir a igreja "{igreja.nome_igreja}", pois ela possui membros ou registros financeiros associados.')
        return redirect('configuracao:lista_igrejas')
    # --- FIM DA VERIFICAÇÃO ---

    if request.method == 'POST':
        try:
            nome_igreja = igreja.nome_igreja
            igreja.delete()
            messages.success(request, f'Igreja "{nome_igreja}" excluída com sucesso!')
        except Exception as e:
            logger.exception(f"Erro ao excluir igreja {pk} para ministério {ministerio.id}")
            messages.error(request, f'Erro ao excluir igreja: {e}')
        return redirect('configuracao:lista_igrejas')
    else:
        # GET: Mostrar página de confirmação
        context = {'igreja': igreja, 'ministerio': ministerio}
        return render(request, 'configuracao/igrejas/confirmar_excluir_igreja.html', context)

# ==================================================
# ========= FIM: VIEWS PARA GERENCIAR IGREJAS =========
# ==================================================

# configuracao/views.py
# ... (imports e views existentes) ...

# ====================================================
# ========= INÍCIO: VIEWS PARA MEU MINISTÉRIO =========
# ====================================================

@login_required
def detalhes_ministerio(request):
    """ Exibe os detalhes do ministério do usuário logado. """
    # A função get_ministerio_or_error já busca a ministério correta
    # e trata os casos de erro (não logado, superuser, sem perfil, sem org)
    ministerio = get_ministerio_or_error(request)
    try:
        aba_ativa = request.POST.get('aba_ativa') or request.GET.get('aba') or 'dados'
        can_edit_logos = is_admin_ministerio(request.user)
        can_edit_carteirinha = is_admin_ministerio(request.user)
        logos_form = MinisterioLogosForm(instance=ministerio)
        carteirinha_form = MinisterioCarteirinhaPoliticaForm(instance=ministerio)

        if request.method == 'POST' and request.POST.get('aba_ativa') == 'logos':
            if not can_edit_logos:
                messages.error(request, 'Você não tem permissão para alterar os logos do ministério.')
                return redirect('configuracao:detalhes_ministerio')

            logos_form = MinisterioLogosForm(request.POST, request.FILES, instance=ministerio)
            if logos_form.is_valid():
                logos_form.save()
                messages.success(request, 'Logos de marketing atualizados com sucesso!')
                return redirect('configuracao:detalhes_ministerio')
            messages.error(request, 'Não foi possível salvar os logos. Revise os campos e tente novamente.')
            aba_ativa = 'logos'

        if request.method == 'POST' and request.POST.get('aba_ativa') == 'carteirinha':
            if not can_edit_carteirinha:
                messages.error(request, 'Você não tem permissão para alterar as políticas da carteirinha.')
                return redirect('configuracao:detalhes_ministerio')

            carteirinha_form = MinisterioCarteirinhaPoliticaForm(request.POST, instance=ministerio)
            if carteirinha_form.is_valid():
                carteirinha_form.save()
                messages.success(request, 'Política de emissão da carteirinha atualizada com sucesso!')
                return redirect('configuracao:detalhes_ministerio')
            messages.error(request, 'Não foi possível salvar a política da carteirinha. Revise os campos e tente novamente.')
            aba_ativa = 'carteirinha'

        context = {
            'ministerio': ministerio,
            'logos_form': logos_form,
            'can_edit_logos': can_edit_logos,
            'carteirinha_form': carteirinha_form,
            'can_edit_carteirinha': can_edit_carteirinha,
            'url_personalizar_carteirinha': reverse('configuracao:carteirinha_ministerio'),
            'aba_ativa': aba_ativa,
        }
        return render(request, 'configuracao/ministerio/detalhes_ministerio.html', context)
    except Exception as e:
        # Captura erro inesperado ao renderizar (menos provável aqui)
        logger.exception(f"Erro ao exibir detalhes do ministério {ministerio.id}")
        messages.error(request, f"Ocorreu um erro ao carregar os detalhes do ministério: {e}")
        return redirect('secretaria:dashboard') # Redireciona para o dashboard principal

# View para editar (a implementar depois)
# @login_required
# --- NOVA VIEW ---
@login_required
@admin_ministerio_required
def editar_ministerio(request):
    """ Permite ao Admin do Minist. editar os dados da sua própria ministério. """
    ministerio = get_ministerio_or_error(request) # Pega a ministério do usuário
    if request.method == 'POST':
    # print(request.FILES) # Removido para produção
        # Passa a instância para editar o objeto correto
        form = MinisterioEditForm(request.POST, request.FILES, instance=ministerio)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Dados do ministério atualizados com sucesso!')
                # Redireciona de volta para a página de detalhes
                return redirect('configuracao:detalhes_ministerio')
            except Exception as e:
                logger.exception(f"Erro ao salvar ministério {ministerio.id}")
                messages.error(request, f'Erro ao salvar dados do ministério: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        # GET: Exibe o formulário preenchido com os dados atuais
        form = MinisterioEditForm(instance=ministerio)

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': f'Editar Ministério: {ministerio.nome_fantasia}'
    }
    # Criaremos um novo template para este formulário
    return render(request, 'configuracao/ministerio/form_ministerio.html', context)
# --- FIM NOVA VIEW ---


@login_required
@verificar_assinatura_valida
def carteirinha_ministerio(request):
    from secretaria.views.carteirinha import _render_carteirinha_premium
    from secretaria.utils import is_secretaria_leader

    if not is_secretaria_leader(request.user):
        messages.error(request, 'Apenas Presidencia ou Secretaria Ministerial podem personalizar carteirinhas.')
        return redirect('secretaria:dashboard')

    return _render_carteirinha_premium(request)


@login_required
@verificar_assinatura_valida
def centro_ministerial(request):
    """
    Dashboard premium do ministério com visão consolidada para presidência/admin.
    """
    from django.db.models import Count, Q, Sum
    from django.utils import timezone
    from secretaria.utils import is_secretaria_leader

    if not (is_admin_ministerio(request.user) or is_secretaria_leader(request.user)):
        messages.error(request, 'Acesso restrito a Presidencia, Secretaria Ministerial ou Admin do Ministerio.')
        return redirect('secretaria:dashboard')

    ministerio = get_ministerio_or_error(request)

    from configuracao.models import Igreja
    from secretaria.models import Membro
    from financeiro.models import ContaPagar, Despesas, FechamentoCaixa
    from eventos.models import Evento
    from contas.models import Convite
    from configuracao.models import Departamento
    from financeiro.models import DepartamentoFinanceiro

    hoje = timezone.localdate()
    agora = timezone.now()
    em_7_dias = hoje + timedelta(days=7)

    igrejas_qs = Igreja.objects.filter(ministerio=ministerio)
    igrejas_total = igrejas_qs.count()
    igrejas_por_tipo = {
        item['tipo_igreja']: item['total']
        for item in igrejas_qs.values('tipo_igreja').annotate(total=Count('id'))
    }

    membros_qs = Membro.objects.filter(igreja__ministerio=ministerio)
    membros_total = membros_qs.count()
    membros_ativos = membros_qs.filter(status_pessoa__nome__iexact='Ativo').count()
    membros_inativos = max(membros_total - membros_ativos, 0)

    contas_pagar_qs = ContaPagar.objects.filter(ministerio=ministerio)
    contas_pendentes = contas_pagar_qs.filter(status='PEN').count()
    contas_vencidas = contas_pagar_qs.filter(status='PEN', data_vencimento__lt=hoje).count()
    contas_vencendo_7d = contas_pagar_qs.filter(
        status='PEN',
        data_vencimento__gte=hoje,
        data_vencimento__lte=em_7_dias,
    ).count()

    eventos_proximos_qs = Evento.objects.filter(
        igreja__ministerio=ministerio,
        status_evento='ativo',
        data_inicio__gte=agora,
        data_inicio__lte=agora + timedelta(days=15),
    ).select_related('igreja').order_by('data_inicio')

    convites_pendentes = Convite.objects.filter(
        ministerio=ministerio,
        status='pendente',
    ).count()

    igrejas_sem_pastor_local = igrejas_qs.filter(
        Q(pastor_local__isnull=True) | Q(pastor_local='')
    ).count()
    igrejas_sem_superior = igrejas_qs.filter(
        tipo_igreja__in=['regional', 'congregacao'],
        igreja_superior__isnull=True,
    ).count()

    ranking_igrejas = list(
        igrejas_qs.annotate(total_membros=Count('membros', distinct=True))
        .order_by('-total_membros', 'nome_igreja')[:8]
    )

    modulos_conectados = [
        {
            'titulo': 'Departamentos',
            'descricao': 'Estrutura organizacional central para criar, ativar e governar cada frente do ministério.',
            'icone': 'fa-layer-group',
            'rota': reverse('configuracao:gestao_departamentos'),
            'cta': 'Abrir Departamentos',
            'relacao': 'Base da operação do ministério.',
        },
        {
            'titulo': 'Secretaria',
            'descricao': 'Pessoas, vínculos, transferências, cargos e acompanhamento da igreja local.',
            'icone': 'fa-users',
            'rota': reverse('secretaria:dashboard'),
            'cta': 'Ir para Secretaria',
            'relacao': 'Conecta membros, equipes e liderança.',
        },
        {
            'titulo': 'Agenda e Eventos',
            'descricao': 'Programação, eventos, convites e celebrações com fluxo operacional unificado.',
            'icone': 'fa-calendar-check',
            'rota': reverse('agenda:agenda'),
            'cta': 'Abrir Agenda',
            'relacao': 'Cada departamento pode gerar eventos e escalas.',
        },
        {
            'titulo': 'Escola Bíblica',
            'descricao': 'Turmas, lições, frequência e acompanhamento de formação por igreja.',
            'icone': 'fa-book-open',
            'rota': reverse('escola_biblica:dashboard'),
            'cta': 'Abrir EBD',
            'relacao': 'Departamentos alimentam turmas e responsabilidades.',
        },
        {
            'titulo': 'Comunicação',
            'descricao': 'Avisos, campanhas, e-mail e WhatsApp com segmentação por contexto ministerial.',
            'icone': 'fa-comments',
            'rota': reverse('comunicacao:home'),
            'cta': 'Abrir Comunicação',
            'relacao': 'Distribui mensagens para membros e líderes.',
        },
        {
            'titulo': 'Financeiro',
            'descricao': 'Receitas, despesas, caixas e prestação de contas por igreja e departamento.',
            'icone': 'fa-landmark',
            'rota': reverse('financeiro:painel_financeiro'),
            'cta': 'Abrir Financeiro',
            'relacao': 'Camada de governança e prestação.',
        },
    ]

    departamentos_qs = Departamento.objects.filter(igreja__ministerio=ministerio)
    departamentos_financeiros_qs = DepartamentoFinanceiro.objects.filter(igreja__ministerio=ministerio)
    departamentos_total = departamentos_qs.count()
    departamentos_ativos = departamentos_qs.filter(ativo=True).count()
    departamentos_financeiros_ativos = departamentos_financeiros_qs.filter(ativo=True).count()
    igrejas_com_departamentos = igrejas_qs.filter(departamentos__isnull=False).distinct().count()
    despesas_pendentes_aprovacao_qs = Despesas.objects.filter(
        igreja__ministerio=ministerio,
        fechado=False,
        aprovacao_status=Despesas.APROVACAO_PENDENTE,
    )
    pendencias_aprovacao_departamental = despesas_pendentes_aprovacao_qs.count()
    valor_pendencias_aprovacao_departamental = despesas_pendentes_aprovacao_qs.aggregate(total=Sum('valor'))['total'] or Decimal('0')
    fechamentos_abertos_qs = FechamentoCaixa.objects.filter(igreja__ministerio=ministerio, status='aberto')
    fechamentos_abertos_count = fechamentos_abertos_qs.count()
    departamentos_sem_financeiro_ativo = max(departamentos_ativos - departamentos_financeiros_ativos, 0)
    ranking_departamentos_pendentes = list(
        departamentos_financeiros_qs.filter(fundo_departamental__isnull=False)
        .annotate(
            pendencias_qtd=Count(
                'fundo_departamental__despesas',
                filter=Q(
                    fundo_departamental__despesas__fechado=False,
                    fundo_departamental__despesas__aprovacao_status=Despesas.APROVACAO_PENDENTE,
                ),
                distinct=True,
            ),
            pendencias_total=Sum(
                'fundo_departamental__despesas__valor',
                filter=Q(
                    fundo_departamental__despesas__fechado=False,
                    fundo_departamental__despesas__aprovacao_status=Despesas.APROVACAO_PENDENTE,
                ),
            ),
        )
        .filter(pendencias_qtd__gt=0)
        .select_related('igreja', 'fundo_departamental')
        .order_by('-pendencias_qtd', '-pendencias_total', 'nome_exibicao')[:5]
    )

    pendencias = []
    if contas_vencidas > 0:
        pendencias.append({
            'nivel': 'critico',
            'icone': 'fa-exclamation-triangle',
            'titulo': 'Contas vencidas',
            'descricao': f'{contas_vencidas} conta(s) pendente(s) com vencimento expirado.',
            'acao_url': reverse('financeiro:lista_contas_pagar'),
            'acao_texto': 'Regularizar contas',
        })
    if contas_vencendo_7d > 0:
        pendencias.append({
            'nivel': 'atencao',
            'icone': 'fa-calendar-day',
            'titulo': 'Vencimentos da semana',
            'descricao': f'{contas_vencendo_7d} conta(s) vencem nos proximos 7 dias.',
            'acao_url': reverse('financeiro:lista_contas_pagar'),
            'acao_texto': 'Planejar pagamentos',
        })
    if igrejas_sem_pastor_local > 0:
        pendencias.append({
            'nivel': 'atencao',
            'icone': 'fa-user-slash',
            'titulo': 'Igrejas sem responsavel local',
            'descricao': f'{igrejas_sem_pastor_local} igreja(s) sem Pastor Local informado.',
            'acao_url': reverse('configuracao:lista_igrejas'),
            'acao_texto': 'Atualizar estrutura',
        })
    if igrejas_sem_superior > 0:
        pendencias.append({
            'nivel': 'info',
            'icone': 'fa-project-diagram',
            'titulo': 'Estrutura hierarquica incompleta',
            'descricao': f'{igrejas_sem_superior} regional/congregacao sem igreja superior definida.',
            'acao_url': reverse('configuracao:lista_igrejas'),
            'acao_texto': 'Ajustar hierarquia',
        })
    if convites_pendentes > 0:
        pendencias.append({
            'nivel': 'info',
            'icone': 'fa-user-clock',
            'titulo': 'Convites pendentes',
            'descricao': f'{convites_pendentes} convite(s) aguardando aceite de usuario.',
            'acao_url': reverse('contas:lista_usuarios'),
            'acao_texto': 'Gerenciar convites',
        })
    if not pendencias:
        pendencias.append({
            'nivel': 'ok',
            'icone': 'fa-check-circle',
            'titulo': 'Operacao em dia',
            'descricao': 'Nenhuma pendencia critica detectada no momento.',
            'acao_url': reverse('secretaria:dashboard'),
            'acao_texto': 'Abrir dashboard local',
        })

    departamentos_principais = list(
        departamentos_qs.select_related('igreja')
        .order_by('igreja__nome_igreja', 'ordem_exibicao', 'nome_exibicao')[:6]
    )

    context = {
        'ministerio': ministerio,
        'igrejas_total': igrejas_total,
        'igrejas_por_tipo': igrejas_por_tipo,
        'membros_total': membros_total,
        'membros_ativos': membros_ativos,
        'membros_inativos': membros_inativos,
        'contas_pendentes': contas_pendentes,
        'contas_vencidas': contas_vencidas,
        'contas_vencendo_7d': contas_vencendo_7d,
        'eventos_proximos': list(eventos_proximos_qs[:8]),
        'convites_pendentes': convites_pendentes,
        'ranking_igrejas': ranking_igrejas,
        'modulos_conectados': modulos_conectados,
        'pendencias': pendencias,
        'atualizado_em': agora,
        'departamentos_total': departamentos_total,
        'departamentos_ativos': departamentos_ativos,
        'departamentos_financeiros_ativos': departamentos_financeiros_ativos,
        'igrejas_com_departamentos': igrejas_com_departamentos,
        'departamentos_principais': departamentos_principais,
        'pendencias_aprovacao_departamental': pendencias_aprovacao_departamental,
        'valor_pendencias_aprovacao_departamental': valor_pendencias_aprovacao_departamental,
        'fechamentos_abertos_count': fechamentos_abertos_count,
        'departamentos_sem_financeiro_ativo': departamentos_sem_financeiro_ativo,
        'ranking_departamentos_pendentes': ranking_departamentos_pendentes,
    }
    return render(request, 'configuracao/ministerio/centro_ministerial.html', context)

#     ministerio = get_ministerio_or_error(request)
#     # ... lógica GET/POST com MinisterioEditForm ...
#     pass

# ==================================================
# ========= FIM: VIEWS PARA MEU MINISTÉRIO =========
# ==================================================




@login_required
@user_passes_test_or_403(pode_editar_configuracao_org) # Proteja a view
def _render_editar_igreja_config_page(
    request,
    ministerio,
    igreja,
    form=None,
    programacao_form=None,
    status_code=200,
):
    if form is None:
        form = IgrejaEditForm(instance=igreja, ministerio=ministerio)
    if programacao_form is None:
        programacao_form = ProgramacaoPadraoIgrejaForm(igreja=igreja)

    from django.db.models import Count, Exists, OuterRef, Q
    from django.utils import timezone
    from escola_biblica.models import Classe, Frequencia, Turma
    ebd_classes_igreja = (
        Classe.objects.filter(igreja=igreja)
        .annotate(total_turmas=Count('turma', distinct=True))
        .order_by('nome')
    )
    hoje = timezone.localdate()
    chamada_hoje_subquery = Frequencia.objects.filter(
        aluno__turma_id=OuterRef('pk'),
        data=hoje,
    )
    ebd_turmas_igreja = (
        Turma.objects.filter(igreja=igreja)
        .select_related('classe', 'ano_letivo')
        .annotate(
            matriculados_ativos=Count('alunos', filter=Q(alunos__ativo=True), distinct=True),
            chamada_hoje=Exists(chamada_hoje_subquery),
        )
        .order_by('nome')
    )
    ebd_turmas_com_chamada_hoje = ebd_turmas_igreja.filter(chamada_hoje=True).count()
    ebd_turmas_pendentes_hoje = ebd_turmas_igreja.filter(chamada_hoje=False).count()

    context = {
        'form': form,
        'igreja': igreja,
        'titulo_pagina': f"Editar Igreja: {igreja.nome_igreja}",
        'cnpj_ministerio': ministerio.cnpj if hasattr(ministerio, 'cnpj') and ministerio.cnpj else '',
        'programacao_form': programacao_form,
        'programacoes_padrao': ProgramacaoPadraoIgreja.objects.filter(igreja=igreja).order_by('ordem', 'dia_semana', 'hora_inicio'),
        'ebd_classes_igreja': ebd_classes_igreja[:8],
        'ebd_classes_total': ebd_classes_igreja.count(),
        'ebd_turmas_igreja': ebd_turmas_igreja[:8],
        'ebd_turmas_total': ebd_turmas_igreja.count(),
        'ebd_turmas_com_chamada_hoje': ebd_turmas_com_chamada_hoje,
        'ebd_turmas_pendentes_hoje': ebd_turmas_pendentes_hoje,
    }
    return render(request, 'configuracao/igrejas/editar_igreja_config.html', context, status=status_code)


@login_required
@user_passes_test_or_403(pode_editar_configuracao_org) # Proteja a view
def editar_igreja_config(request, igreja_id): # Renomeei para evitar conflito com outras views editar_igreja
    ministerio = get_ministerio_or_error(request) # Usar a função auxiliar
    # Garante que a igreja a ser editada pertence à ministério do usuário
    igreja = get_object_or_404(Igreja, pk=igreja_id, ministerio=ministerio)

    if request.method == 'POST':
        form = IgrejaEditForm(request.POST, request.FILES, instance=igreja, ministerio=ministerio)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dados da igreja '{igreja.nome_igreja}' atualizados com sucesso!")
            return redirect('configuracao:editar_igreja_config', igreja_id=igreja.id)

        messages.error(request, "Erro ao atualizar os dados da igreja. Verifique os campos.")
        return _render_editar_igreja_config_page(request, ministerio, igreja, form=form, status_code=400)

    return _render_editar_igreja_config_page(request, ministerio, igreja)


@login_required
@user_passes_test_or_403(pode_editar_configuracao_org)
def adicionar_programacao_padrao_igreja(request, igreja_id):
    ministerio = get_ministerio_or_error(request)
    igreja = get_object_or_404(Igreja, pk=igreja_id, ministerio=ministerio)

    if request.method != 'POST':
        return redirect('configuracao:editar_igreja_config', igreja_id=igreja.id)

    form = ProgramacaoPadraoIgrejaForm(request.POST, igreja=igreja)
    if form.is_valid():
        programacao = form.save(commit=False)
        programacao.igreja = igreja
        programacao.save()

        from configuracao.services_programacao import sync_programacao_padrao
        sync_programacao_padrao(programacao)

        messages.success(request, 'Programação padrão cadastrada e sincronizada na agenda.')
        return redirect(f"{reverse('configuracao:editar_igreja_config', args=[igreja.id])}?aba=programacoes")

    messages.error(request, 'Não foi possível salvar a programação padrão. Veja abaixo os campos que precisam de ajuste.')
    form_igreja = IgrejaEditForm(instance=igreja, ministerio=ministerio)
    return _render_editar_igreja_config_page(
        request,
        ministerio,
        igreja,
        form=form_igreja,
        programacao_form=form,
        status_code=400,
    )


@login_required
@user_passes_test_or_403(pode_editar_configuracao_org)
def excluir_programacao_padrao_igreja(request, igreja_id, programacao_id):
    ministerio = get_ministerio_or_error(request)
    igreja = get_object_or_404(Igreja, pk=igreja_id, ministerio=ministerio)
    programacao = get_object_or_404(ProgramacaoPadraoIgreja, pk=programacao_id, igreja=igreja)

    if request.method == 'POST':
        from eventos.models import Evento

        Evento.objects.filter(
            igreja=igreja,
            programacao_padrao=programacao,
            data_inicio__date__gte=timezone.localdate(),
            status_evento='ativo',
        ).delete()
        programacao.delete()
        messages.success(request, 'Programação padrão removida com sucesso.')

    return redirect(f"{reverse('configuracao:editar_igreja_config', args=[igreja.id])}?aba=programacoes")


@login_required
@user_passes_test_or_403(pode_editar_configuracao_org)
def sincronizar_programacoes_padrao_igreja(request, igreja_id):
    ministerio = get_ministerio_or_error(request)
    igreja = get_object_or_404(Igreja, pk=igreja_id, ministerio=ministerio)

    if request.method == 'POST':
        from configuracao.services_programacao import sync_programacoes_igreja

        total = sync_programacoes_igreja(igreja)
        messages.success(request, f'Sincronização concluída. {total} programação(ões) processada(s).')

    return redirect(f"{reverse('configuracao:editar_igreja_config', args=[igreja.id])}?aba=programacoes")


# Adicione esta view ao seu c:\Gereigreja\configuracao\views.py
# Certifique-se de importar IgrejaEditForm (ou um IgrejaCreateForm se preferir)
# e outras dependências como login_required, user_passes_test, messages, redirect, etc.
# from django.utils import timezone # Adicionado para gerenciar_assinatura
# from .utils import pode_editar_configuracao_org (ou uma permissão similar)

@login_required
@user_passes_test_or_403(pode_editar_configuracao_org) # Use a permissão apropriada
def adicionar_igreja(request):
    ministerio = get_ministerio_or_error(request) # Usar a função auxiliar

    if request.method == 'POST' and not ministerio_pode_criar_igreja(ministerio):
        plano = obter_plano_efetivo_ministerio(ministerio)
        limite = plano.limite_igrejas if plano else 1
        messages.error(request, f"Limite de igrejas do seu plano foi atingido ({limite}). Faça upgrade para adicionar mais igrejas.")
        return redirect('configuracao:gerenciar_assinatura')

    if request.method == 'POST':
        # Se você usar IgrejaEditForm, ele tentará pegar uma 'instance'.
        # Para criação, é melhor não passar 'instance'.
        # Você pode criar um IgrejaCreateForm que não exija 'instance'
        # ou adaptar o IgrejaEditForm para lidar com criação.
        # Por simplicidade, vamos assumir que IgrejaEditForm pode ser usado para criar se instance=None
        form = IgrejaForm(request.POST, request.FILES, ministerio=ministerio) # Usando IgrejaForm para criação
        if form.is_valid():
            nova_igreja = form.save(commit=False)
            nova_igreja.ministerio = ministerio # Garante que a ministério está definida
            nova_igreja.save()
            # messages.success(request, f"Igreja '{nova_igreja.nome_igreja}' adicionada com sucesso!") # Comentado para evitar duplicidade
            return redirect('configuracao:lista_igrejas')
        else:
            messages.error(request, "Erro ao adicionar igreja. Verifique os campos.")
    else:
        form = IgrejaEditForm(ministerio=ministerio) # Formulário vazio para criação


    context = { # Corrigido: 'form' deve ser o objeto do formulário
        'form': form, # Corrigido
        'titulo_pagina': "Adicionar Nova Igreja",
        'ministerio': ministerio # Adicionado para o template ter acesso
    }
   
    # Você precisará de um template para adicionar igreja, ex: 'configuracao/igreja/adicionar_igreja.html'
    return render(request, 'configuracao/igrejas/form_igreja.html', context) # Reutilizando form_igreha.html




def _igrejas_operacionais_meus_departamentos(user):
    """Retorna o escopo aditivo de atalhos da visao pessoal de departamentos.

    Vínculos ativos continuam visíveis independentemente deste escopo. O conjunto
    abaixo limita somente atalhos operacionais e não usa o escopo hierárquico
    legado nem o seletor global de igrejas.
    """
    perfil = getattr(user, 'perfil', None) or getattr(user, 'perfil_usuario', None)
    if not perfil or not perfil.ministerio_id:
        return set()

    igrejas_ids = set()
    if user.groups.filter(name__in=[PASTOR_LOCAL, SECRETARIO_LOCAL]).exists():
        igrejas_ids.update(
            perfil.igrejas_permitidas.filter(
                ministerio_id=perfil.ministerio_id,
            ).values_list('pk', flat=True)
        )

    if user_is_admin(user):
        igrejas_ids.update(
            Igreja.objects.filter(
                ministerio_id=perfil.ministerio_id,
                tipo_igreja__in=['sede', 'independente'],
            ).values_list('pk', flat=True)
        )

    return igrejas_ids


def _atalhos_permitidos_departamento(
    request,
    departamento,
    capacidades_ativas,
    igrejas_operacionais_ids,
    autorizacoes_cache,
):
    """Monta atalhos sem transformar vinculo ou capacidade em autorizacao."""
    igreja = departamento.igreja
    if igreja.pk not in igrejas_operacionais_ids:
        return []

    definicoes = {
        DepartamentoCapacidade.PESSOAS: ('dashboard_secretaria', 'Pessoas', 'secretaria:dashboard'),
        DepartamentoCapacidade.AGENDA: ('agenda', 'Agenda', 'agenda:agenda'),
        DepartamentoCapacidade.EVENTOS: ('eventos', 'Eventos', 'eventos:lista_eventos'),
        DepartamentoCapacidade.COMUNICACAO: ('comunicacao', 'Comunicacao', 'comunicacao:home'),
    }
    atalhos = []
    for capacidade, (pagina, rotulo, rota) in definicoes.items():
        if capacidade not in capacidades_ativas:
            continue
        chave_autorizacao = (pagina, igreja.pk)
        if chave_autorizacao not in autorizacoes_cache:
            autorizacoes_cache[chave_autorizacao] = user_can_access_page(
                request.user,
                pagina,
                request=request,
                igreja=igreja,
            )
        if autorizacoes_cache[chave_autorizacao]:
            atalhos.append({'rotulo': rotulo, 'url': reverse(rota)})

    chave_financeiro = ('financeiro', igreja.pk)
    if DepartamentoCapacidade.FINANCEIRO in capacidades_ativas:
        if chave_financeiro not in autorizacoes_cache:
            autorizacoes_cache[chave_financeiro] = user_can_access_page(
                request.user,
                'financeiro',
                request=request,
                igreja=igreja,
            )
        if not autorizacoes_cache[chave_financeiro]:
            return atalhos
        atalhos.append(
            {
                'rotulo': 'Financeiro',
                'url': f"{reverse('financeiro:painel_financeiro')}?igreja_filtro={igreja.pk}",
            }
        )
    return atalhos


@login_required
@require_GET
def meus_departamentos(request):
    """Visao pessoal e somente leitura dos vinculos departamentais ativos."""
    pessoa = getattr(request.user, 'membro_secretaria', None)
    vinculos = []
    if pessoa is not None:
        capacidades_ativas_qs = DepartamentoCapacidade.objects.filter(ativa=True).order_by('capacidade')
        vinculos = list(
            DepartamentoVinculo.objects.filter(membro=pessoa, data_fim__isnull=True)
            .select_related('departamento__igreja__ministerio', 'cargo')
            .prefetch_related(
                Prefetch(
                    'departamento__capacidades',
                    queryset=capacidades_ativas_qs,
                    to_attr='capacidades_ativas_meus_departamentos',
                )
            )
            .order_by('departamento__igreja__nome_igreja', 'departamento__nome_exibicao')
        )

    itens = []
    for vinculo in vinculos:
        capacidades = vinculo.departamento.capacidades_ativas_meus_departamentos
        capacidades_codigos = {capacidade.capacidade for capacidade in capacidades}
        itens.append(
            {
                'vinculo': vinculo,
                'capacidades': capacidades,
                'capacidades_codigos': capacidades_codigos,
            }
        )

    igrejas_operacionais_ids = _igrejas_operacionais_meus_departamentos(request.user)

    autorizacoes_cache = {}
    for item in itens:
        item['atalhos'] = _atalhos_permitidos_departamento(
            request,
            item['vinculo'].departamento,
            item.pop('capacidades_codigos'),
            igrejas_operacionais_ids,
            autorizacoes_cache,
        )

    return render(
        request,
        'configuracao/departamentos/meus_departamentos.html',
        {'departamentos_itens': itens},
    )


def _anotar_tipo_planos(planos, plano_efetivo, pessoas_ativas=0, igrejas_ativas=0):
    """Retorna lista de dicts com tipo e flags de limite excedido."""
    efetivo_ordem = plano_efetivo.ordem_liberacao if plano_efetivo else None
    efetivo_id = plano_efetivo.id if plano_efetivo else None
    primeiro_upgrade_encontrado = False
    resultado = []
    for p in planos:
        if p.id == efetivo_id:
            tipo = 'atual'
        elif efetivo_ordem is not None and p.ordem_liberacao > efetivo_ordem:
            if not primeiro_upgrade_encontrado:
                tipo = 'recomendado'
                primeiro_upgrade_encontrado = True
            else:
                tipo = 'upgrade'
        else:
            tipo = 'downgrade'
        excede_pessoas = bool(p.limite_membros and p.limite_membros > 0 and pessoas_ativas > p.limite_membros)
        excede_igrejas = bool(p.limite_igrejas and p.limite_igrejas > 0 and igrejas_ativas > p.limite_igrejas)
        resultado.append({
            'plano': p,
            'tipo': tipo,
            'excede_pessoas': excede_pessoas,
            'excede_igrejas': excede_igrejas,
            'excede_algum': excede_pessoas or excede_igrejas,
        })
    return resultado


def _registrar_historico_mensalidade(
    ministerio,
    plano,
    valor,
    data_inicio,
    data_fim=None,
    observacao='',
):
    """Registra mensalidade no histórico com deduplicação por observação Stripe."""
    from configuracao.models import HistoricoAssinatura

    observacao = (observacao or '').strip()
    if observacao:
        ja_existe = HistoricoAssinatura.objects.filter(
            ministerio=ministerio,
            tipo='mensalidade',
            observacao=observacao,
        ).exists()
        if ja_existe:
            return

    HistoricoAssinatura.objects.create(
        ministerio=ministerio,
        plano=plano,
        tipo='mensalidade',
        valor=valor,
        status='paga',
        data_inicio=data_inicio,
        data_fim=data_fim,
        observacao=observacao or None,
    )


@login_required
def gerenciar_assinatura(request):
    """
    Permite ao administrador do ministério visualizar os planos disponíveis,
    ver sua assinatura atual e escolher/alterar um plano.
    """
    ministerio = get_ministerio_or_error(request)
    assinatura_atual = AssinaturaMinisterio.objects.filter(ministerio=ministerio).order_by('-data_inicio').first()

    # Reconciliacao de sucesso de checkout para cobrir atraso/falha de webhook.
    checkout_status = request.GET.get('status')
    checkout_session_id = request.GET.get('session_id', '').strip()
    if checkout_status == 'success' and checkout_session_id:
        try:
            session = stripe.checkout.Session.retrieve(
                checkout_session_id,
                expand=['subscription', 'subscription.latest_invoice'],
            )
            metadata = session.get('metadata', {}) or {}
            if str(metadata.get('ministerio_id', '')) == str(ministerio.id):
                plano_id = metadata.get('plano_id')
                ciclo_pagamento = metadata.get('ciclo_pagamento')
                plano_checkout = Plano.objects.filter(id=plano_id).first()
                if plano_checkout and ciclo_pagamento in ('mensal', 'anual'):
                    data_inicio = timezone.now()
                    subscription_obj = session.get('subscription') or {}
                    current_period_end = subscription_obj.get('current_period_end')
                    data_fim = data_inicio + (timedelta(days=365) if ciclo_pagamento == 'anual' else timedelta(days=30))
                    if current_period_end:
                        from datetime import datetime

                        dt = datetime.fromtimestamp(current_period_end)
                        data_fim = timezone.make_aware(dt, timezone.get_current_timezone()) if timezone.is_naive(dt) else dt

                    assinatura_atual, _ = AssinaturaMinisterio.objects.update_or_create(
                        ministerio=ministerio,
                        defaults={
                            'plano': plano_checkout,
                            'data_inicio': data_inicio,
                            'data_fim': data_fim,
                            'ciclo_pagamento': ciclo_pagamento,
                            'status': 'ativa',
                            'periodo_cortesia_ativo': False,
                            'trial_ativo': False,
                            'tentativas_falha_pagamento': 0,
                            'data_fim_graca_inadimplencia': None,
                            'id_transacao_gateway': session.get('subscription'),
                        },
                    )

                    stripe_customer_id = session.get('customer')
                    if stripe_customer_id and ministerio.stripe_customer_id != stripe_customer_id:
                        ministerio.stripe_customer_id = stripe_customer_id
                        ministerio.save(update_fields=['stripe_customer_id'])

                    amount_total = session.get('amount_total')
                    valor_pago = Decimal('0.00')
                    if amount_total is not None:
                        valor_pago = (Decimal(str(amount_total)) / Decimal('100')).quantize(Decimal('0.01'))

                    invoice_obj = (subscription_obj or {}).get('latest_invoice') or {}
                    invoice_id = invoice_obj.get('id')
                    obs = f"Checkout Stripe confirmado. session_id={checkout_session_id}; invoice_id={invoice_id or 'n/a'}"
                    _registrar_historico_mensalidade(
                        ministerio=ministerio,
                        plano=plano_checkout,
                        valor=valor_pago,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        observacao=obs,
                    )
        except Exception as exc:
            logger.warning(f"Falha na reconciliacao de checkout success para ministerio {ministerio.id}: {exc}")

    # --- VERIFICAR EXPIRAÇÃO DE GRACE PERIOD ---
    if assinatura_atual and assinatura_atual.status == 'pendente_pagamento' and assinatura_atual.data_fim_graca_inadimplencia:
        if timezone.now() > assinatura_atual.data_fim_graca_inadimplencia:
            # Grace period expirou: downgrade automático para Pioneiro
            try:
                plano_pioneiro = Plano.objects.get(codigo_plano='pioneiro')
                assinatura_atual.plano = plano_pioneiro
                assinatura_atual.status = 'gratuita'
                assinatura_atual.tentativas_falha_pagamento = 0  # Reset contador
                assinatura_atual.data_fim_graca_inadimplencia = None
                assinatura_atual.save(update_fields=['plano', 'status', 'tentativas_falha_pagamento', 'data_fim_graca_inadimplencia'])
                logger.info(f"Grace period expirado para {ministerio.nome_fantasia}. Downgrade para Pioneiro.")
                messages.info(request, "Seu período de carência expirou. Você foi downgradeado para o plano Pioneiro. Regularize seu pagamento para continuar com o plano anterior.")
            except Plano.DoesNotExist:
                logger.error(f"Plano Pioneiro não encontrado ao processar expiração de grace period para {ministerio.id}.")

    # --- VERIFICAR EXPIRAÇÃO DE TRIAL ---
    if assinatura_atual and assinatura_atual.trial_ativo and assinatura_atual.data_inicio_trial:
        dias_trial = assinatura_atual.dias_trial_totais or 14
        data_fim_trial = assinatura_atual.data_inicio_trial + timedelta(days=dias_trial)
        if timezone.now() >= data_fim_trial:
            try:
                plano_pioneiro = Plano.objects.get(codigo_plano='pioneiro')
                assinatura_atual.plano = plano_pioneiro
                assinatura_atual.status = 'gratuita'
                assinatura_atual.trial_ativo = False
                assinatura_atual.save(update_fields=['plano', 'status', 'trial_ativo'])
                messages.info(request, "Seu trial de 14 dias terminou. Você foi movido para o plano Pioneiro.")
            except Plano.DoesNotExist:
                logger.error(f"Plano Pioneiro não encontrado ao processar expiração de trial para {ministerio.id}.")

    # Verifica se o plano gratuito está ativo e o limite foi excedido
    if assinatura_atual and assinatura_atual.status == 'gratuita' and assinatura_atual.plano and assinatura_atual.plano.preco_mensal == 0:
        total_membros = 0
        for igreja in ministerio.igrejas.all():
            total_membros += igreja.membros.count()
        if assinatura_atual.plano.limite_membros and total_membros > assinatura_atual.plano.limite_membros:
            assinatura_atual.status = 'vencida'
            assinatura_atual.save()

    planos_disponiveis = listar_planos_para_ministerio(ministerio)

    # Fallback: se a assinatura está irregular, amplia a vitrine para facilitar
    # a regularização (inclusive quando só 1 plano veio da allowlist).
    status_irregular = not assinatura_atual or assinatura_atual.status not in ('ativa', 'gratuita')
    if status_irregular and len(planos_disponiveis) <= 1:
        planos_disponiveis = list(
            Plano.objects.filter(ativo=True, is_visible=True).order_by('ordem_liberacao', 'preco_mensal')
        )

    mostrar_opcao_cortesia = False
    mostrar_opcao_trial = False

    # Consulta histórico de mensalidades e cortesias
    historico_assinatura = ministerio.historicos_assinatura.select_related('plano').order_by('-data_inicio')

    if request.method == 'POST':
        # --- LÓGICA PARA ATIVAR TRIAL DE 14 DIAS ---
        if request.POST.get('ativar_trial') == 'true':
            if assinatura_atual and assinatura_atual.data_inicio_trial:
                messages.warning(request, "Seu ministério já utilizou o período de trial anteriormente.")
                return redirect('configuracao:gerenciar_assinatura')

            assinatura_trial = iniciar_trial(ministerio)
            plano_nome = assinatura_trial.plano.get_nome_display() if assinatura_trial.plano else 'atual'
            messages.success(request, f"Trial de 14 dias ativado com sucesso no plano {plano_nome}!")
            return redirect('configuracao:gerenciar_assinatura')

        # --- LÓGICA PARA ATIVAR CORTESIA ---
        if request.POST.get('ativar_cortesia') == 'true':
            # Só permite cortesia se não há cortesia válida e houve pagamento após a última cortesia
            ultima_cortesia = ministerio.historicos_assinatura.filter(tipo='cortesia').order_by('-data_inicio').first()
            ultimo_pagamento = ministerio.historicos_assinatura.filter(tipo='mensalidade', status='paga').order_by('-data_inicio').first()
            pode_ativar = False
            if assinatura_atual and assinatura_atual.status == 'vencida' and not assinatura_atual.is_periodo_cortesia_valido():
                if not ultima_cortesia or (ultimo_pagamento and ultimo_pagamento.data_inicio > ultima_cortesia.data_fim):
                    pode_ativar = True
            if pode_ativar:
                assinatura_atual.periodo_cortesia_ativo = True
                assinatura_atual.data_inicio_cortesia = timezone.now()
                assinatura_atual.save()
                # Registrar evento no histórico
                from configuracao.models import HistoricoAssinatura
                HistoricoAssinatura.objects.create(
                    ministerio=ministerio,
                    plano=assinatura_atual.plano,
                    tipo='cortesia',
                    valor=0.00,
                    status='a_vencer',
                    data_inicio=assinatura_atual.data_inicio_cortesia,
                    data_fim=assinatura_atual.data_inicio_cortesia + timedelta(days=3),
                    observacao='Cortesia ativada automaticamente.'
                )
                messages.success(request, "Período de cortesia de 3 dias ativado! Você pode usar o sistema normalmente.")
                return redirect('configuracao:gerenciar_assinatura')
            else:
                messages.error(request, "Não foi possível ativar o período de cortesia. É necessário realizar um pagamento antes de ativar nova cortesia.")
            return redirect('configuracao:gerenciar_assinatura')
        # --- FIM LÓGICA CORTESIA ---
        plano_id_selecionado = request.POST.get('plano_id')
        ciclo_pagamento_selecionado = request.POST.get('ciclo_pagamento') # 'mensal' ou 'anual'
        stripe_coupon = request.POST.get('stripe_coupon', '').strip()
        
        if not plano_id_selecionado or not ciclo_pagamento_selecionado:
            messages.error(request, "Nenhum plano foi selecionado.")
            return redirect('configuracao:gerenciar_assinatura')
        
        # Validar cupom se fornecido
        if stripe_coupon:
            from configuracao.services_assinatura import validar_codigo_promocional
            is_valido, erro = validar_codigo_promocional(stripe_coupon)
            if not is_valido:
                messages.error(request, f"❌ Cupom inválido: {erro}")
                return redirect('configuracao:gerenciar_assinatura')

        def _resolver_desconto_checkout(codigo_desconto):
            """Resolve o desconto para o formato aceito pelo Checkout do Stripe.

            Ordem de tentativa:
            1) ID de promotion code (promo_...)
            2) Código promocional legível (ex.: USUARIO10) -> busca PromotionCode por código
            3) ID de cupom Stripe (Coupon ID)
            4) Nome do cupom no Stripe (fallback para casos antigos)
            """
            if not codigo_desconto:
                return None

            codigo_limpo = codigo_desconto.strip()
            if not codigo_limpo:
                return None

            if codigo_limpo.startswith('promo_'):
                return {'promotion_code': codigo_limpo}

            # Tenta como ID de promotion code (quando não veio com prefixo esperado)
            try:
                promo = stripe.PromotionCode.retrieve(codigo_limpo)
                if promo and getattr(promo, 'active', False):
                    return {'promotion_code': promo.id}
            except Exception:
                pass

            try:
                promotion_codes = stripe.PromotionCode.list(code=codigo_limpo, active=True, limit=1)
                if getattr(promotion_codes, 'data', None):
                    return {'promotion_code': promotion_codes.data[0].id}
            except Exception as exc:
                logger.warning(f"Falha ao consultar PromotionCode no Stripe para '{codigo_limpo}': {exc}")

            # Tenta como Coupon ID
            try:
                coupon = stripe.Coupon.retrieve(codigo_limpo)
                if coupon and getattr(coupon, 'valid', False):
                    return {'coupon': coupon.id}
            except Exception:
                pass

            # Fallback: alguns ambientes antigos salvam/expõem o NOME do cupom,
            # mas o Checkout precisa do ID interno do Stripe.
            try:
                coupons = stripe.Coupon.list(limit=100)
                for coupon in coupons.auto_paging_iter():
                    if (getattr(coupon, 'name', '') or '').strip().lower() == codigo_limpo.lower():
                        if getattr(coupon, 'valid', False):
                            return {'coupon': coupon.id}
                        return None
            except Exception as exc:
                logger.warning(f"Falha ao buscar cupom por nome no Stripe para '{codigo_limpo}': {exc}")

            return None
        try:
            plano_escolhido = Plano.objects.get(id=plano_id_selecionado, ativo=True)

            # Ignora a verificação de release/allowlist quando a assinatura está irregular,
            # pois o fallback já exibiu todos os planos visíveis para regularização.
            assinatura_irregular = not assinatura_atual or assinatura_atual.status not in ('ativa', 'gratuita')
            if not assinatura_irregular and not ministerio_pode_contratar_plano(ministerio, plano_escolhido):
                messages.error(request, "Este plano ainda não está liberado para contratação no seu ministério.")
                return redirect('configuracao:gerenciar_assinatura')

            # Se o plano é gratuito, verifica limite de membros antes de ativar
            if plano_escolhido.preco_mensal == 0:
                total_membros = ministerio.membros.count()
                if plano_escolhido.limite_membros and total_membros > plano_escolhido.limite_membros:
                    messages.error(request, f"Este plano permite até {plano_escolhido.limite_membros} pessoas. Seu ministério possui {total_membros} pessoas. Faça um upgrade para um plano maior.")
                    return redirect('configuracao:gerenciar_assinatura')
                assinatura, criada = AssinaturaMinisterio.objects.get_or_create(
                    ministerio=ministerio,
                    defaults={
                        'plano': plano_escolhido,
                        'data_inicio': timezone.now(),
                        'status': 'gratuita',
                        'ciclo_pagamento': ciclo_pagamento_selecionado,
                        'data_fim': None,
                    }
                )
                if not criada:
                    assinatura.plano = plano_escolhido
                    assinatura.data_inicio = timezone.now()
                    assinatura.status = 'gratuita'
                    assinatura.ciclo_pagamento = ciclo_pagamento_selecionado
                    assinatura.data_fim = None
                    assinatura.save()
                messages.success(request, "Plano gratuito ativado com sucesso!")
                return redirect('configuracao:gerenciar_assinatura')

            # Processamento normal de escolha de plano pago
            if ciclo_pagamento_selecionado == 'anual':
                stripe_price_id = plano_escolhido.stripe_price_id_anual
            else: # 'mensal'
                stripe_price_id = plano_escolhido.stripe_price_id_mensal

            if not stripe_price_id:
                messages.error(request, "Este plano não está configurado para pagamento online. Contate o suporte.")
                return redirect('configuracao:gerenciar_assinatura')

            checkout_params = {
                'line_items': [
                    {
                        'price': stripe_price_id,
                        'quantity': 1,
                    },
                ],
                'mode': 'subscription',
                # Deixa o Stripe exibir automaticamente os métodos habilitados no
                # Dashboard para a região do cliente (cartão, PIX, boleto etc.).
                # Nota: PIX e boleto não suportam débito automático recorrente —
                # renovações subsequentes serão cobradas apenas via cartão salvo.
                'payment_method_types': ['card'],
                'success_url': request.build_absolute_uri(reverse('configuracao:gerenciar_assinatura')) + '?status=success&session_id={CHECKOUT_SESSION_ID}',
                'cancel_url': request.build_absolute_uri(reverse('configuracao:gerenciar_assinatura')) + '?status=cancelled',
                'metadata': {
                    'ministerio_id': ministerio.id,
                    'user_id': request.user.id,
                    'plano_id': plano_escolhido.id,
                    'ciclo_pagamento': ciclo_pagamento_selecionado,
                    'stripe_coupon': '',
                    'stripe_coupon_input': stripe_coupon or '',
                }
            }
            if stripe_coupon:
                desconto = _resolver_desconto_checkout(stripe_coupon)
                if desconto:
                    checkout_params['discounts'] = [desconto]
                    checkout_params['metadata']['stripe_coupon'] = desconto.get('promotion_code') or desconto.get('coupon') or stripe_coupon
                else:
                    messages.error(request, "❌ Cupom inválido no Stripe. Use um código promocional válido ou o ID do cupom.")
                    return redirect('configuracao:gerenciar_assinatura')

            checkout_session = stripe.checkout.Session.create(**checkout_params)

            # --- FUNIL: checkout iniciado ---
            from configuracao.services_assinatura import registrar_evento_funil
            registrar_evento_funil(
                'checkout_iniciado',
                ministerio=ministerio,
                plano=plano_escolhido,
                ciclo_pagamento=ciclo_pagamento_selecionado,
                valor=plano_escolhido.preco_anual if ciclo_pagamento_selecionado == 'anual' else plano_escolhido.preco_mensal,
            )

            return redirect(checkout_session.url, code=303)
        except Plano.DoesNotExist:
            messages.error(request, "O plano selecionado não é válido ou não está mais disponível.")
            return redirect('configuracao:gerenciar_assinatura')
        except stripe.error.InvalidRequestError as e:
            logger.error(f"Erro de validação Stripe ao processar escolha de plano para ministério {ministerio.id}: {e}")
            if stripe_coupon:
                messages.error(request, "❌ Cupom inválido no Stripe. Revise o código promocional e tente novamente.")
            else:
                messages.error(request, "Não foi possível iniciar o checkout com o Stripe. Tente novamente.")
            return redirect('configuracao:gerenciar_assinatura')
        except Exception as e:
            logger.error(f"Erro ao processar escolha de plano para ministério {ministerio.id}: {e}")
            messages.error(request, "Ocorreu um erro ao processar sua solicitação. Tente novamente.")
            return redirect('configuracao:gerenciar_assinatura')
    
    # Lógica para mostrar opção de cortesia no GET
    if assinatura_atual and assinatura_atual.status == 'vencida' and not assinatura_atual.is_periodo_cortesia_valido():
        mostrar_opcao_cortesia = True

    if assinatura_atual and is_trial_ativo(assinatura_atual):
        trial_dias_restantes = dias_restantes_trial(assinatura_atual)
    else:
        trial_dias_restantes = None

    trial_ja_utilizado = bool(assinatura_atual and assinatura_atual.data_inicio_trial)
    if not trial_ja_utilizado:
        if not assinatura_atual or assinatura_atual.status in ('vencida', 'cancelada', 'pendente_pagamento'):
            mostrar_opcao_trial = True

    aviso_vencimento_proximo = False
    dias_para_vencer = None
    if assinatura_atual and assinatura_atual.data_fim and assinatura_atual.status == 'ativa':
        dias_para_vencer_calc = (assinatura_atual.data_fim - timezone.now()).days
        if 0 <= dias_para_vencer_calc <= 7:
            aviso_vencimento_proximo = True
            dias_para_vencer = dias_para_vencer_calc

    tempo_cortesia_restante = None
    if assinatura_atual and assinatura_atual.is_periodo_cortesia_valido():
        data_fim_cortesia = assinatura_atual.data_inicio_cortesia + timedelta(days=3)
        tempo_restante = data_fim_cortesia - timezone.now()
        if tempo_restante.total_seconds() > 0:
            tempo_cortesia_restante = {
                'dias': tempo_restante.days,
                'horas': tempo_restante.seconds // 3600,
                'minutos': (tempo_restante.seconds % 3600) // 60,
            }

    # Dados adicionais (plano efetivo, uso, faturas)
    plano_efetivo = obter_plano_efetivo_ministerio(ministerio)
    plano_assinatura = assinatura_atual.plano if assinatura_atual else None

    liberacao_ativa_plano_efetivo = None
    if plano_efetivo:
        liberacao_ativa_plano_efetivo = (
            ministerio.liberacoes_planos.filter(
                plano=plano_efetivo,
                ativo=True,
                pode_visualizar=True,
            )
            .order_by('-data_atualizacao', '-id')
            .first()
        )
    plano_efetivo_por_liberacao = bool(
        liberacao_ativa_plano_efetivo and (
            not plano_assinatura or plano_assinatura.id != plano_efetivo.id
        )
    )
    liberacao_beta_ativa = ministerio.liberacoes_planos.filter(
        ativo=True, acesso_beta=True, pode_visualizar=True
    ).exists()

    pessoas_ativas = contar_pessoas_ativas(ministerio)
    limite_pessoas = obter_limite_pessoas_ativas(ministerio)
    percentual_pessoas = 0
    if limite_pessoas and limite_pessoas > 0:
        percentual_pessoas = round((pessoas_ativas / limite_pessoas) * 100, 1)

    igrejas_ativas = ministerio.igrejas.count()
    limite_igrejas = plano_efetivo.limite_igrejas if plano_efetivo else 0
    percentual_igrejas = 0
    if limite_igrejas and limite_igrejas > 0:
        percentual_igrejas = round((igrejas_ativas / limite_igrejas) * 100, 1)

    grace_dias_restantes = dias_restantes_graca(assinatura_atual) if assinatura_atual else None

    invoices = []
    if ministerio.stripe_customer_id:
        try:
            invoices = stripe.Invoice.list(customer=ministerio.stripe_customer_id, limit=10)
        except Exception as e:
            logger.warning(f"Erro ao buscar faturas do Stripe para {ministerio.id}: {e}")

    context = {
        'ministerio': ministerio,
        'assinatura_atual': assinatura_atual,
        'planos_disponiveis': planos_disponiveis,
        'historico_assinatura': historico_assinatura,
        'titulo_pagina': "Assinatura",
        'aviso_vencimento_proximo': aviso_vencimento_proximo,
        'dias_para_vencer': dias_para_vencer,
        'mostrar_opcao_cortesia': mostrar_opcao_cortesia,
        'mostrar_opcao_trial': mostrar_opcao_trial,
        'trial_dias_restantes': trial_dias_restantes,
        'tempo_cortesia_restante': tempo_cortesia_restante,
        'plano_efetivo': plano_efetivo,
        'plano_assinatura': plano_assinatura,
        'plano_efetivo_por_liberacao': plano_efetivo_por_liberacao,
        'liberacao_beta_ativa': liberacao_beta_ativa,
        'pessoas_ativas': pessoas_ativas,
        'limite_pessoas': limite_pessoas if limite_pessoas else '∞',
        'percentual_pessoas': percentual_pessoas,
        'igrejas_ativas': igrejas_ativas,
        'limite_igrejas': limite_igrejas if limite_igrejas else '∞',
        'percentual_igrejas': percentual_igrejas,
        'grace_dias_restantes': grace_dias_restantes,
        'invoices': invoices.data if invoices else [],
        'plano_efetivo_ordem': plano_efetivo.ordem_liberacao if plano_efetivo else 0,
        'plano_upgrade_recomendado_id': next(
            (p.id for p in planos_disponiveis
             if plano_efetivo and p.ordem_liberacao > plano_efetivo.ordem_liberacao),
            None
        ),
        'planos_com_tipo': _anotar_tipo_planos(planos_disponiveis, plano_efetivo, pessoas_ativas, igrejas_ativas),
    }
    return render(request, 'configuracao/assinatura/gerenciar_assinatura.html', context)


@login_required
def minha_assinatura(request):
    """Redireciona para a página unificada de assinatura."""
    return redirect('configuracao:gerenciar_assinatura')


def _minha_assinatura_legado(request):
    """Dashboard com detalhes completos da assinatura e histórico de faturas."""
    ministerio = get_ministerio_or_error(request)
    assinatura_atual = AssinaturaMinisterio.objects.filter(ministerio=ministerio).order_by('-data_inicio').first()
    plano_efetivo = obter_plano_efetivo_ministerio(ministerio)
    plano_assinatura = assinatura_atual.plano if assinatura_atual else None

    liberacao_ativa_plano_efetivo = None
    if plano_efetivo:
        liberacao_ativa_plano_efetivo = (
            ministerio.liberacoes_planos.filter(
                plano=plano_efetivo,
                ativo=True,
                pode_visualizar=True,
            )
            .order_by('-data_atualizacao', '-id')
            .first()
        )

    plano_efetivo_por_liberacao = bool(
        liberacao_ativa_plano_efetivo and (
            not plano_assinatura or plano_assinatura.id != plano_efetivo.id
        )
    )

    # Cálculo de limites e uso
    pessoas_ativas = contar_pessoas_ativas(ministerio)
    limite_pessoas = obter_limite_pessoas_ativas(ministerio)
    percentual_pessoas = 0
    if limite_pessoas and limite_pessoas > 0:
        percentual_pessoas = round((pessoas_ativas / limite_pessoas) * 100, 1)

    igrejas_ativas = ministerio.igrejas.count()
    limite_igrejas = plano_efetivo.limite_igrejas if plano_efetivo else 0
    percentual_igrejas = 0
    if limite_igrejas and limite_igrejas > 0:
        percentual_igrejas = round((igrejas_ativas / limite_igrejas) * 100, 1)

    # Dias restantes de grace period
    grace_dias_restantes = None
    trial_dias_restantes = None
    if assinatura_atual:
        from configuracao.services_assinatura import dias_restantes_graca
        grace_dias_restantes = dias_restantes_graca(assinatura_atual)
        trial_dias_restantes = dias_restantes_trial(assinatura_atual)

    # Listar faturas do Stripe (se houver customer_id)
    invoices = []
    if ministerio.stripe_customer_id:
        try:
            invoices = stripe.Invoice.list(customer=ministerio.stripe_customer_id, limit=10)
        except Exception as e:
            logger.warning(f"Erro ao buscar faturas do Stripe para {ministerio.id}: {e}")

    context = {
        'ministerio': ministerio,
        'assinatura_atual': assinatura_atual,
        'plano_efetivo': plano_efetivo,
        'plano_assinatura': plano_assinatura,
        'plano_efetivo_por_liberacao': plano_efetivo_por_liberacao,
        'pessoas_ativas': pessoas_ativas,
        'limite_pessoas': limite_pessoas if limite_pessoas else '∞',
        'percentual_pessoas': percentual_pessoas,
        'igrejas_ativas': igrejas_ativas,
        'limite_igrejas': limite_igrejas if limite_igrejas else '∞',
        'percentual_igrejas': percentual_igrejas,
        'grace_dias_restantes': grace_dias_restantes,
        'trial_dias_restantes': trial_dias_restantes,
        'invoices': invoices.data if invoices else [],
        'titulo_pagina': "Minha Assinatura",
    }

    return render(request, 'configuracao/assinatura/minha_assinatura.html', context)

# Adicionar ao final de c:\Gereigreja\configuracao\views.py

@login_required
@require_POST
def set_active_church(request):
    requested_value = (request.POST.get('igreja_id_selector') or '').strip()
    previous_church_id = getattr(getattr(request, 'igreja_ativa', None), 'pk', None)
    perfil = getattr(request.user, 'perfil', None)
    ministerio_id = getattr(perfil, 'ministerio_id', None)
    redirect_url = request.POST.get('next', '')
    if not url_has_allowed_host_and_scheme(
        redirect_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        redirect_url = reverse('secretaria:dashboard')

    log_context = {
        'event': 'active_church_context_change',
        'user_id': request.user.pk,
        'ministerio_id': ministerio_id,
        'previous_church_id': previous_church_id,
        'requested_church_id': None,
        'new_church_id': previous_church_id,
    }

    if requested_value in ('', 'todas'):
        request.session.pop('igreja_ativa_id', None)
        logger.info(
            "Contexto de igreja removido",
            extra={**log_context, 'new_church_id': None, 'result': 'cleared'},
        )
        messages.info(request, "Contexto de igreja removido.")
        return HttpResponseRedirect(redirect_url)

    try:
        requested_church_id = int(requested_value)
    except (TypeError, ValueError):
        logger.warning("Troca de contexto de igreja negada", extra={**log_context, 'result': 'denied'})
        messages.error(request, "Igreja selecionada inválida ou não permitida.")
        return HttpResponseRedirect(redirect_url)

    allowed_churches = getattr(request, 'igrejas_permitidas', None)
    if allowed_churches is None:
        allowed_churches = get_igrejas_selecionaveis(request.user)
    igreja_selecionada = allowed_churches.filter(pk=requested_church_id).first()
    log_context['requested_church_id'] = requested_church_id

    if igreja_selecionada is None:
        logger.warning("Troca de contexto de igreja negada", extra={**log_context, 'result': 'denied'})
        messages.error(request, "Igreja selecionada inválida ou não permitida.")
        return HttpResponseRedirect(redirect_url)

    request.session['igreja_ativa_id'] = igreja_selecionada.pk
    request.session.modified = True
    logger.info(
        "Contexto de igreja alterado",
        extra={**log_context, 'new_church_id': igreja_selecionada.pk, 'result': 'success'},
    )
    messages.success(request, f"Contexto alterado para a igreja: {igreja_selecionada.nome_igreja}.")
    return HttpResponseRedirect(redirect_url)


@login_required
def lista_atualizacoes_sistema(request):
    """
    Exibe uma lista de todas as atualizações do sistema que foram publicadas.
    """
    # Apenas para garantir que o usuário está em uma ministério válida,
    # embora as atualizações sejam globais para o sistema.
    try:
        get_ministerio_or_error(request) # Valida a ministério do usuário
    except Exception: # Se get_ministerio_or_error levantar PermissionDenied ou Http404
        # Você pode decidir se quer permitir acesso mesmo sem ministério
        # ou redirecionar para o login/página de erro.
        # Por enquanto, vamos permitir, pois as atualizações são do sistema.
        pass


    atualizacoes = AtualizacaoSistema.objects.filter(publicado=True).order_by('-data_publicacao', '-versao')
    
    context = {
        'atualizacoes': atualizacoes,
        'titulo_pagina': "Novidades e Atualizações do Sistema",
    }
    return render(request, 'configuracao/lista_atualizacoes.html', context)

# --- NOVA VIEW PARA MEU PERFIL ---
@login_required
def meu_perfil(request):
    """
    Exibe e permite a edição do perfil do usuário logado.
    """
    logger.info(f"Usuário acessando meu_perfil: {request.user.username} (ID: {request.user.id})")

    # Tenta obter o PerfilUsuario associado ao usuário logado
    try:
        perfil_usuario = request.user.perfil
        logger.info(f"Perfil encontrado para o usuário: {perfil_usuario.id}")
        ministerio = perfil_usuario.ministerio
        logger.info(f"Ministério associada ao perfil: {ministerio.nome_fantasia} (ID: {ministerio.id})")

    except PerfilUsuario.DoesNotExist:
        # Caso o perfil não exista por algum motivo (improvável se o sistema estiver consistente)
        # Você pode criar um perfil aqui ou redirecionar/mostrar um erro.
        # Por simplicidade, vamos assumir que o perfil deve existir.
        messages.error(request, "Perfil de usuário não encontrado. Contate o suporte.")
        logger.error(f"Perfil não encontrado para o usuário: {request.user.username} (ID: {request.user.id})")

        return redirect('secretaria:index') # Ou outra página apropriada

    logger.debug(f"Usuário: {request.user}")
    logger.debug(f"PerfilUsuario: {perfil_usuario}")
    logger.debug(f"Ministério: {perfil_usuario.ministerio if perfil_usuario else None}")
    context = _montar_contexto_hub_perfil(
        request=request,
        usuario_alvo=request.user,
        perfil_usuario_obj=perfil_usuario,
        titulo_pagina="Meu Perfil",
    )
    return render(request, 'configuracao/perfil/meu_perfil.html', context)
# --- FIM NOVA VIEW ---

# --- NOVA VIEW PARA EDITAR MEU PERFIL ---
@login_required
def editar_meu_perfil(request):
    """
    Permite ao usuário logado editar seus dados básicos e do perfil.
    """
    user = request.user
    try:
        logger.info(f"Usuário acessando editar_meu_perfil: {request.user.username} (ID: {request.user.id})")

        perfil_usuario = user.perfil
    except PerfilUsuario.DoesNotExist:
        messages.error(request, "Perfil de usuário não encontrado. Contate o suporte.")
        return redirect('configuracao:meu_perfil') # Redireciona de volta para a página de visualização

    if request.method == 'POST':
       # request.FILES é necessário para o upload da foto_perfil
        user_form = UserEditForm(request.POST, instance=user)
        perfil_form = PerfilUsuarioEditForm(request.POST, request.FILES, instance=perfil_usuario)
       
        logger.debug(f"Usuário: {request.user}")
        logger.debug(f"PerfilUsuario: {perfil_usuario}")
        logger.debug(f"Ministério: {perfil_usuario.ministerio if perfil_usuario else None}")

        logger.debug(f"Usuário: {request.user}, PerfilUsuario: {perfil_usuario}")
        if perfil_usuario:
            logger.debug(f"Ministério: {perfil_usuario.ministerio}")
        else:
            logger.warning("PerfilUsuario não encontrado.")
        if user_form.is_valid() and perfil_form.is_valid():
            try:
                # with transaction.atomic(): # Garante que ambas as alterações sejam salvas ou nenhuma
                logger.info("Salvando user_form...")

                user_form.save()
                logger.info("user_form salvo com sucesso.")

                logger.info("Salvando perfil_form...")
                perfil_form.save()
                logger.info("perfil_form salvo com sucesso.")

                logger.info("Valor de perfil_usuario.foto_perfil atualizado.")

                messages.success(request, 'Seu perfil foi atualizado com sucesso!')
                return redirect('configuracao:meu_perfil') # Redireciona para a página de visualização do perfil
            except ValidationError as e:
                logger.error(f"Erro de validação ao salvar edição do perfil para usuário {user.username}: {e}")
                messages.error(request, "Ocorreu um erro de validação ao salvar seu perfil. Tente novamente.")

            # except Exception as e:
            #    logger.error(f"Erro ao salvar edição do perfil para usuário {user.username}: {e}")
            #    messages.error(request, "Ocorreu um erro ao salvar seu perfil. Tente novamente.")
            except Exception as e:
                logger.error(f"Erro ao salvar edição do perfil para usuário {user.username}: {e}")
                messages.error(request, "Ocorreu um erro ao salvar seu perfil. Tente novamente.")
        else:
            # Se um ou ambos os formulários forem inválidos
            if not user_form.is_valid():
                messages.error(request, 'Por favor, corrija os erros no formulário de dados da conta.')
            if not perfil_form.is_valid():
                messages.error(request, 'Por favor, corrija os erros no formulário de dados do perfil.')

    else: # GET request
        user_form = UserEditForm(instance=user)
        perfil_form = PerfilUsuarioEditForm(instance=perfil_usuario)

    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'titulo_pagina': "Editar Meu Perfil",
        'usuario': user,
        'perfil_usuario': perfil_usuario,

        'ministerio': perfil_usuario.ministerio # Adiciona a ministério ao contexto
    }
    return render(request, 'configuracao/perfil/editar_meu_perfil.html', context) # Crie este template
# --- FIM NOVA VIEW ---

@login_required
@admin_ministerio_required
def abrir_billing_portal(request):
    """
    Cria uma sessão no Stripe Customer Portal e redireciona o cliente.
    Permite ao administrador do ministério gerenciar cartão, faturas e cancelamento
    diretamente na interface segura do Stripe.
    """
    ministerio = get_ministerio_or_error(request)

    if not ministerio.stripe_customer_id:
        messages.warning(
            request,
            "Seu ministério ainda não possui uma assinatura paga vinculada ao Stripe. "
            "Assine um plano pago para acessar o portal de cobrança."
        )
        return redirect('configuracao:gerenciar_assinatura')

    try:
        return_url = request.build_absolute_uri(reverse('configuracao:gerenciar_assinatura'))
        portal_session = stripe.billing_portal.Session.create(
            customer=ministerio.stripe_customer_id,
            return_url=return_url,
        )
        return redirect(portal_session.url, code=303)
    except stripe.error.InvalidRequestError as e:
        logger.error(f"Stripe billing portal error para ministério {ministerio.id}: {e}")
        messages.error(
            request,
            "Não foi possível abrir o portal de cobrança. "
            "Verifique se o Customer Portal está ativado no seu painel Stripe."
        )
        return redirect('configuracao:gerenciar_assinatura')
    except Exception as e:
        logger.error(f"Erro inesperado ao abrir billing portal para ministério {ministerio.id}: {e}")
        messages.error(request, "Ocorreu um erro ao abrir o portal de cobrança. Tente novamente.")
        return redirect('configuracao:gerenciar_assinatura')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    if not sig_header:
        logger.warning('Webhook Stripe recebido sem header de assinatura.')
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Payload inválido
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Assinatura inválida
        return HttpResponse(status=400)

    # Lidar com o evento checkout.session.completed
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Obter os metadados que enviamos
        metadata = session.get('metadata', {})
        ministerio_id = metadata.get('ministerio_id')
        plano_id = metadata.get('plano_id')
        ciclo_pagamento = metadata.get('ciclo_pagamento')
        stripe_coupon = metadata.get('stripe_coupon', '').strip()
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get('subscription')

        if not all([ministerio_id, plano_id, ciclo_pagamento]):
            logger.error(f"Webhook do Stripe com metadados faltando: {session.id}")
            return HttpResponse(status=400)

        try:
            with transaction.atomic():
                ministerio = Ministerio.objects.get(id=ministerio_id)
                plano_escolhido = Plano.objects.get(id=plano_id)

                # Atualiza a ministério com os IDs do Stripe para gerenciamento futuro
                ministerio.stripe_customer_id = stripe_customer_id
                ministerio.save()

                # Calcula a data de fim da assinatura
                data_inicio = timezone.now()
                if ciclo_pagamento == 'anual':
                    data_fim = data_inicio + timedelta(days=365)
                else:
                    data_fim = data_inicio + timedelta(days=30)

                # Atualiza ou cria a assinatura
                assinatura, created = AssinaturaMinisterio.objects.update_or_create(
                    ministerio=ministerio,
                    defaults={
                        'plano': plano_escolhido,
                        'data_inicio': data_inicio,
                        'data_fim': data_fim,
                        'ciclo_pagamento': ciclo_pagamento,
                        'status': 'ativa',
                        'periodo_cortesia_ativo': False,
                        'trial_ativo': False,
                        'id_transacao_gateway': stripe_subscription_id,
                    }
                )
                logger.info(f"Assinatura para a ministério '{ministerio.nome_fantasia}' foi ativada/atualizada via webhook do Stripe.")

                # --- REGISTRAR USO DO CUPOM (se usado) ---
                if stripe_coupon:
                    try:
                        from configuracao.models import CodigoPromocional
                        cupom = CodigoPromocional.objects.get(codigo_stripe=stripe_coupon)
                        cupom.registrar_uso()
                        logger.info(f"Cupom {stripe_coupon} registrado como usado por {ministerio.nome_fantasia}")
                    except CodigoPromocional.DoesNotExist:
                        logger.warning(f"Cupom {stripe_coupon} não encontrado no banco (stripe webhook). Tentando sincronizar do Stripe.")
                        try:
                            from configuracao.services_assinatura import validar_codigo_promocional
                            ok, _ = validar_codigo_promocional(stripe_coupon)
                            if ok:
                                cupom_sync = CodigoPromocional.objects.get(codigo_stripe=stripe_coupon)
                                cupom_sync.registrar_uso()
                                logger.info(f"Cupom {stripe_coupon} sincronizado e registrado como usado por {ministerio.nome_fantasia}")
                        except Exception as exc_sync:
                            logger.warning(f"Não foi possível sincronizar cupom {stripe_coupon} no webhook: {exc_sync}")

                # --- FUNIL: checkout completo ---
                from configuracao.services_assinatura import registrar_evento_funil
                registrar_evento_funil(
                    'checkout_completo',
                    ministerio=ministerio,
                    plano=plano_escolhido,
                    ciclo_pagamento=ciclo_pagamento,
                    valor=assinatura.plano.preco_anual if ciclo_pagamento == 'anual' else assinatura.plano.preco_mensal,
                )

        except (Ministerio.DoesNotExist, Plano.DoesNotExist) as e:
            logger.error(f"Erro no webhook do Stripe: Ministério ou Plano não encontrado. Detalhes: {e}")
            return HttpResponse(status=404)
        except Exception as e:
            logger.error(f"Erro crítico ao processar webhook do Stripe: {e}")
            return HttpResponse(status=500)

    elif event['type'] == 'invoice.payment_failed':
        # Pagamento da fatura falhou — inicia grace period e notifica
        invoice = event['data']['object']
        stripe_customer_id = invoice.get('customer')
        stripe_subscription_id = invoice.get('subscription')
        if stripe_customer_id:
            try:
                with transaction.atomic():
                    ministerio = Ministerio.objects.get(stripe_customer_id=stripe_customer_id)
                    assinatura = AssinaturaMinisterio.objects.filter(ministerio=ministerio).first()
                    if assinatura:
                        # Incrementar contador de falhas e registrar timestamp
                        assinatura.tentativas_falha_pagamento += 1
                        assinatura.data_ultima_falha_pagamento = timezone.now()
                        
                        # Grace period: 7 dias para resolver o pagamento
                        MAX_TENTATIVAS = 3
                        if assinatura.tentativas_falha_pagamento == 1:
                            # Primeira falha: inicia grace period
                            assinatura.data_fim_graca_inadimplencia = timezone.now() + timedelta(days=7)
                            assinatura.status = 'pendente_pagamento'
                            assinatura.save(update_fields=['status', 'tentativas_falha_pagamento', 'data_ultima_falha_pagamento', 'data_fim_graca_inadimplencia'])
                            
                            # Notificar ministério
                            from notificacoes.models import Notificacao
                            Notificacao.objects.create(
                                usuario=ministerio.usuario_admin,
                                titulo='⚠️ Falha de Pagamento — 7 Dias de Carência',
                                mensagem=f'Seu pagamento não foi processado. Você tem 7 dias para regularizar antes de perder acesso.',
                                tipo='alerta',
                                url=reverse('configuracao:gerenciar_assinatura'),
                            )
                            logger.warning(
                                f"Primeira falha de pagamento para {ministerio.nome_fantasia}. "
                                f"Grace period iniciado (7 dias). subscription={stripe_subscription_id}"
                            )
                        elif assinatura.tentativas_falha_pagamento < MAX_TENTATIVAS:
                            # Falha seguinte durante grace period
                            assinatura.save(update_fields=['tentativas_falha_pagamento', 'data_ultima_falha_pagamento'])
                            logger.warning(
                                f"Falha de pagamento #{assinatura.tentativas_falha_pagamento} para {ministerio.nome_fantasia}. "
                                f"subscription={stripe_subscription_id}"
                            )
                        else:
                            # Excedeu tentativas: bloqueia acesso
                            assinatura.status = 'cancelada'
                            assinatura.save(update_fields=['status', 'tentativas_falha_pagamento', 'data_ultima_falha_pagamento'])
                            
                            from notificacoes.models import Notificacao
                            Notificacao.objects.create(
                                usuario=ministerio.usuario_admin,
                                titulo='❌ Acesso Cancelado — Inadimplência',
                                mensagem=f'Seu acesso foi suspenso após múltiplas falhas de pagamento. Contate o suporte para regularizar.',
                                tipo='erro',
                                url=reverse('configuracao:gerenciar_assinatura'),
                            )
                            logger.error(
                                f"Assinatura cancelada por inadimplência: {ministerio.nome_fantasia} "
                                f"(tentativas: {assinatura.tentativas_falha_pagamento}). subscription={stripe_subscription_id}"
                            )
            except Ministerio.DoesNotExist:
                logger.warning(f"invoice.payment_failed: customer {stripe_customer_id} não encontrado no banco.")
            except Exception as e:
                logger.error(f"Erro ao processar invoice.payment_failed: {e}")
                return HttpResponse(status=500)

    elif event['type'] == 'invoice.paid':
        invoice = event['data']['object']
        stripe_customer_id = invoice.get('customer')
        stripe_subscription_id = invoice.get('subscription')
        if stripe_customer_id:
            try:
                with transaction.atomic():
                    ministerio = Ministerio.objects.get(stripe_customer_id=stripe_customer_id)
                    assinatura = AssinaturaMinisterio.objects.filter(ministerio=ministerio).first()
                    if assinatura:
                        # Pagamento confirmado, limpa estado de inadimplencia.
                        assinatura.status = 'ativa'
                        assinatura.tentativas_falha_pagamento = 0
                        assinatura.data_ultima_falha_pagamento = None
                        assinatura.data_fim_graca_inadimplencia = None
                        assinatura.periodo_cortesia_ativo = False

                        lines = (invoice.get('lines') or {}).get('data') or []
                        if lines:
                            period = (lines[0] or {}).get('period') or {}
                            period_start = period.get('start')
                            period_end = period.get('end')
                            if period_start:
                                from datetime import datetime

                                dt_start = datetime.fromtimestamp(period_start)
                                assinatura.data_inicio = timezone.make_aware(dt_start, timezone.get_current_timezone()) if timezone.is_naive(dt_start) else dt_start
                            if period_end:
                                from datetime import datetime

                                dt_end = datetime.fromtimestamp(period_end)
                                assinatura.data_fim = timezone.make_aware(dt_end, timezone.get_current_timezone()) if timezone.is_naive(dt_end) else dt_end

                        assinatura.save(update_fields=[
                            'status',
                            'tentativas_falha_pagamento',
                            'data_ultima_falha_pagamento',
                            'data_fim_graca_inadimplencia',
                            'periodo_cortesia_ativo',
                            'data_inicio',
                            'data_fim',
                        ])

                        amount_paid = invoice.get('amount_paid')
                        valor_pago = Decimal('0.00')
                        if amount_paid is not None:
                            valor_pago = (Decimal(str(amount_paid)) / Decimal('100')).quantize(Decimal('0.01'))

                        from datetime import datetime

                        created_ts = invoice.get('created')
                        data_inicio_hist = timezone.now()
                        if created_ts:
                            dt_created = datetime.fromtimestamp(created_ts)
                            data_inicio_hist = timezone.make_aware(dt_created, timezone.get_current_timezone()) if timezone.is_naive(dt_created) else dt_created

                        data_fim_hist = assinatura.data_fim
                        observacao = f"Pagamento Stripe confirmado. invoice_id={invoice.get('id')}; subscription_id={stripe_subscription_id or 'n/a'}"
                        _registrar_historico_mensalidade(
                            ministerio=ministerio,
                            plano=assinatura.plano,
                            valor=valor_pago,
                            data_inicio=data_inicio_hist,
                            data_fim=data_fim_hist,
                            observacao=observacao,
                        )

                        from configuracao.services_assinatura import registrar_evento_funil
                        registrar_evento_funil(
                            'pagamento_confirmado',
                            ministerio=ministerio,
                            plano=assinatura.plano,
                            ciclo_pagamento=assinatura.ciclo_pagamento,
                            valor=valor_pago,
                            extra={
                                'invoice_id': invoice.get('id') or '',
                                'subscription_id': stripe_subscription_id or '',
                                'billing_reason': invoice.get('billing_reason') or '',
                            },
                        )
            except Ministerio.DoesNotExist:
                logger.warning(f"invoice.paid: customer {stripe_customer_id} não encontrado no banco.")
            except Exception as e:
                logger.error(f"Erro ao processar invoice.paid: {e}")
                return HttpResponse(status=500)

    elif event['type'] == 'customer.subscription.deleted':
        # Assinatura cancelada definitivamente no Stripe
        subscription = event['data']['object']
        stripe_customer_id = subscription.get('customer')
        if stripe_customer_id:
            try:
                with transaction.atomic():
                    ministerio = Ministerio.objects.get(stripe_customer_id=stripe_customer_id)
                    assinatura = AssinaturaMinisterio.objects.filter(ministerio=ministerio).first()
                    if assinatura:
                        status_anterior = assinatura.status
                        plano_anterior = assinatura.plano
                        ciclo_anterior = assinatura.ciclo_pagamento
                        
                        # Downgrade automático para o plano Pioneiro (gratuito)
                        try:
                            plano_pioneiro = Plano.objects.get(codigo_plano='pioneiro')
                            assinatura.plano = plano_pioneiro
                            assinatura.status = 'gratuita'
                            assinatura.data_fim = None
                            assinatura.save(update_fields=['plano', 'status', 'data_fim'])
                            logger.info(
                                f"Ministério '{ministerio.nome_fantasia}' downgradeado automaticamente para plano Pioneiro após cancelamento de assinatura."
                            )
                        except Plano.DoesNotExist:
                            # Se Pioneiro não existe, apenas marca como cancelada
                            assinatura.status = 'cancelada'
                            assinatura.save(update_fields=['status'])
                            logger.error(f"Plano Pioneiro não encontrado. Assinatura marcada como cancelada sem downgrade.")
                            return HttpResponse(status=500)
                        from configuracao.services_assinatura import registrar_evento_funil
                        registrar_evento_funil(
                            'plano_cancelado',
                            ministerio=ministerio,
                            plano=plano_anterior,
                            ciclo_pagamento=ciclo_anterior,
                        )
            except Ministerio.DoesNotExist:
                logger.warning(f"customer.subscription.deleted: customer {stripe_customer_id} não encontrado no banco.")
            except Exception as e:
                logger.error(f"Erro ao processar customer.subscription.deleted: {e}")
                return HttpResponse(status=500)

    elif event['type'] == 'customer.subscription.updated':
        # Stripe renovou ou atualizou o status da assinatura
        subscription = event['data']['object']
        stripe_customer_id = subscription.get('customer')
        stripe_status = subscription.get('status')  # active, past_due, canceled, etc.
        # Mapeia status do Stripe para status interno
        STATUS_MAP = {
            'active': 'ativa',
            'past_due': 'vencida',
            'canceled': 'cancelada',
            'unpaid': 'vencida',
            'trialing': 'ativa',
        }
        status_interno = STATUS_MAP.get(stripe_status)
        if stripe_customer_id and status_interno:
            try:
                with transaction.atomic():
                    ministerio = Ministerio.objects.get(stripe_customer_id=stripe_customer_id)
                    assinatura = AssinaturaMinisterio.objects.filter(ministerio=ministerio).first()
                    if assinatura:
                        status_anterior = assinatura.status
                        plano_anterior = assinatura.plano
                        ciclo_anterior = assinatura.ciclo_pagamento

                        # Tenta resolver plano/ciclo pelo price id atual da assinatura no Stripe
                        novo_plano = None
                        novo_ciclo = None
                        itens = (subscription.get('items') or {}).get('data') or []
                        if itens:
                            price_obj = (itens[0] or {}).get('price') or {}
                            stripe_price_id = price_obj.get('id')
                            if stripe_price_id:
                                novo_plano = Plano.objects.filter(stripe_price_id_mensal=stripe_price_id).first()
                                if novo_plano:
                                    novo_ciclo = 'mensal'
                                else:
                                    novo_plano = Plano.objects.filter(stripe_price_id_anual=stripe_price_id).first()
                                    if novo_plano:
                                        novo_ciclo = 'anual'

                        if novo_plano:
                            assinatura.plano = novo_plano
                        if novo_ciclo:
                            assinatura.ciclo_pagamento = novo_ciclo

                        # Atualiza data_fim com base no período atual da assinatura
                        current_period_end = subscription.get('current_period_end')
                        if current_period_end:
                            from datetime import datetime
                            assinatura.data_fim = timezone.make_aware(
                                datetime.fromtimestamp(current_period_end),
                                timezone.get_current_timezone(),
                            ) if timezone.is_naive(datetime.fromtimestamp(current_period_end)) else timezone.datetime.fromtimestamp(current_period_end, tz=timezone.utc)
                        assinatura.status = status_interno
                        assinatura.save(update_fields=['status', 'data_fim', 'plano', 'ciclo_pagamento'])

                        from configuracao.services_assinatura import registrar_evento_funil
                        if novo_plano and plano_anterior and novo_plano.id != plano_anterior.id:
                            registrar_evento_funil(
                                'upgrade',
                                ministerio=ministerio,
                                plano=novo_plano,
                                ciclo_pagamento=novo_ciclo or ciclo_anterior,
                                valor=novo_plano.preco_anual if (novo_ciclo or ciclo_anterior) == 'anual' else novo_plano.preco_mensal,
                                extra={
                                    'plano_anterior': plano_anterior.codigo_plano,
                                    'plano_novo': novo_plano.codigo_plano,
                                },
                            )

                        if status_interno == 'cancelada' and status_anterior != 'cancelada':
                            registrar_evento_funil(
                                'plano_cancelado',
                                ministerio=ministerio,
                                plano=assinatura.plano,
                                ciclo_pagamento=assinatura.ciclo_pagamento,
                            )

                        logger.info(
                            f"Assinatura do ministério '{ministerio.nome_fantasia}' atualizada: "
                            f"status={status_interno} via customer.subscription.updated."
                        )
            except Ministerio.DoesNotExist:
                logger.warning(f"customer.subscription.updated: customer {stripe_customer_id} não encontrado no banco.")
            except Exception as e:
                logger.error(f"Erro ao processar customer.subscription.updated: {e}")
                return HttpResponse(status=500)

    return HttpResponse(status=200)



@staff_member_required
def validar_imagens_perfil(request):
    try:
        resultados = []
        for perfil in PerfilUsuario.objects.filter(foto_perfil__isnull=False):
            status = '✅ OK'
            resultados.append({
                'usuario': perfil.user.get_full_name() or perfil.user.username,
                'ministerio': perfil.ministerio.nome_fantasia if perfil.ministerio else '',
                'imagem': perfil.foto_perfil,
                'status': status
            })
            
        context = {
            'title': 'Validação de Imagens de Perfil',
            'resultados': resultados,
        }
        
        if request.path.startswith('/admin/'):
            template_name = 'admin/configuracao/validar_imagens.html'
        else:
            template_name = 'configuracao/validacao_imagens_sistema.html'
            
        return render(request, template_name, context)
        
    except Exception as e:
        messages.error(request, str(e))
        if request.path.startswith('/admin/'):
            return redirect('admin:index')
        return redirect('dashboard')
