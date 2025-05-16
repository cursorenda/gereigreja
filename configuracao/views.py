# configuracao/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Importar User e login
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from django.db.models import Q # Para buscas
import logging
from .models import Igreja, Organizacao, PerfilUsuario # Certifique-se que PerfilUsuario está importado
from .forms import IgrejaForm,OrganizacaoEditForm # Importe os forms necessários
from .utils import pode_editar_configuracao_org # Importa a função
from django.contrib.auth.decorators import user_passes_test

logger = logging.getLogger(__name__)


# Função de teste de permissão (exemplo, adapte à sua lógica)
def pode_editar_configuracao_org(user):
    if not user.is_authenticated:
        return False
    # Exemplo: Admin da Organização ou um grupo específico pode editar
    return user.groups.filter(name='Admin Organizacao').exists() # ou outra lógica


def get_organizacao_or_error(request):
    """
    Obtém a organização do usuário logado.
    Levanta PermissionDenied se não autenticado, superuser, ou erro de perfil.
    Levanta Http404 se o perfil não tem organização associada.
    Retorna o objeto Organizacao em caso de sucesso.
    """
    if not request.user.is_authenticated:
        raise PermissionDenied("Usuário não autenticado.")
    try:
        if request.user.is_superuser:
             messages.info(request, "Superusuários devem usar o painel Admin para secretaria global.")
             raise PermissionDenied("Superusuário não acessa esta área.")
        perfil = request.user.perfil
        organizacao = perfil.organizacao
        if not organizacao:
            messages.error(request, "Seu usuário não está associado a nenhuma organização.")
            raise Http404("Organização não encontrada para o usuário.")
        return organizacao
    except PerfilUsuario.DoesNotExist:
        messages.error(request, "Perfil de usuário não encontrado. Contate o suporte.")
        raise PermissionDenied("Perfil de usuário não encontrado.")
    except Exception as e:
         logger.exception(f"Erro inesperado ao obter organização para usuário {request.user.username}")
         messages.error(request, f"Erro interno ao obter organização: {e}")
         raise PermissionDenied("Erro interno ao obter organização.") # Mantido, pois é um erro de configuração do usuário/perfil
# --- Fim função auxiliar ---


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
        form = OrganizacaoEditForm(request.POST, instance=organizacao)
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
    else:
        form = IgrejaEditForm(instance=igreja, organizacao=organizacao)

    context = {
        'form': form,
        'igreja': igreja,
        'titulo_pagina': f"Editar Igreja: {igreja.nome_igreja}"
    }
    return render(request, 'configuracao/igreja/editar_igreja_config.html', context) # Caminho do template atualizado


# Adicione esta view ao seu c:\Gereigreja\configuracao\views.py
# Certifique-se de importar IgrejaEditForm (ou um IgrejaCreateForm se preferir)
# e outras dependências como login_required, user_passes_test, messages, redirect, etc.
# from .forms import IgrejaEditForm # Ou um formulário específico para criação
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
        form = IgrejaEditForm(request.POST, request.FILES, organizacao=organizacao) # Removido instance=igreja
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

    context = {
        'form': form,
        'titulo_pagina': "Adicionar Nova Igreja"
    }
    # Você precisará de um template para adicionar igreja, ex: 'configuracao/igreja/adicionar_igreja.html'
    return render(request, 'configuracao/igreja/adicionar_igreja.html', context)

