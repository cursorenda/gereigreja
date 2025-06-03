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
from .models import Igreja, Organizacao, PerfilUsuario, Plano, AssinaturaOrganizacao # Adicionado Plano e AssinaturaOrganizacao
from .forms import IgrejaForm, OrganizacaoEditForm, IgrejaEditForm # Adicionado IgrejaEditForm
from .utils import pode_editar_configuracao_org # Importa a função
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
# Ajuste o import de get_allowed_churches_for_user se você a moveu para core.utils
from financeiro.utils import get_allowed_churches_for_user # Importar para set_active_church

from core.utils import get_organizacao_or_error # Importar de core.utils
from .models import AtualizacaoSistema


from django.utils import timezone # Movido para o topo do arquivo ou garantir que está importado
from datetime import timedelta # Movido para o topo do arquivo ou garantir que está importado

from core.decorators import verificar_assinatura_valida # Ou o caminho correto
from .forms import UserEditForm, PerfilUsuarioEditForm


@login_required
@verificar_assinatura_valida # Nosso novo decorator
def minha_view_protegida(request):
    organizacao = get_organizacao_or_error(request) # Ainda chama para obter a org e verificar org.ativo
    # ... resto da view ...


logger = logging.getLogger(__name__)


# Função de teste de permissão (exemplo, adapte à sua lógica)
def pode_editar_configuracao_org(user):
    if not user.is_authenticated:
        return False
    # Exemplo: Admin da Organização ou um grupo específico pode editar
    return user.groups.filter(name='Admin Organizacao').exists() # ou outra lógica


## A função get_organizacao_or_error foi movida para core.utils.py ##


# --- View Principal de Configuração (Lista Igrejas) ---
@login_required
def configuracao_view(request):
    """
    View principal de configuração. Lista as igrejas da organização do usuário logado.
    """
    try:
        perfil = request.user.perfil
        organizacao = perfil.organizacao
        if not organizacao:
            messages.error(request, "Seu usuário não está associado a nenhuma organização.")
            # Se for superuser, talvez redirecionar para uma visão geral?
            if request.user.is_superuser:
                 return redirect('admin:index') # Ex: para o admin do Django
            return redirect('secretaria:index')

        # Verifica se a organização está ativa (opcional, mas recomendado)
        if not organizacao.ativo and not request.user.is_superuser:
             messages.warning(request, f'Sua organização "{organizacao.nome}" ainda não foi aprovada. Algumas funcionalidades podem estar limitadas.')
             # Você pode decidir se limita o acesso aqui ou apenas mostra a mensagem

        igrejas = Igreja.objects.filter(organizacao=organizacao).order_by('tipo_igreja', 'nome_igreja')

        context = {
            'organizacao': organizacao,
            'igrejas': igrejas,
            'organizacao_ativa': organizacao.ativo # Passa o status para o template
        }
        return render(request, 'configuracao/lista_igrejas.html', context)

    except PerfilUsuario.DoesNotExist:
        if request.user.is_superuser:
             messages.info(request, "Como Superusuário, você não tem uma organização padrão. Use o painel Admin para gerenciar organizações.")
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
    """ Lista as igrejas da organização do usuário logado. """
    organizacao = get_organizacao_or_error(request)
# --- NOVA VERIFICAÇÃO DE GRUPO ---
    if not request.user.groups.filter(name='Admin Organizacao').exists():
        messages.error(request, "Você não tem permissão para gerenciar igrejas.")
        return redirect('secretaria:index') # Ou 'dashboard'
        # --- FIM DA VERIFICAÇÃO ---
    
    
    try: # <<< DESCOMENTADO
        igrejas_qs = Igreja.objects.filter(organizacao=organizacao).order_by('nome_igreja')

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
            'organizacao': organizacao,
            'current_q': query,
        }
        return render(request, 'configuracao/igrejas/lista_igrejas.html', context)
    except Exception as e: # <<< DESCOMENTADO
        logger.exception(f"Erro ao listar igrejas para organização {organizacao.id}") # <<< DESCOMENTADO
        messages.error(request, f"Ocorreu um erro ao listar as igrejas: {e}") # <<< DESCOMENTADO
        return redirect('secretaria:dashboard') # <<< DESCOMENTADO


@login_required
def adicionar_igreja(request):
    """ Cria uma nova igreja para a organização do usuário. """
    organizacao = get_organizacao_or_error(request)
    # --- NOVA VERIFICAÇÃO DE GRUPO ---
    if not request.user.groups.filter(name='Admin Organizacao').exists():
        messages.error(request, "Você não tem permissão para gerenciar igrejas.")
        return redirect('secretaria:index') # Ou 'dashboard'
        # --- FIM DA VERIFICAÇÃO ---

    if request.method == 'POST':
        form = IgrejaForm(request.POST)
        if form.is_valid():
            try:
                igreja = form.save(commit=False)
                igreja.organizacao = organizacao # Associa à organização do usuário
                igreja.save()
                messages.success(request, f'Igreja "{igreja.nome_igreja}" criada com sucesso!')
                return redirect('configuracao:lista_igrejas')
            except Exception as e:
                # Tratar erro de unicidade se houver (ex: CNPJ único)
                logger.exception(f"Erro ao salvar nova igreja para organização {organizacao.id}")
                messages.error(request, f'Erro ao salvar igreja: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = IgrejaForm()

    context = {'form': form, 'organizacao': organizacao, 'titulo_pagina': 'Adicionar Nova Igreja'}
    return render(request, 'configuracao/igrejas/form_igreja.html', context)

@login_required
def editar_igreja(request, pk):
    """ Edita uma igreja existente da organização do usuário. """
    organizacao = get_organizacao_or_error(request)
    # --- NOVA VERIFICAÇÃO DE GRUPO ---
    if not request.user.groups.filter(name='Admin Organizacao').exists():
        messages.error(request, "Você não tem permissão para gerenciar igrejas.")
        return redirect('secretaria:index') # Ou 'dashboard'
        # --- FIM DA VERIFICAÇÃO ---
        #   
    igreja = get_object_or_404(Igreja, pk=pk, organizacao=organizacao)

    if request.method == 'POST':
        form = IgrejaForm(request.POST, instance=igreja)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Igreja "{igreja.nome_igreja}" atualizada com sucesso!')
                return redirect('configuracao:lista_igrejas')
            except Exception as e:
                logger.exception(f"Erro ao editar igreja {pk} para organização {organizacao.id}")
                messages.error(request, f'Erro ao salvar igreja: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            print("ERROS NO FORMULÁRIO:", form.errors.as_json()) # Imprime os erros no console

    else:
        form = IgrejaForm(instance=igreja)

    context = {
        'form': form,
        'organizacao': organizacao,
        'titulo_pagina': f'Editar Igreja: {igreja.nome_igreja}',
        'igreja': igreja
    }
    return render(request, 'configuracao/igrejas/form_igreja.html', context)

@login_required
def excluir_igreja(request, pk):
    """ Exclui uma igreja (requer POST e confirmação). """
    organizacao = get_organizacao_or_error(request)
    # --- NOVA VERIFICAÇÃO DE GRUPO ---
    if not request.user.groups.filter(name='Admin Organizacao').exists():
        messages.error(request, "Você não tem permissão para gerenciar igrejas.")
        return redirect('secretaria:index') # Ou 'dashboard'
        # --- FIM DA VERIFICAÇÃO ---
    igreja = get_object_or_404(Igreja, pk=pk, organizacao=organizacao)

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
            logger.exception(f"Erro ao excluir igreja {pk} para organização {organizacao.id}")
            messages.error(request, f'Erro ao excluir igreja: {e}')
        return redirect('configuracao:lista_igrejas')
    else:
        # GET: Mostrar página de confirmação
        context = {'igreja': igreja, 'organizacao': organizacao}
        return render(request, 'configuracao/igrejas/confirmar_excluir_igreja.html', context)

# ==================================================
# ========= FIM: VIEWS PARA GERENCIAR IGREJAS =========
# ==================================================

# configuracao/views.py
# ... (imports e views existentes) ...

# ====================================================
# ========= INÍCIO: VIEWS PARA MINHA ORGANIZAÇÃO =========
# ====================================================

@login_required
def detalhes_organizacao(request):
    """ Exibe os detalhes da organização do usuário logado. """
    # A função get_organizacao_or_error já busca a organização correta
    # e trata os casos de erro (não logado, superuser, sem perfil, sem org)
    organizacao = get_organizacao_or_error(request)
    try:
        context = {
            'organizacao': organizacao,
            # Passar outros dados relacionados se necessário
        }
        return render(request, 'configuracao/organizacao/detalhes_organizacao.html', context)
    except Exception as e:
        # Captura erro inesperado ao renderizar (menos provável aqui)
        logger.exception(f"Erro ao exibir detalhes da organização {organizacao.id}")
        messages.error(request, f"Ocorreu um erro ao carregar os detalhes da organização: {e}")
        return redirect('secretaria:dashboard') # Redireciona para o dashboard principal

# View para editar (a implementar depois)
# @login_required
# --- NOVA VIEW ---
@login_required
def editar_organizacao(request):
    """ Permite ao Admin da Org editar os dados da sua própria organização. """
    organizacao = get_organizacao_or_error(request) # Pega a organização do usuário
# --- NOVA VERIFICAÇÃO DE GRUPO ---
    if not request.user.groups.filter(name='Admin Organizacao').exists():
        messages.error(request, "Você não tem permissão para gerenciar igrejas.")
        return redirect('secretaria:index') # Ou 'dashboard'
        # --- FIM DA VERIFICAÇÃO ---
    if request.method == 'POST':
        # Passa a instância para editar o objeto correto
        form = OrganizacaoEditForm(request.POST, request.FILES, instance=organizacao)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Dados da organização atualizados com sucesso!')
                # Redireciona de volta para a página de detalhes
                return redirect('configuracao:detalhes_organizacao')
            except Exception as e:
                logger.exception(f"Erro ao salvar organização {organizacao.id}")
                messages.error(request, f'Erro ao salvar dados da organização: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        # GET: Exibe o formulário preenchido com os dados atuais
        form = OrganizacaoEditForm(instance=organizacao)

    context = {
        'form': form,
        'organizacao': organizacao,
        'titulo_pagina': f'Editar Organização: {organizacao.nome_fantasia}'
    }
    # Criaremos um novo template para este formulário
    return render(request, 'configuracao/organizacao/form_organizacao.html', context)
# --- FIM NOVA VIEW ---

#     organizacao = get_organizacao_or_error(request)
#     # ... lógica GET/POST com OrganizacaoEditForm ...
#     pass

# ==================================================
# ========= FIM: VIEWS PARA MINHA ORGANIZAÇÃO =========
# ==================================================




@login_required
@user_passes_test(pode_editar_configuracao_org) # Proteja a view
def editar_igreja_config(request, igreja_id): # Renomeei para evitar conflito com outras views editar_igreja
    organizacao = get_organizacao_or_error(request) # Usar a função auxiliar
    # Garante que a igreja a ser editada pertence à organização do usuário
    igreja = get_object_or_404(Igreja, pk=igreja_id, organizacao=organizacao)

    if request.method == 'POST':
        form = IgrejaEditForm(request.POST, request.FILES, instance=igreja, organizacao=organizacao)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dados da igreja '{igreja.nome_igreja}' atualizados com sucesso!")
            return redirect('configuracao:lista_igrejas') # Ou para onde você quiser redirecionar
        else:
            messages.error(request, "Erro ao atualizar os dados da igreja. Verifique os campos.")
            print("ERROS NO FORMULÁRIO IgrejaEditForm:", form.errors.as_json()) # <--- ADICIONE ESTA LINHA

    else:
        form = IgrejaEditForm(instance=igreja, organizacao=organizacao)

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
    organizacao = get_organizacao_or_error(request) # Usar a função auxiliar

    if request.method == 'POST':
        # Se você usar IgrejaEditForm, ele tentará pegar uma 'instance'.
        # Para criação, é melhor não passar 'instance'.
        # Você pode criar um IgrejaCreateForm que não exija 'instance'
        # ou adaptar o IgrejaEditForm para lidar com criação.
        # Por simplicidade, vamos assumir que IgrejaEditForm pode ser usado para criar se instance=None
        form = IgrejaForm(request.POST, request.FILES, organizacao=organizacao) # Usando IgrejaForm para criação
        if form.is_valid():
            nova_igreja = form.save(commit=False)
            nova_igreja.organizacao = organizacao # Garante que a organização está definida
            nova_igreja.save()
            messages.success(request, f"Igreja '{nova_igreja.nome_igreja}' adicionada com sucesso!")
            return redirect('configuracao:lista_igrejas')
        else:
            messages.error(request, "Erro ao adicionar igreja. Verifique os campos.")
    else:
        form = IgrejaEditForm(organizacao=organizacao) # Formulário vazio para criação


    context = { # Corrigido: 'form' deve ser o objeto do formulário
        'form': form, # Corrigido
        'titulo_pagina': "Adicionar Nova Igreja",
        'organizacao': organizacao # Adicionado para o template ter acesso
    }
   
    # Você precisará de um template para adicionar igreja, ex: 'configuracao/igreja/adicionar_igreja.html'
    return render(request, 'configuracao/igrejas/form_igreja.html', context) # Reutilizando form_igreja.html



@login_required
def gerenciar_assinatura(request):
    """
    Permite ao administrador da organização visualizar os planos disponíveis,
    ver sua assinatura atual e escolher/alterar um plano.
    """
    # organizacao = get_organizacao_or_error(request) # REMOVER ESTA LINHA

    # Obter a organização diretamente do perfil do usuário,
    # permitindo acesso mesmo que a organização esteja inativa.
    organizacao = None
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.organizacao:
        organizacao = request.user.perfil.organizacao
    else:
        # Este caso não deveria ocorrer para um usuário logado com perfil,
        # mas é uma segurança.
        messages.error(request, "Não foi possível identificar sua organização. Por favor, contate o suporte.")
        return redirect('login') # Redireciona para login ou página de erro

    # Se a organização existe, mas não está ativa, exibe uma mensagem de aviso, mas continua
    if not organizacao.ativo:
        messages.warning(request, f"Sua organização '{organizacao.nome_fantasia}' ainda não está ativa. Você pode configurar sua assinatura enquanto aguarda a aprovação do sistema.")
    assinatura_atual = None
    try:
        assinatura_atual = organizacao.assinatura # Usando o related_name='assinatura'
    except AssinaturaOrganizacao.DoesNotExist:
        # Se não existe, pode ser uma organização nova que não passou pela lógica de atribuição
        # ou uma que ainda não escolheu um plano.
        pass
    except AttributeError: # Caso o related_name 'assinatura' não exista por algum motivo
        logger.warning(f"Organização {organizacao.id} não possui o atributo 'assinatura'. Verifique o related_name no modelo AssinaturaOrganizacao.")

     # Tenta criar assinatura gratuita se elegível e não tiver nenhuma, e o plano gratuito estiver ativo
    if not assinatura_atual and organizacao.verificar_elegibilidade_plano_gratuito():
        try:
            plano_gratuito = Plano.objects.get(nome='gratuito', ativo=True) # Verifica se o plano gratuito está ativo
            assinatura_atual, criada = AssinaturaOrganizacao.objects.get_or_create(
                organizacao=organizacao,
                defaults={
                    'plano': plano_gratuito,
                    'data_inicio': timezone.now(),
                    'status': 'gratuita'
                }
            )
            if criada:
                messages.info(request, "Seu plano gratuito foi ativado.")
        except Plano.DoesNotExist:
            logger.warning("Plano 'gratuito' ativo não encontrado para atribuição automática.")

    # Planos ativos, excluindo o "gratuito" se a organização não for elegível ou se já tiver um plano pago
    planos_disponiveis = Plano.objects.filter(ativo=True).exclude(nome='gratuito').order_by('preco')
    mostrar_opcao_cortesia = False

    if request.method == 'POST':
        plano_id_selecionado = request.POST.get('plano_id')
        if not plano_id_selecionado:
            messages.error(request, "Nenhum plano foi selecionado.")
            return redirect('configuracao:gerenciar_assinatura')

        try:
            plano_escolhido = Plano.objects.get(id=plano_id_selecionado, ativo=True)
             # --- LÓGICA PARA ATIVAR CORTESIA ---
            if request.POST.get('ativar_cortesia') == 'true':
                if assinatura_atual and assinatura_atual.status == 'vencida' and not assinatura_atual.is_periodo_cortesia_valido():
                    # Poderia adicionar uma lógica para limitar a concessão de cortesia (ex: uma vez)
                    assinatura_atual.periodo_cortesia_ativo = True
                    assinatura_atual.data_inicio_cortesia = timezone.now()
                    assinatura_atual.save()
                    messages.success(request, "Período de cortesia de 3 dias ativado! Você pode usar o sistema normalmente.")
                    return redirect('configuracao:gerenciar_assinatura')
                else:
                    messages.error(request, "Não foi possível ativar o período de cortesia no momento.")
            # --- FIM LÓGICA CORTESIA ---
            else: # Processamento normal de escolha de plano
                plano_escolhido = Plano.objects.get(id=plano_id_selecionado, ativo=True)

                # Lógica de "pagamento" (simulada por enquanto)
                data_inicio_nova_assinatura = timezone.now()
                data_fim_nova_assinatura = data_inicio_nova_assinatura + timedelta(days=plano_escolhido.duracao_dias)

            

            if assinatura_atual:
                # Atualiza a assinatura existente
                assinatura_atual.plano = plano_escolhido
                assinatura_atual.data_inicio = data_inicio_nova_assinatura
                assinatura_atual.data_fim = data_fim_nova_assinatura
                assinatura_atual.status = 'ativa' # Simula pagamento confirmado
                # assinatura_atual.id_transacao_gateway = "simulado_xyz" # Exemplo
                assinatura_atual.save()
                messages.success(request, f"Sua assinatura foi atualizada para o plano {plano_escolhido.get_nome_display()}!")
            else:
                # Cria uma nova assinatura
                AssinaturaOrganizacao.objects.create(
                    organizacao=organizacao,
                    plano=plano_escolhido,
                    data_inicio=data_inicio_nova_assinatura,
                    data_fim=data_fim_nova_assinatura,
                    status='ativa', # Simula pagamento confirmado
                    # id_transacao_gateway = "simulado_abc" # Exemplo
                )
                messages.success(request, f"Você assinou o plano {plano_escolhido.get_nome_display()}!")
            return redirect('configuracao:gerenciar_assinatura')

        except Plano.DoesNotExist:
            messages.error(request, "O plano selecionado não é válido ou não está mais disponível.")
        except Exception as e:
            logger.error(f"Erro ao processar escolha de plano para organização {organizacao.id}: {e}")
            messages.error(request, "Ocorreu um erro ao processar sua solicitação. Tente novamente.")
        return redirect('configuracao:gerenciar_assinatura')
    
    # Lógica para mostrar opção de cortesia no GET
    if assinatura_atual and assinatura_atual.status == 'vencida' and \
       not assinatura_atual.is_periodo_cortesia_valido():
        mostrar_opcao_cortesia = True

    aviso_vencimento_proximo = False
    dias_para_vencer = None
    if assinatura_atual and assinatura_atual.data_fim and assinatura_atual.status == 'ativa':
        dias_para_vencer_calc = (assinatura_atual.data_fim - timezone.now()).days
        if 0 <= dias_para_vencer_calc <= 7: # Se vence nos próximos 7 dias
            aviso_vencimento_proximo = True
            dias_para_vencer = dias_para_vencer_calc


    context = {
        'organizacao': organizacao,
        'assinatura_atual': assinatura_atual,
        'planos_disponiveis': planos_disponiveis,
        'titulo_pagina': "Gerenciar Assinatura",
        'aviso_vencimento_proximo': aviso_vencimento_proximo,
        'dias_para_vencer': dias_para_vencer,
        'mostrar_opcao_cortesia': mostrar_opcao_cortesia,    }

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
    # Apenas para garantir que o usuário está em uma organização válida,
    # embora as atualizações sejam globais para o sistema.
    try:
        get_organizacao_or_error(request) # Valida a organização do usuário
    except Exception: # Se get_organizacao_or_error levantar PermissionDenied ou Http404
        # Você pode decidir se quer permitir acesso mesmo sem organização
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
    # Tenta obter o PerfilUsuario associado ao usuário logado
    try:
        perfil_usuario = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        # Caso o perfil não exista por algum motivo (improvável se o sistema estiver consistente)
        # Você pode criar um perfil aqui ou redirecionar/mostrar um erro.
        # Por simplicidade, vamos assumir que o perfil deve existir.
        messages.error(request, "Perfil de usuário não encontrado. Contate o suporte.")
        return redirect('secretaria:index') # Ou outra página apropriada

    # Aqui você pode adicionar lógica para um formulário de edição do perfil, se desejar.
    # Por enquanto, apenas exibiremos os dados.

    context = {
        'perfil_usuario': perfil_usuario,
        'usuario': request.user,
        'titulo_pagina': "Meu Perfil",
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
        perfil_usuario = user.perfil
    except PerfilUsuario.DoesNotExist:
        messages.error(request, "Perfil de usuário não encontrado. Contate o suporte.")
        return redirect('configuracao:meu_perfil') # Redireciona de volta para a página de visualização

    if request.method == 'POST':
        # request.FILES é necessário para o upload da foto_perfil
        user_form = UserEditForm(request.POST, instance=user)
        perfil_form = PerfilUsuarioEditForm(request.POST, request.FILES, instance=perfil_usuario)

        if user_form.is_valid() and perfil_form.is_valid():
            try:
                with transaction.atomic(): # Garante que ambas as alterações sejam salvas ou nenhuma
                    user_form.save()
                    perfil_form.save()
                messages.success(request, 'Seu perfil foi atualizado com sucesso!')
                return redirect('configuracao:meu_perfil') # Redireciona para a página de visualização do perfil
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
    }
    return render(request, 'configuracao/perfil/editar_meu_perfil.html', context) # Crie este template
# --- FIM NOVA VIEW ---