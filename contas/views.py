# c:\Gereigreja\contas\views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.views.generic import TemplateView # Adicionar TemplateView
from django.core.exceptions import PermissionDenied # Importar PermissionDenied
from django.http import Http404 # Importar Http404
import logging

# Models e Forms

from configuracao.models import Ministerio, PerfilUsuario, Plano, AssinaturaMinisterio # Adicionar Plano e AssinaturaMinisterio
from secretaria.models import Membro # Importar Membro

from .models import Convite
from .forms import (
    RegistroForm,
    ConviteForm,
    AceitarConviteSetPasswordForm,
    EditarPapeisUsuarioForm
)
from core.decorators import verificar_assinatura_valida # Ou o caminho correto
from core.utils import get_ministerio_or_error # Importar de core.utils

@login_required
@verificar_assinatura_valida # Nosso novo decorator
def minha_view_protegida(request):
    ministerio = get_ministerio_or_error(request) # Ainda chama para obter a org e verificar org.ativo
    # ... resto da view ...

# --- NOVA VIEW PARA A LANDING PAGE ---
class LandingPageView(TemplateView):
    template_name = 'contas/landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passa os planos visíveis para o template
        context['planos'] = Plano.objects.filter(is_visible=True, ativo=True).order_by('preco_mensal')
        return context
# --- FIM DA NOVA VIEW ---

logger = logging.getLogger(__name__)

# --- VIEW DE REGISTRO ---
def registrar_usuario_e_org(request):
    """ View para lidar com o autocadastro de usuário e ministério. """
    if request.user.is_authenticated:
        return redirect('secretaria:dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            senha = form.cleaned_data['senha']
            primeiro_nome = form.cleaned_data['primeiro_nome']
            ultimo_nome = form.cleaned_data['ultimo_nome']
            nome_fantasia_org = form.cleaned_data['nome_fantasia_org']

            try:
                with transaction.atomic():
                    novo_usuario = User.objects.create_user(
                        username=email,
                        email=email,
                        password=senha,
                        first_name=primeiro_nome,
                        last_name=ultimo_nome,
                        is_active=True
                    )
                    nova_ministerio = Ministerio.objects.create(
                        nome_fantasia=nome_fantasia_org,
                        administrador_principal=novo_usuario,
                        ativo=False
                    )
                    PerfilUsuario.objects.create(
                        user=novo_usuario,
                        ministerio=nova_ministerio
                    )

                    # --- LÓGICA PARA ATRIBUIR PLANO GRATUITO SE ELEGÍVEL ---
                    try:
                        plano_pioneiro = Plano.objects.get(nome='pioneiro')
                        # Verifica se o plano pioneiro está ativo E se a ministério é elegível
                        if plano_pioneiro.ativo and nova_ministerio.verificar_elegibilidade_plano_gratuito():
                            AssinaturaMinisterio.objects.create(
                                ministerio=nova_ministerio,
                                plano=plano_pioneiro,
                                data_inicio=timezone.now(),
                                status='gratuita'
                            )
                            # Ativa automaticamente o ministério se for pioneiro
                            nova_ministerio.ativo = True
                            nova_ministerio.save(update_fields=['ativo'])
                            # Adiciona o usuário ao grupo Admin Ministerio
                            from django.contrib.auth.models import Group
                            grupo_admin, _ = Group.objects.get_or_create(name='Admin Ministerio')
                            novo_usuario.groups.add(grupo_admin)
                            logger.info(f"Usuário '{email}' adicionado ao grupo Admin Ministerio.")
                            logger.info(f"Ministério '{nome_fantasia_org}' ativado automaticamente no plano Pioneiro.")
                            logger.info(f"Novo usuário '{email}' e ministério '{nome_fantasia_org}' registrados e ativados com sucesso.")
                            login(request, novo_usuario)
                            # Atualiza a sessão para refletir os novos grupos
                            from django.contrib.auth import update_session_auth_hash
                            update_session_auth_hash(request, novo_usuario)
                            messages.success(request, f'Bem-vindo, {primeiro_nome}! Seu registro e o da ministério "{nome_fantasia_org}" foram concluídos e ativados. Aproveite o sistema!')
                            return redirect('secretaria:dashboard')
                        else:
                            # Opcional: Criar uma assinatura pendente para um plano padrão ou deixar sem assinatura
                            logger.info(f"Ministério '{nome_fantasia_org}' não elegível para plano Pioneiro no momento do registro.")
                            messages.info(request, f'Seu cadastro foi realizado, mas aguarda aprovação do administrador.')
                            return redirect('contas:aguardando_aprovacao')
                    except Plano.DoesNotExist:
                        logger.warning("Plano 'pioneiro' não encontrado no banco de dados. Não será ofertado automaticamente.")
                        messages.info(request, f'Seu cadastro foi realizado, mas aguarda aprovação do administrador.')
                        return redirect('contas:aguardando_aprovacao')
                    except Exception as e_plano:
                        logger.error(f"Erro ao tentar atribuir plano para '{nome_fantasia_org}': {e_plano}")
                        messages.info(request, f'Seu cadastro foi realizado, mas aguarda aprovação do administrador.')
                        return redirect('contas:aguardando_aprovacao')
            except Exception as e: # Captura exceções da criação de usuário/org ou da lógica de plano
                logger.exception(f"Erro durante o registro do usuário {email} ou ministério {nome_fantasia_org}: {e}")
                messages.error(request, f"Ocorreu um erro inesperado durante o registro: {e}. Por favor, tente novamente ou contate o suporte.")
                # Não limpar o form aqui para o usuário não perder os dados digitados

           
        else:
            messages.error(request, "Erro no formulário. Verifique os campos e tente novamente.")

    else: # GET request
        form = RegistroForm()

    context = {'form': form}
    return render(request, 'contas/registrar.html', context)

# --- VIEW LISTAR USUÁRIOS E CONVITES ---
@login_required
def lista_usuarios_org(request):
    """ Lista os usuários associados E os convites pendentes do ministério. """
    try:
        ministerio = get_ministerio_or_error(request) # Levanta exceção se não for admin de org
    except (PermissionDenied, Http404):
        return redirect('login')
    except Exception as e:
        org_id = request.user.perfil.ministerio.id if hasattr(request.user, 'perfil') and request.user.perfil.ministerio else 'N/A'
        logger.exception(f"Erro ao listar usuários/convites para ministério {org_id}")
        messages.error(request, f"Ocorreu um erro ao listar os usuários e convites: {e}")
        return redirect('secretaria:dashboard')

    # --- NOVA VERIFICAÇÃO DE GRUPO ---
    if not request.user.groups.filter(name='Admin Ministerio').exists():
        messages.error(request, "Você não tem permissão para gerenciar usuários.")
        return redirect('secretaria:index')
    # --- FIM DA VERIFICAÇÃO ---
    usuarios_org = User.objects.filter(
        perfil__ministerio=ministerio
    ).select_related('perfil').prefetch_related('groups').order_by('first_name', 'last_name')
    convites_pendentes = Convite.objects.filter(
        ministerio=ministerio,
        status='pendente'
    ).select_related('remetente').order_by('-data_criacao')
    context = {
        'ministerio': ministerio,
        'usuarios': usuarios_org,
        'convites_pendentes': convites_pendentes,
        'titulo_pagina': 'Gerenciar Usuários e Convites'
    }
    return render(request, 'contas/lista_usuarios.html', context)

# --- VIEW ENVIAR CONVITE ---
@login_required
def enviar_convite(request):
    """ View para o Admin do Minist. enviar um convite para um novo usuário. """
    try:
        ministerio = get_ministerio_or_error(request)
    except (PermissionDenied, Http404):
        return redirect('login')
    if not request.user.groups.filter(name='Admin Ministerio').exists():
        messages.error(request, "Você não tem permissão para gerenciar usuários.")
        return redirect('secretaria:index')

    if request.method == 'POST':
        form = ConviteForm(request.POST, ministerio=ministerio)
        if form.is_valid():
            email_convidado = form.cleaned_data['email_convidado']
            try:
                novo_convite = Convite.objects.create(
                    email_convidado=email_convidado,
                    remetente=request.user,
                    ministerio=ministerio,
                    status='pendente'
                )

                # Lógica de Envio de E-mail
                current_site = get_current_site(request)
                subject = f"Convite para se juntar à ministério {ministerio.nome_fantasia}"
                accept_url = request.build_absolute_uri(
                    reverse('contas:aceitar_convite', kwargs={'token': novo_convite.token})
                )
                message_html = render_to_string('contas/email/convite_email.html', {
                    'ministerio': ministerio,
                    'remetente': request.user,
                    'accept_url': accept_url,
                    'site_name': current_site.name,
                    'protocol': 'https' if request.is_secure() else 'http',
                    'domain': current_site.domain,
                })

                try:
                    send_mail(
                        subject,
                        message_html, # Mensagem principal (pode ser texto puro)
                        settings.DEFAULT_FROM_EMAIL,
                        [email_convidado],
                        html_message=message_html # Versão HTML
                    )
                    messages.success(request, f"Convite enviado com sucesso para {email_convidado}!")
                except Exception as mail_error:
                     logger.error(f"Erro ao enviar email de convite para {email_convidado}: {mail_error}")
                     messages.warning(request, f"Convite para {email_convidado} foi criado, mas houve um erro ao enviar o e-mail. Token para teste manual: {novo_convite.token}")

                return redirect('contas:lista_usuarios')

            except Exception as e:
                logger.exception(f"Erro ao criar convite para {email_convidado} na ministério {ministerio.id}")
                messages.error(request, f"Ocorreu um erro inesperado ao criar o convite: {e}")
                # Re-renderiza o formulário em caso de erro na criação
        else:
            # Formulário inválido
            # print("ERROS NO ConviteForm:", form.errors.as_json()) # Linha de debug (remover se não precisar mais)
            messages.error(request, "Não foi possível enviar o convite. Verifique os erros abaixo.")
    else:
        # GET request
        form = ConviteForm(ministerio=ministerio)

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Convidar Novo Usuário'
    }
    return render(request, 'contas/enviar_convite.html', context)

# --- VIEW ACEITAR CONVITE ---
def aceitar_convite(request, token):
    """ View para processar o aceite de um convite usando o token. """
    convite = get_object_or_404(Convite, token=token)

    if not convite.is_valido():
        messages.error(request, "Este convite é inválido, expirou ou já foi utilizado.")
        return redirect('login')

    if request.user.is_authenticated:
        if request.user.email.lower() == convite.email_convidado.lower():
            try:
                with transaction.atomic():
                    perfil, criado = PerfilUsuario.objects.get_or_create(
                        user=request.user,
                        defaults={'ministerio': convite.ministerio}
                    )
                    if not criado and perfil.ministerio != convite.ministerio:
                        ministerio_anterior_nome = perfil.ministerio.nome_fantasia if perfil.ministerio else "uma ministério anterior"
                        perfil.ministerio = convite.ministerio
                        perfil.save()
                        messages.warning(
                            request,
                            f"Seu acesso foi atualizado para a ministério '{convite.ministerio.nome_fantasia}'. "
                            f"Você não terá mais acesso direto aos dados de '{ministerio_anterior_nome}' com esta conta."
                        )

                    convite.status = 'aceito'
                    convite.data_aceite = timezone.now()
                    convite.save()

                messages.success(request, f"Convite aceito! Você agora faz parte do ministério {convite.ministerio.nome_fantasia}.")
                return redirect('secretaria:dashboard')
            except Exception as e:
                 logger.exception(f"Erro ao aceitar convite (logado) para {convite.email_convidado}, token {token}")
                 messages.error(request, f"Ocorreu um erro ao processar o convite: {e}")
                 return redirect('secretaria:index')
        else:
            messages.warning(request, "Você estava logado com outra conta. Por favor, faça login ou crie uma conta com o e-mail do convite.")
            logout(request)
            return redirect('contas:aceitar_convite', token=token)

    # Usuário NÃO está logado.
    try:
        usuario_existente = User.objects.get(email__iexact=convite.email_convidado)
        messages.info(request, f"Encontramos uma conta para {convite.email_convidado}. Por favor, faça login para aceitar o convite.")
        login_url = reverse('login')
        next_url = reverse('contas:aceitar_convite', kwargs={'token': token})
        return redirect(f'{login_url}?next={next_url}')

    except User.DoesNotExist:
        # Usuário NÃO existe. Precisa criar conta.
        if request.method == 'POST':
            form = AceitarConviteSetPasswordForm(request.POST)
            if form.is_valid():
                senha = form.cleaned_data['senha']
                primeiro_nome = form.cleaned_data['primeiro_nome']
                ultimo_nome = form.cleaned_data['ultimo_nome']

                try:
                    with transaction.atomic():
                        novo_usuario = User.objects.create_user(
                            username=convite.email_convidado,
                            email=convite.email_convidado,
                            password=senha,
                            first_name=primeiro_nome,
                            last_name=ultimo_nome,
                            is_active=True
                        )
                        PerfilUsuario.objects.create(
                            user=novo_usuario,
                            ministerio=convite.ministerio
                        )
                        convite.status = 'aceito'
                        convite.data_aceite = timezone.now()
                        convite.save()

                    login(request, novo_usuario)
                    messages.success(request, f"Conta criada e convite aceito! Bem-vindo à ministério {convite.ministerio.nome_fantasia}, {primeiro_nome}.")
                    return redirect('secretaria:dashboard')

                except Exception as e:
                    logger.exception(f"Erro ao criar usuário/perfil ao aceitar convite para {convite.email_convidado}, token {token}")
                    messages.error(request, f"Ocorreu um erro ao finalizar seu registro: {e}")
            else:
                messages.error(request, "Erro no formulário. Verifique os campos.")
        else:
            # GET request para usuário inexistente
            form = AceitarConviteSetPasswordForm()

        context = {
            'form': form,
            'convite': convite,
            'titulo_pagina': 'Complete seu Cadastro'
        }
        return render(request, 'contas/aceitar_convite_criar_conta.html', context)

# --- VIEW CANCELAR CONVITE ---
@login_required
def cancelar_convite(request, pk):
    """ Cancela um convite pendente (requer POST). """
    try:
        ministerio = get_ministerio_or_error(request)
    except (PermissionDenied, Http404):
        return redirect('login')
    if not request.user.groups.filter(name='Admin Ministerio').exists():
        messages.error(request, "Você não tem permissão para gerenciar usuários.")
        return redirect('secretaria:index')
    convite = get_object_or_404(
        Convite,
        pk=pk,
        ministerio=ministerio,
        status='pendente'
    )

    if request.method == 'POST':
        try:
            convite.status = 'cancelado'
            convite.save(update_fields=['status'])
            messages.success(request, f"Convite para {convite.email_convidado} foi cancelado com sucesso.")
        except Exception as e:
            logger.exception(f"Erro ao cancelar convite {pk} para ministério {ministerio.id}")
            messages.error(request, f"Ocorreu um erro ao cancelar o convite: {e}")
        return redirect('contas:lista_usuarios')
    else:
        messages.error(request, "Ação inválida (requer POST).")
        return redirect('contas:lista_usuarios')

# --- VIEW EDITAR PAPÉIS/GRUPOS ---
@login_required
def editar_papeis_usuario(request, user_pk):
    """ Permite ao Admin do Minist. editar os grupos (papéis) e igrejas permitidas de um usuário. """
    try:
        ministerio = get_ministerio_or_error(request)
        # Busca o usuário alvo e seu perfil, garantindo que pertence à ministério
        usuario_alvo = get_object_or_404(
            User.objects.select_related('perfil'), # Otimiza buscando o perfil junto
            pk=user_pk,
            perfil__ministerio=ministerio
        )
        # Pega o perfil do usuário alvo (já sabemos que existe por causa do filtro acima)
        perfil_alvo = usuario_alvo.perfil

    except (PermissionDenied, Http404):
         return redirect('login')
    except User.DoesNotExist: # Caso raro, mas seguro incluir
        messages.error(request, "Usuário alvo não encontrado.")
        return redirect('contas:lista_usuarios')
    except PerfilUsuario.DoesNotExist: # Caso o select_related falhe ou haja inconsistência
        messages.error(request, f"Perfil não encontrado para o usuário {usuario_alvo.username}. Contate o suporte.")
        return redirect('contas:lista_usuarios')


    # Validações de Permissão (como antes)
    if usuario_alvo == request.user:
        messages.error(request, "Você não pode editar seus próprios acessos aqui.")
        return redirect('contas:lista_usuarios')
    if usuario_alvo == ministerio.administrador_principal:
         messages.error(request, f"Não é possível alterar os acessos do administrador principal ({usuario_alvo.get_full_name()}) por aqui.")
         return redirect('contas:lista_usuarios')

    if request.method == 'POST':
        # Passa a ministério para o form filtrar o queryset de igrejas
        form = EditarPapeisUsuarioForm(request.POST, ministerio=ministerio)
        if form.is_valid():
            try:
                with transaction.atomic(): # Garante atomicidade ao salvar grupos e igrejas
                    # Atualiza os grupos
                    grupos_selecionados = form.cleaned_data['grupos']
                    usuario_alvo.groups.set(grupos_selecionados)

                    # Atualiza as igrejas permitidas no Perfil
                    igrejas_selecionadas = form.cleaned_data['igrejas_permitidas']
                    perfil_alvo.igrejas_permitidas.set(igrejas_selecionadas)

                messages.success(request, f"Acessos do usuário {usuario_alvo.get_full_name()} atualizados com sucesso.")
                return redirect('contas:lista_usuarios')
            except Exception as e:
                logger.exception(f"Erro ao atualizar acessos do usuário {user_pk} para ministério {ministerio.id}")
                messages.error(request, f"Ocorreu um erro ao atualizar os acessos: {e}")
        else:
            messages.error(request, "Erro no formulário. Verifique os dados.")
    else:
        # GET: Preenche o formulário com os dados atuais do usuário
        form = EditarPapeisUsuarioForm(
            ministerio=ministerio, # Passa ministério para filtrar igrejas
            initial={
                'grupos': usuario_alvo.groups.all(),
                'igrejas_permitidas': perfil_alvo.igrejas_permitidas.all() # Pega igrejas do perfil
            }
        )

    context = {
        'form': form,
        'usuario_alvo': usuario_alvo,
        'ministerio': ministerio,
        # Atualizar título para refletir a edição de acessos
        'titulo_pagina': f'Editar Acessos de {usuario_alvo.get_full_name()}'
    }
    # O template continua o mesmo por enquanto, mas o título muda
    return render(request, 'contas/editar_papeis_usuario.html', context)
# --- FIM VIEW ATUALIZADA ---

# --- NOVA VIEW PARA ENVIAR LINK DE RESET PELO ADMIN ---
@login_required
def enviar_link_reset_senha(request, user_pk):
    """
    View para o Admin do Minist. enviar um link de redefinição de senha
    para um usuário específico.
    """
    # 1. Validação de permissão
    try:
        ministerio = get_ministerio_or_error(request)
    except (PermissionDenied, Http404):
        return redirect('login')
    if not request.user.groups.filter(name='Admin Ministerio').exists():
        messages.error(request, "Você não tem permissão para realizar esta ação.")
        return redirect('secretaria:index')

    # 2. Encontrar o usuário alvo, garantindo que ele pertence à ministério
    usuario_alvo = get_object_or_404(User, pk=user_pk, perfil__ministerio=ministerio)

    # 3. Gerar o token e a URL de reset manualmente
    current_site = get_current_site(request)
    context = {
        'email': usuario_alvo.email,
        'domain': current_site.domain,
        'site_name': current_site.name,
        'uid': urlsafe_base64_encode(force_bytes(usuario_alvo.pk)),
        'user': usuario_alvo,
        'token': default_token_generator.make_token(usuario_alvo),
        'protocol': 'https' if request.is_secure() else 'http',
    }

    # 4. Renderizar e enviar o e-mail
    subject = render_to_string('contas/password_reset_subject.txt', context)
    subject = ''.join(subject.splitlines()) # Remove quebras de linha do assunto
    body = render_to_string('contas/password_reset_email.html', context)

    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [usuario_alvo.email], fail_silently=False)
        messages.success(request, f"Link de redefinição de senha enviado com sucesso para {usuario_alvo.email}.")
    except Exception as e:
        logger.error(f"Erro ao enviar email de reset de senha para {usuario_alvo.email}: {e}")
        messages.error(request, f"Ocorreu um erro ao enviar o e-mail: {e}")

    # 5. Redirecionar de volta para a página de edição do membro
    try:
        membro_associado = Membro.objects.get(email__iexact=usuario_alvo.email, igreja__ministerio=ministerio)
        # Adiciona o parâmetro ?tab=... para voltar para a aba correta
        redirect_url = reverse('secretaria:editar_membro', args=[membro_associado.pk]) + '?tab=acesso-sistema'
        return redirect(redirect_url)
    except Membro.DoesNotExist:
        # Se não houver membro associado (caso raro), volta para a lista de usuários.
        return redirect('contas:lista_usuarios')

# --- VIEW ATIVAR/DESATIVAR USUÁRIO ---
@login_required
def alternar_status_usuario_org(request, user_pk):
    """ Ativa ou desativa um usuário dentro do ministério (requer POST). """
    try:
        ministerio = get_ministerio_or_error(request)
    except (PermissionDenied, Http404):
        return redirect('login')
    if not request.user.groups.filter(name='Admin Ministerio').exists():
        messages.error(request, "Você não tem permissão para gerenciar usuários.")
        return redirect('secretaria:index')
    usuario_alvo = get_object_or_404(User, pk=user_pk, perfil__ministerio=ministerio)

    # Validações de Permissão
    if usuario_alvo == request.user:
        messages.error(request, "Você não pode alterar seu próprio status de ativação.")
        return redirect('contas:lista_usuarios')
    if usuario_alvo == ministerio.administrador_principal:
         messages.error(request, f"Não é possível alterar o status do administrador principal ({usuario_alvo.get_full_name()}).")
         return redirect('contas:lista_usuarios')

    if request.method == 'POST':
        try:
            usuario_alvo.is_active = not usuario_alvo.is_active
            usuario_alvo.save(update_fields=['is_active'])
            status_msg = "ativado" if usuario_alvo.is_active else "desativado"
            messages.success(request, f'Usuário "{usuario_alvo.get_full_name()}" foi {status_msg} com sucesso.')
        except Exception as e:
            logger.exception(f"Erro ao alternar status do usuário {user_pk} para ministério {ministerio.id}")
            messages.error(request, f'Erro ao alterar status do usuário: {e}')
    else:
        messages.error(request, "Ação inválida (requer POST).")

    return redirect('contas:lista_usuarios')

@login_required
def aguardando_aprovacao(request):
    """
    Página exibida para usuários cuja ministério ainda não foi ativada.
    """
    ministerio_usuario = None
    if hasattr(request.user, 'perfil') and request.user.perfil:
        ministerio_usuario = request.user.perfil.ministerio
    
    if not ministerio_usuario:
        # Isso não deveria acontecer se o registro foi bem-sucedido
        messages.error(request, "Não foi possível identificar sua ministério. Por favor, contate o suporte.")
        return redirect('login') 

    # Verificar se a ministério já foi ativada, e se sim, redirecionar para o dashboard
    if ministerio_usuario.ativo:
        messages.info(request, f"Sua ministério '{ministerio_usuario.nome_fantasia}' já está ativa!")
        return redirect('secretaria:dashboard') # Ou a página principal após ativação

    context = {
        'ministerio': ministerio_usuario,
        'titulo_pagina': "Aguardando Aprovação da Ministério"
    }
    return render(request, 'contas/aguardando_aprovacao.html', context)