from django.shortcuts import render

def configuracoes_sistema(request):
    # Buscar o ministério do usuário logado
    perfil = getattr(request.user, 'perfil', None)
    ministerio = getattr(perfil, 'ministerio', None)

    categorias = []
    fornecedores = []
    contas_bancarias = []
    can_edit_finance = False
    if ministerio:
        from financeiro.models import CategoriaDespesa, Fornecedor, ContaBancaria
        from financeiro.utils import has_finance_edit_permission
        categorias = CategoriaDespesa.objects.filter(ministerio=ministerio)
        fornecedores = Fornecedor.objects.filter(ministerio=ministerio)
        igrejas = Igreja.objects.filter(ministerio=ministerio)
        contas_bancarias = ContaBancaria.objects.filter(igreja__in=igrejas)
        can_edit_finance = has_finance_edit_permission(request.user)

    context = {
        'categorias': categorias,
        'fornecedores': fornecedores,
        'contas_bancarias': contas_bancarias,
        'ministerio': ministerio,
        'can_edit_finance': can_edit_finance,
    }
    return render(request, 'configuracao/configuracoes_sistema.html', context)
# configuracao/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Importar User e login
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponseRedirect # Adicionado HttpResponseRedirect
from django.db.models import Q # Para buscas
import logging
from .models import Igreja, Ministerio, PerfilUsuario, Plano, AssinaturaMinisterio # Adicionado Plano e AssinaturaMinisterio
from django.conf import settings # Para pegar as chaves do Stripe
import stripe # Importar a biblioteca do Stripe
import django.db.utils # Import django utils
from .forms import IgrejaForm, MinisterioEditForm, IgrejaEditForm # Adicionado IgrejaEditForm
from .utils import pode_editar_configuracao_org # Importa a função
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
# Ajuste o import de get_allowed_churches_for_user se você a moveu para core.utils
from financeiro.utils import get_allowed_churches_for_user # Importar para set_active_church

from core.utils import get_ministerio_or_error # Importar de core.utils
from .models import AtualizacaoSistema


from django.utils import timezone # Movido para o topo do arquivo ou garantir que está importado
from datetime import timedelta # Movido para o topo do arquivo ou garantir que está importado

from core.decorators import verificar_assinatura_valida # Ou o caminho correto
from .forms import UserEditForm, PerfilUsuarioEditForm
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pdb # Importar o módulo pdb
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
    return user.groups.filter(name='Admin Ministerio').exists() # ou outra lógica


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
    if not request.user.groups.filter(name='Admin Ministerio').exists():
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

        context = {
            'igrejas': igrejas_qs,
            'ministerio': ministerio,
            'current_q': query,
        }
        return render(request, 'configuracao/igrejas/lista_igrejas.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar igrejas para ministério {ministerio.id}")
        messages.error(request, f"Ocorreu um erro ao listar as igrejas: {e}")
        return redirect('secretaria:dashboard')


@login_required
def adicionar_igreja(request):
    """ Cria uma nova igreja para a ministério do usuário. """
    ministerio = get_ministerio_or_error(request)
    # --- NOVA VERIFICAÇÃO DE GRUPO ---
    if not request.user.groups.filter(name='Admin Ministerio').exists():
        messages.error(request, "Você não tem permissão para gerenciar igrejas.")
        return redirect('secretaria:index') # Ou 'dashboard'
        # --- FIM DA VERIFICAÇÃO ---

    if request.method == 'POST':
        form = IgrejaForm(request.POST)
        if form.is_valid():
            igreja = form.save(commit=False)
            igreja.ministerio = ministerio # Associa ao ministério do usuário
            igreja.save()
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
def excluir_igreja(request, pk):
    """ Exclui uma igreja (requer POST e confirmação). """
    ministerio = get_ministerio_or_error(request)
    # --- NOVA VERIFICAÇÃO DE GRUPO ---
    if not request.user.groups.filter(name='Admin Ministerio').exists():
        messages.error(request, "Você não tem permissão para gerenciar igrejas.")
        return redirect('secretaria:index') # Ou 'dashboard'
        # --- FIM DA VERIFICAÇÃO ---
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
        context = {
            'ministerio': ministerio,
            # Passar outros dados relacionados se necessário
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
def editar_ministerio(request):
    """ Permite ao Admin do Minist. editar os dados da sua própria ministério. """
    ministerio = get_ministerio_or_error(request) # Pega a ministério do usuário
# --- NOVA VERIFICAÇÃO DE GRUPO ---
    if not request.user.groups.filter(name='Admin Ministerio').exists():
        messages.error(request, "Você não tem permissão para gerenciar igrejas.")
        return redirect('secretaria:index') # Ou 'dashboard'
        # --- FIM DA VERIFICAÇÃO ---
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

#     ministerio = get_ministerio_or_error(request)
#     # ... lógica GET/POST com MinisterioEditForm ...
#     pass

# ==================================================
# ========= FIM: VIEWS PARA MEU MINISTÉRIO =========
# ==================================================




@login_required
@user_passes_test(pode_editar_configuracao_org) # Proteja a view
def editar_igreja_config(request, igreja_id): # Renomeei para evitar conflito com outras views editar_igreja
    ministerio = get_ministerio_or_error(request) # Usar a função auxiliar
    # Garante que a igreja a ser editada pertence à ministério do usuário
    igreja = get_object_or_404(Igreja, pk=igreja_id, ministerio=ministerio)

    if request.method == 'POST':
        form = IgrejaEditForm(request.POST, request.FILES, instance=igreja, ministerio=ministerio)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dados da igreja '{igreja.nome_igreja}' atualizados com sucesso!")
            return redirect('configuracao:lista_igrejas') # Ou para onde você quiser redirecionar
        else:
            messages.error(request, "Erro ao atualizar os dados da igreja. Verifique os campos.")
            # print("ERROS NO FORMULÁRIO IgrejaEditForm:", form.errors.as_json()) # Removido para produção

    else:
        form = IgrejaEditForm(instance=igreja, ministerio=ministerio)

    context = {
        'form': form,
        'igreja': igreja,
        'titulo_pagina': f"Editar Igreja: {igreja.nome_igreja}"
    }
    return render(request, 'configuracao/igrejas/editar_igreja_config.html', context) # Ajustado para 'igrejas' no plural


# Adicione esta view ao seu c:\Gereigreja\configuracao\views.py
# Certifique-se de importar IgrejaEditForm (ou um IgrejaCreateForm se preferir)
# e outras dependências como login_required, user_passes_test, messages, redirect, etc.
# from django.utils import timezone # Adicionado para gerenciar_assinatura
# from .utils import pode_editar_configuracao_org (ou uma permissão similar)

@login_required
@user_passes_test(pode_editar_configuracao_org) # Use a permissão apropriada
def adicionar_igreja(request):
    ministerio = get_ministerio_or_error(request) # Usar a função auxiliar

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
            messages.success(request, f"Igreja '{nova_igreja.nome_igreja}' adicionada com sucesso!")
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



@login_required
def gerenciar_assinatura(request):
    # Obter a ministério diretamente do perfil do usuário
    ministerio = get_ministerio_or_error(request)
    assinatura_atual = AssinaturaMinisterio.objects.filter(ministerio=ministerio).order_by('-data_inicio').first()
    planos_disponiveis = Plano.objects.filter(ativo=True, is_visible=True)

    # Verifica se o plano gratuito está ativo e o limite foi excedido
    if assinatura_atual and assinatura_atual.status == 'gratuita' and assinatura_atual.plano and assinatura_atual.plano.preco_mensal == 0:
        total_membros = 0
        for igreja in ministerio.igrejas.all():
            total_membros += igreja.membros.count()
        if assinatura_atual.plano.limite_membros and total_membros > assinatura_atual.plano.limite_membros:
            assinatura_atual.status = 'vencida'
            assinatura_atual.save()
    """
    Permite ao administrador do ministério visualizar os planos disponíveis,
    ver sua assinatura atual e escolher/alterar um plano.
    """
    # Obter a ministério diretamente do perfil do usuário
    ministerio = get_ministerio_or_error(request)
    assinatura_atual = AssinaturaMinisterio.objects.filter(ministerio=ministerio).order_by('-data_inicio').first()
    planos_disponiveis = Plano.objects.filter(ativo=True, is_visible=True)

    mostrar_opcao_cortesia = False

    # Consulta histórico de mensalidades e cortesias
    historico_assinatura = ministerio.historicos_assinatura.select_related('plano').order_by('-data_inicio')

    if request.method == 'POST':
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
        stripe_coupon = request.POST.get('stripe_coupon')
        if not plano_id_selecionado or not ciclo_pagamento_selecionado:
            messages.error(request, "Nenhum plano foi selecionado.")
            return redirect('configuracao:gerenciar_assinatura')
        try:
            plano_escolhido = Plano.objects.get(id=plano_id_selecionado, ativo=True)

            # Se o plano é gratuito, verifica limite de membros antes de ativar
            if plano_escolhido.preco_mensal == 0:
                total_membros = ministerio.membros.count()
                if plano_escolhido.limite_membros and total_membros > plano_escolhido.limite_membros:
                    messages.error(request, f"Este plano permite até {plano_escolhido.limite_membros} pessoas. Seu ministério possui {total_membros} membros. Faça um upgrade para um plano maior.")
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
                'success_url': request.build_absolute_uri(reverse('configuracao:gerenciar_assinatura')) + '?status=success',
                'cancel_url': request.build_absolute_uri(reverse('configuracao:gerenciar_assinatura')) + '?status=cancelled',
                'metadata': {
                    'ministerio_id': ministerio.id,
                    'user_id': request.user.id,
                    'plano_id': plano_escolhido.id,
                    'ciclo_pagamento': ciclo_pagamento_selecionado,
                }
            }
            if stripe_coupon:
                checkout_params['discounts'] = [{ 'coupon': stripe_coupon }]

            checkout_session = stripe.checkout.Session.create(**checkout_params)

            return redirect(checkout_session.url, code=303)
        except Plano.DoesNotExist:
            messages.error(request, "O plano selecionado não é válido ou não está mais disponível.")
            return redirect('configuracao:gerenciar_assinatura')
        except Exception as e:
            logger.error(f"Erro ao processar escolha de plano para ministério {ministerio.id}: {e}")
            messages.error(request, "Ocorreu um erro ao processar sua solicitação. Tente novamente.")
            return redirect('configuracao:gerenciar_assinatura')
    
    # Lógica para mostrar opção de cortesia no GET
    if assinatura_atual and assinatura_atual.status == 'vencida' and not assinatura_atual.is_periodo_cortesia_valido():
        mostrar_opcao_cortesia = True

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

    context = {
        'ministerio': ministerio,
        'assinatura_atual': assinatura_atual,
        'planos_disponiveis': planos_disponiveis,
        'titulo_pagina': "Gerenciar Assinatura",
        'aviso_vencimento_proximo': aviso_vencimento_proximo,
        'dias_para_vencer': dias_para_vencer,
        'mostrar_opcao_cortesia': mostrar_opcao_cortesia,
        'tempo_cortesia_restante': tempo_cortesia_restante,
    }
    context['historico_assinatura'] = historico_assinatura
    return render(request, 'configuracao/assinatura/gerenciar_assinatura.html', context)

# Adicionar ao final de c:\Gereigreja\configuracao\views.py

@login_required
def set_active_church(request):
    if request.method == 'POST':
        igreja_id_selecionada_str = request.POST.get('igreja_id_selector') # Nome do campo no formulário do seletor

        if not request.user.is_authenticated or not hasattr(request.user, 'perfil') or not request.user.perfil:
            messages.error(request, "Você precisa estar logado e ter um perfil para selecionar uma igreja.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('secretaria:dashboard')))

        if igreja_id_selecionada_str:
            if igreja_id_selecionada_str == "todas": # Opção para limpar a seleção
                if 'igreja_ativa_id' in request.session:
                    del request.session['igreja_ativa_id']
                messages.info(request, "Visualização consolidada (todas as igrejas permitidas) ativada.")
            else:
                try:
                    igreja_id_int = int(igreja_id_selecionada_str)
                    # Verificar se o usuário tem permissão para esta igreja
                    allowed_churches = get_allowed_churches_for_user(request.user) # Função agora está no escopo
                    igreja_selecionada_obj = allowed_churches.get(pk=igreja_id_int)
                    
                    request.session['igreja_ativa_id'] = igreja_selecionada_obj.pk
                    request.session.modified = True # Garante que a sessão seja salva
                    messages.success(request, f"Contexto alterado para a igreja: {igreja_selecionada_obj.nome_igreja}.")
                
                except (ValueError, TypeError): # TypeError se igreja_id_selecionada_str não for conversível para int
                    messages.error(request, "ID de igreja inválido.")
                except Igreja.DoesNotExist:
                    messages.error(request, "Igreja selecionada inválida ou não permitida.")
                except Exception as e:
                    logger.error(f"Erro ao definir igreja ativa para usuário {request.user.username} (ID: {request.user.id}): {e}")
                    messages.error(request, "Ocorreu um erro ao tentar alterar o contexto da igreja.")
        else:
            # Se nenhum ID for enviado (ou for vazio), pode ser interpretado como limpar a seleção
            if 'igreja_ativa_id' in request.session:
                del request.session['igreja_ativa_id']
            messages.info(request, "Contexto de igreja removido. Visualizando dados de todas as igrejas permitidas.")

    # Redirecionar para a página anterior ou para o dashboard
    redirect_url = request.META.get('HTTP_REFERER', reverse('secretaria:dashboard')) # Ajuste 'secretaria:dashboard' se necessário
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

    # Aqui você pode adicionar lógica para um formulário de edição do perfil, se desejar.
    # Por enquanto, apenas exibiremos os dados.

    logger.debug(f"Usuário: {request.user}")
    logger.debug(f"PerfilUsuario: {perfil_usuario}")
    logger.debug(f"Ministério: {perfil_usuario.ministerio if perfil_usuario else None}")

    context = {
        'perfil_usuario': perfil_usuario,
        'usuario': request.user,
        'titulo_pagina': "Meu Perfil",
        'ministerio': perfil_usuario.ministerio # Adiciona a ministério ao contexto

    }
    return render(request, 'configuracao/perfil/meu_perfil.html', context) # Crie este template
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
                # print("[DEBUG VIEW] Após salvar perfil_form, foto_perfil:", perfil_usuario.foto_perfil) # Removido para produção
                logger.info("perfil_form salvo com sucesso.")

                # --- DEBUG: Mostra o valor do campo de imagem após salvar ---
                logger.info(f"[DEBUG view] Valor de perfil_usuario.foto_perfil: {perfil_usuario.foto_perfil}")
                # print(f"[DEBUG view] Valor de perfil_usuario.foto_perfil: {perfil_usuario.foto_perfil}") # Removido para produção

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

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

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
                        'id_transacao_gateway': stripe_subscription_id,
                    }
                )
                logger.info(f"Assinatura para a ministério '{ministerio.nome_fantasia}' foi ativada/atualizada via webhook do Stripe.")

        except (Ministerio.DoesNotExist, Plano.DoesNotExist) as e:
            logger.error(f"Erro no webhook do Stripe: Ministério ou Plano não encontrado. Detalhes: {e}")
            return HttpResponse(status=404)
        except Exception as e:
            logger.error(f"Erro crítico ao processar webhook do Stripe: {e}")
            return HttpResponse(status=500)

    # Adicione outros tipos de evento se necessário (ex: 'invoice.payment_failed')

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