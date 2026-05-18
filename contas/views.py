from configuracao.signals import garantir_perfilusuario
# c:\Gereigreja\contas\views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.views.generic import TemplateView # Adicionar TemplateView
from django.core.exceptions import PermissionDenied # Importar PermissionDenied
from django.http import Http404, HttpResponse, JsonResponse # Importar Http404, HttpResponse, JsonResponse
import logging
import json
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Models e Forms

from configuracao.models import Ministerio, PerfilUsuario, Plano, AssinaturaMinisterio # Adicionar Plano e AssinaturaMinisterio
from secretaria.models import Membro # Importar Membro
from contas.constants import ADMIN_MINISTERIO, user_is_admin, user_has_permission_level_or_higher

from .models import Convite, PermissionRequest
from .forms import (
    RegistroForm,
    ConviteForm,
    AceitarConviteSetPasswordForm,
    EditarPapeisUsuarioForm,
    PermissionRequestForm,
    PermissionRequestResponseForm,
)
from core.decorators import verificar_assinatura_valida, admin_ministerio_required # Ou o caminho correto

from core.utils import get_ministerio_or_error # Importar de core.utils


# --- FUNÇÃO AUXILIAR PARA CAPTURAR IP ---
def get_client_ip(request):
    """
    Captura o endereço IP real do cliente, considerando proxies.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
# --- FIM FUNÇÃO AUXILIAR ---

# --- VIEW REENVIAR CONVITE ---
@login_required
@admin_ministerio_required
def reenviar_convite(request, pk):
    """Reenvia o e-mail de convite para um usuário pendente."""
    ministerio = get_ministerio_or_error(request)
    convite = get_object_or_404(
        Convite,
        pk=pk,
        ministerio=ministerio,
        status='pendente'
    )
    if request.method == 'POST':
        current_site = get_current_site(request)
        subject = f"Convite para se juntar à ministério {ministerio.nome_fantasia}"
        accept_url = request.build_absolute_uri(
            reverse('contas:aceitar_convite', kwargs={'token': convite.token})
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
                message_html,
                settings.DEFAULT_FROM_EMAIL,
                [convite.email_convidado],
                html_message=message_html
            )
            messages.success(request, f"Convite reenviado com sucesso para {convite.email_convidado}!")
        except Exception as mail_error:
            logger.error(f"Erro ao reenviar email de convite para {convite.email_convidado}: {mail_error}")
            messages.warning(request, f"Houve um erro ao reenviar o e-mail. Token para teste manual: {convite.token}")
        return redirect('contas:lista_usuarios')
    else:
        return redirect('contas:lista_usuarios')

@login_required
@verificar_assinatura_valida # Nosso novo decorator
def minha_view_protegida(request):
    ministerio = get_ministerio_or_error(request) # Ainda chama para obter a org e verificar org.ativo
    # ... resto da view ...

# --- NOVA VIEW PARA A LANDING PAGE ---
class PublicMarketingBaseView(TemplateView):
    """Base para páginas públicas de marketing com interlinking para o blog."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from blog.models import Post

        context['recent_posts'] = Post.objects.filter(publicado=True).order_by('-publicado_em')[:3]
        return context


class LandingPageView(TemplateView):
    template_name = 'contas/landing_page.html'

    def get(self, request, *args, **kwargs):
        # Registra visita à landing (1 por sessão para não inflar)
        if not request.session.get('_funil_landing_registrado'):
            from configuracao.services_assinatura import registrar_evento_funil
            registrar_evento_funil('visita_landing', extra={'path': request.path})
            request.session['_funil_landing_registrado'] = True
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from configuracao.services_assinatura import listar_planos_landing_page
        context['planos'] = listar_planos_landing_page()
        from blog.models import Post
        context['recent_posts'] = Post.objects.filter(publicado=True).order_by('-publicado_em')[:3]
        return context


class FuncionalidadesPageView(PublicMarketingBaseView):
    template_name = 'contas/public_funcionalidades.html'


class PlanosPageView(PublicMarketingBaseView):
    template_name = 'contas/public_planos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from configuracao.services_assinatura import listar_planos_landing_page

        context['planos'] = listar_planos_landing_page()
        return context


class FaqPageView(PublicMarketingBaseView):
    template_name = 'contas/public_faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faq_items'] = [
            {
                'question': 'O Gereigreja atende igrejas pequenas e grandes?',
                'answer': 'Sim. Ha planos para diferentes fases, desde igrejas em inicio ate ministerios com varias congregacoes e equipes maiores.'
            },
            {
                'question': 'Posso testar antes de contratar?',
                'answer': 'Sim. Voce pode comecar gratuitamente e acessar a demonstracao para validar os principais fluxos de secretaria, financeiro e comunicacao.'
            },
            {
                'question': 'Em quanto tempo consigo implantar o sistema?',
                'answer': 'A implantacao inicial pode comecar no mesmo dia com cadastro, configuracoes basicas e importacao de membros. O ritmo depende do volume de dados da igreja.'
            },
            {
                'question': 'Consigo migrar dados de planilhas para o Gereigreja?',
                'answer': 'Sim. E possivel organizar os dados em planilhas padrao para migracao de membros e informacoes essenciais, reduzindo retrabalho manual.'
            },
            {
                'question': 'Como funciona o suporte tecnico?',
                'answer': 'O suporte pode ser acionado pelo proprio sistema. Planos pagos contam com canais prioritarios para acelerar atendimento e resolucao.'
            },
            {
                'question': 'Existe controle de permissao por perfil?',
                'answer': 'Sim. O sistema aplica permissoes por perfil e hierarquia, com escopo por igreja ativa para proteger dados e operacoes sensiveis.'
            },
            {
                'question': 'O sistema e seguro para dados da igreja?',
                'answer': 'Sim. O Gereigreja adota boas praticas de seguranca, controle de acesso, registros de operacao e comunicacao protegida para resguardar informacoes.'
            },
            {
                'question': 'O Gereigreja esta adequado a LGPD?',
                'answer': 'O sistema oferece recursos para apoiar governanca de dados, historico de consentimentos e rotinas administrativas alinhadas a privacidade.'
            },
            {
                'question': 'Posso usar com mais de uma congregacao?',
                'answer': 'Sim. Ha recursos para gestao multi-igreja, com separacao por unidade e visao consolidada para lideranca quando necessario.'
            },
            {
                'question': 'Quais modulos estao disponiveis no sistema?',
                'answer': 'Os principais modulos incluem secretaria, financeiro, agenda, comunicacao, configuracoes e suporte, variando conforme o plano escolhido.'
            },
            {
                'question': 'Consigo acompanhar dizimos, ofertas e despesas?',
                'answer': 'Sim. O modulo financeiro permite registrar entradas e saidas, acompanhar caixa, gerar relatorios e melhorar transparencia da prestacao de contas.'
            },
            {
                'question': 'Posso cancelar quando quiser?',
                'answer': 'Sim. O cancelamento pode ser solicitado conforme as regras do plano, e a igreja pode organizar seus dados para transicao quando necessario.'
            },
        ]
        return context
# --- FIM DA NOVA VIEW ---

logger = logging.getLogger(__name__)

# --- VIEW DE REGISTRO ---
def registrar_usuario_e_org(request):
    """ View para lidar com o autocadastro de usuário e ministério. """
    if request.user.is_authenticated:
        return redirect('secretaria:index')

    origem = request.GET.get('origem')

    # Se chegou do CTA da landing, registra clique uma vez por sessão
    if request.method == 'GET' and origem and 'landing' in origem:
        flag_key = f'_funil_cta_{origem}'
        if not request.session.get(flag_key):
            from configuracao.services_assinatura import registrar_evento_funil
            registrar_evento_funil('clique_cta', extra={'origem': origem})
            request.session[flag_key] = True

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

                    # Adiciona o usuário ao grupo Admin Ministerio (sempre)
                    from django.contrib.auth.models import Group
                    grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
                    novo_usuario.groups.add(grupo_admin)
                    logger.info(f"Usuário '{email}' adicionado ao grupo Admin Ministerio.")

                    # --- REGISTRAR CONSENTIMENTO LGPD ---
                    from .models import ConsentimentoLGPD
                    ConsentimentoLGPD.objects.create(
                        usuario=novo_usuario,
                        aceite_termos=True,
                        aceite_privacidade=True,
                        ip_consentimento=get_client_ip(request),
                        versao_termos='1.1',  # Atualizado para versão 1.1 (LGPD completo)
                        versao_privacidade='1.1',  # Atualizado em 08/03/2026
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]  # Limita a 500 caracteres
                    )
                    logger.info(f"Consentimento LGPD v1.1 registrado para usuário '{email}'")
                    # --- FIM REGISTRO CONSENTIMENTO ---

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
                            grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
                            novo_usuario.groups.add(grupo_admin)
                            logger.info(f"Usuário '{email}' adicionado ao grupo Admin Ministerio.")
                            logger.info(f"Ministério '{nome_fantasia_org}' ativado automaticamente no plano Pioneiro.")
                            logger.info(f"Novo usuário '{email}' e ministério '{nome_fantasia_org}' registrados e ativados com sucesso.")
                            login(request, novo_usuario)
                            # Atualiza a sessão para refletir os novos grupos
                            from django.contrib.auth import update_session_auth_hash
                            update_session_auth_hash(request, novo_usuario)
                            # --- FUNIL: cadastro ---
                            from configuracao.services_assinatura import registrar_evento_funil
                            registrar_evento_funil(
                                'cadastro',
                                ministerio=nova_ministerio,
                                plano=plano_pioneiro,
                                extra={'email': email, 'origem': origem or ''},
                            )
                            messages.success(request, f'Bem-vindo, {primeiro_nome}! Seu registro e o do ministério "{nome_fantasia_org}" foram concluídos e ativados.\n\nAgora cadastre a primeira igreja do seu ministério para começar a usar o sistema.')
                            return redirect('configuracao:adicionar_igreja')
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
@admin_ministerio_required
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

    usuarios_org = User.objects.filter(
        perfil__ministerio=ministerio
    ).select_related('perfil').prefetch_related('groups')

    # Filtros de busca
    nome = request.GET.get('nome', '').strip()
    email = request.GET.get('email', '').strip()
    status = request.GET.get('status', '').strip()
    if nome:
        usuarios_org = usuarios_org.filter(
            models.Q(first_name__icontains=nome) | models.Q(last_name__icontains=nome) | models.Q(username__icontains=nome)
        )
    if email:
        usuarios_org = usuarios_org.filter(email__icontains=email)
    if status == 'ativo':
        usuarios_org = usuarios_org.filter(is_active=True)
    elif status == 'inativo':
        usuarios_org = usuarios_org.filter(is_active=False)
    usuarios_org = usuarios_org.order_by('first_name', 'last_name')
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
@admin_ministerio_required
def enviar_convite(request):
    """ View para o Admin do Minist. enviar um convite para um novo usuário. """
    ministerio = get_ministerio_or_error(request)

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
                    # Garante/atualiza o PerfilUsuario para o ministério correto
                    garantir_perfilusuario(request.user, convite.ministerio)
                    convite.status = 'aceito'
                    convite.data_aceite = timezone.now()
                    convite.save()

                messages.success(request, f"Convite aceito! Você agora faz parte do ministério {convite.ministerio.nome_fantasia}.")
                return redirect('secretaria:index')
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
                        # Garante/atualiza o PerfilUsuario para o ministério correto
                        garantir_perfilusuario(novo_usuario, convite.ministerio)
                        convite.status = 'aceito'
                        convite.data_aceite = timezone.now()
                        convite.save()

                    login(request, novo_usuario)
                    messages.success(request, f"Conta criada e convite aceito! Bem-vindo à ministério {convite.ministerio.nome_fantasia}, {primeiro_nome}.")
                    return redirect('secretaria:index')

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
@admin_ministerio_required
def cancelar_convite(request, pk):
    """ Cancela um convite pendente (requer POST). """
    ministerio = get_ministerio_or_error(request)
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
@admin_ministerio_required
def editar_papeis_usuario(request, user_pk):
    """ Permite ao Admin do Minist. editar os grupos (papéis) e igrejas permitidas de um usuário. """
    ministerio = get_ministerio_or_error(request)
    
    try:
        # Busca o usuário alvo e seu perfil, garantindo que pertence à ministério
        usuario_alvo = get_object_or_404(
            User.objects.select_related('perfil'), # Otimiza buscando o perfil junto
            pk=user_pk,
            perfil__ministerio=ministerio
        )
        # Pega o perfil do usuário alvo (já sabemos que existe por causa do filtro acima)
        perfil_alvo = usuario_alvo.perfil
    except Http404:
         messages.error(request, "Usuário alvo não encontrado.")
         return redirect('contas:lista_usuarios')
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
                    
                    # --- AVISO DE REMOÇÃO DE GRUPOS ---
                    if not grupos_selecionados:
                        messages.warning(
                            request, 
                            f"⚠️ Você removeu TODOS os grupos de {usuario_alvo.get_full_name()}. "
                            f"Este usuário ficará sem acesso ao sistema e verá uma tela de 'Aguardando Permissões'. "
                            f"Considere desativar o usuário em vez disso."
                        )
                    # --- FIM DO AVISO ---
                    
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
@admin_ministerio_required
def enviar_link_reset_senha(request, user_pk):
    """
    View para o Admin do Minist. enviar um link de redefinição de senha
    para um usuário específico.
    """
    ministerio = get_ministerio_or_error(request)

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
@admin_ministerio_required
def alternar_status_usuario_org(request, user_pk):
    """ Ativa ou desativa um usuário dentro do ministério (requer POST). """
    ministerio = get_ministerio_or_error(request)
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
        return redirect('secretaria:index') # Ou a página principal após ativação

    context = {
        'ministerio': ministerio_usuario,
        'titulo_pagina': "Aguardando Aprovação da Ministério"
    }
    return render(request, 'contas/aguardando_aprovacao.html', context)


# --- VIEW PARA USUÁRIOS SEM GRUPOS (AGUARDANDO PERMISSÕES) ---
@login_required
def aguardando_acesso(request):
    """
    Página exibida para usuários autenticados que não têm grupos/papéis atribuídos.
    Mostra informações do ministério e do administrador para contato.
    """
    # Se usuário tem grupos, redireciona para dashboard
    if request.user.groups.exists():
        messages.info(request, "Suas permissões foram configuradas! Você já tem acesso ao sistema.")
        return redirect('secretaria:index')
    
    # Busca informações do ministério e admin
    ministerio_usuario = None
    admin_principal = None
    
    if hasattr(request.user, 'perfil') and request.user.perfil:
        ministerio_usuario = request.user.perfil.ministerio
        if ministerio_usuario:
            admin_principal = ministerio_usuario.administrador_principal
    
    context = {
        'ministerio': ministerio_usuario,
        'admin_principal': admin_principal,
        'titulo_pagina': "Aguardando Configuração de Permissões"
    }
    return render(request, 'contas/aguardando_acesso.html', context)


# --- VIEW MEUS DADOS LGPD (ÁREA DE PRIVACIDADE) ---
@login_required
def meus_dados_lgpd(request):
    """
    Página que mostra todos os dados pessoais coletados sobre o usuário (LGPD Art. 18º).
    Permite visualizar, exportar e gerenciar dados pessoais.
    """
    usuario = request.user
    
    # Coletar dados do usuário
    dados_usuario = {
        'username': usuario.username,
        'email': usuario.email,
        'nome_completo': usuario.get_full_name() or usuario.username,
        'primeiro_nome': usuario.first_name,
        'ultimo_nome': usuario.last_name,
        'is_active': usuario.is_active,
        'date_joined': usuario.date_joined,
        'last_login': usuario.last_login,
    }
    
    # Perfil do usuário (ministério, igreja ativa)
    perfil = None
    ministerio = None
    if hasattr(usuario, 'perfil') and usuario.perfil:
        perfil = usuario.perfil
        ministerio = perfil.ministerio
    
    # Grupos/Papéis
    grupos = list(usuario.groups.values_list('name', flat=True))
    
    # Membro associado (se houver)
    membro = None
    try:
        from secretaria.models import Membro
        # Verifica se há um membro com o mesmo email ou usuário associado
        if hasattr(usuario, 'membro'):
            membro = usuario.membro
        else:
            # Busca por email
            membro = Membro.objects.filter(email__iexact=usuario.email).first()
    except:
        pass
    
    # Consentimentos LGPD
    from .models import ConsentimentoLGPD, NotaUsuario
    consentimentos = ConsentimentoLGPD.objects.filter(usuario=usuario).order_by('-data_consentimento')
    
    # Notas pessoais
    nota_usuario = None
    try:
        nota_usuario = NotaUsuario.objects.get(usuario=usuario)
    except NotaUsuario.DoesNotExist:
        pass
    
    context = {
        'dados_usuario': dados_usuario,
        'perfil': perfil,
        'ministerio': ministerio,
        'grupos': grupos,
        'membro': membro,
        'consentimentos': consentimentos,
        'nota_usuario': nota_usuario,
        'titulo_pagina': 'Meus Dados Pessoais - LGPD'
    }
    
    return render(request, 'contas/meus_dados.html', context)


# --- VIEW EXPORTAR DADOS JSON (LGPD) ---
@login_required
def exportar_dados_json(request):
    """
    Exporta todos os dados pessoais do usuário em formato JSON (LGPD Art. 18º - Portabilidade).
    Retorna um arquivo JSON para download.
    """
    usuario = request.user
    
    # Estrutura de dados completa
    dados_exportacao = {
        'metadata': {
            'data_exportacao': timezone.now().isoformat(),
            'versao': '1.0',
            'formato': 'JSON',
            'titular': usuario.get_full_name() or usuario.username,
        },
        'usuario': {
            'username': usuario.username,
            'email': usuario.email,
            'primeiro_nome': usuario.first_name,
            'ultimo_nome': usuario.last_name,
            'nome_completo': usuario.get_full_name() or usuario.username,
            'is_active': usuario.is_active,
            'is_staff': usuario.is_staff,
            'is_superuser': usuario.is_superuser,
            'data_cadastro': usuario.date_joined.isoformat() if usuario.date_joined else None,
            'ultimo_acesso': usuario.last_login.isoformat() if usuario.last_login else None,
        },
        'ministerio': None,
        'grupos_permissoes': [],
        'membro': None,
        'consentimentos': [],
        'notas_pessoais': None,
    }
    
    # Dados do Perfil/Ministério
    if hasattr(usuario, 'perfil') and usuario.perfil:
        perfil = usuario.perfil
        ministerio = perfil.ministerio
        dados_exportacao['ministerio'] = {
            'nome': ministerio.nome_fantasia if ministerio else None,
            'igrejas_permitidas': list(perfil.igrejas_permitidas.values_list('nome_igreja', flat=True)) if perfil.igrejas_permitidas.exists() else [],
        }
    
    # Grupos e Permissões
    dados_exportacao['grupos_permissoes'] = list(usuario.groups.values_list('name', flat=True))
    
    # Dados do Membro (se associado)
    try:
        from secretaria.models import Membro
        membro = None
        if hasattr(usuario, 'membro'):
            membro = usuario.membro
        else:
            membro = Membro.objects.filter(email__iexact=usuario.email).first()
        
        if membro:
            # Montar endereço completo
            endereco_completo = ', '.join(filter(None, [
                membro.rua,
                membro.numero_casa,
                membro.complemento,
                membro.bairro_distrito,
                f"{membro.cidade}/{membro.estado}" if membro.cidade and membro.estado else membro.cidade or membro.estado,
                membro.cep
            ]))
            
            dados_exportacao['membro'] = {
                'nome_completo': membro.nome,
                'apelido': membro.apelido,
                'cpf': membro.cpf,
                'rg': membro.rg,
                'data_nascimento': membro.nascimento.isoformat() if membro.nascimento else None,
                'genero': membro.genero,
                'estado_civil': membro.estado_civil,
                'profissao': membro.profissao,
                'escolaridade': membro.escolaridade,
                'telefone': membro.telefone,
                'email': membro.email,
                'endereco_completo': endereco_completo,
                'rua': membro.rua,
                'numero': membro.numero_casa,
                'complemento': membro.complemento,
                'bairro': membro.bairro_distrito,
                'cidade': membro.cidade,
                'estado': membro.estado,
                'cep': membro.cep,
                'pais': membro.pais,
                'naturalidade': membro.naturalidade,
                'nacionalidade': membro.nacionalidade,
                'nome_pai': membro.nome_pai,
                'nome_mae': membro.nome_mae,
                'data_cadastro_sistema': membro.criado_em.isoformat() if hasattr(membro, 'criado_em') and membro.criado_em else None,
                'ultima_atualizacao': membro.atualizado_em.isoformat() if hasattr(membro, 'atualizado_em') and membro.atualizado_em else None,
            }
    except:
        pass
    
    # Consentimentos LGPD
    from .models import ConsentimentoLGPD, NotaUsuario
    consentimentos = ConsentimentoLGPD.objects.filter(usuario=usuario).order_by('-data_consentimento')
    dados_exportacao['consentimentos'] = [
        {
            'data_consentimento': c.data_consentimento.isoformat(),
            'aceite_termos': c.aceite_termos,
            'aceite_privacidade': c.aceite_privacidade,
            'versao_termos': c.versao_termos,
            'versao_privacidade': c.versao_privacidade,
            'ip': c.ip_consentimento,
            'user_agent': c.user_agent,
        }
        for c in consentimentos
    ]
    
    # Notas Pessoais
    try:
        nota = NotaUsuario.objects.get(usuario=usuario)
        dados_exportacao['notas_pessoais'] = {
            'conteudo': nota.conteudo,
            'criado_em': nota.criado_em.isoformat(),
            'atualizado_em': nota.atualizado_em.isoformat(),
        }
    except NotaUsuario.DoesNotExist:
        pass
    
    # Preparar resposta JSON
    response = HttpResponse(
        json.dumps(dados_exportacao, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    
    # Nome do arquivo com timestamp
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f'meus_dados_{usuario.username}_{timestamp}.json'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Log da exportação (auditoria)
    logger.info(f"Usuário '{usuario.username}' exportou seus dados em JSON em {timezone.now()}")
    
    return response


@login_required
def exportar_dados_pdf(request):
    """
    Gera arquivo PDF com todos os dados pessoais do usuário conforme LGPD Art. 18.
    """
    from .models import ConsentimentoLGPD, NotaUsuario
    from secretaria.models import Membro
    
    usuario = request.user
    
    # Criar buffer para o PDF
    buffer = BytesIO()
    
    # Configurar documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title=f'Dados Pessoais - {usuario.get_full_name() or usuario.username}'
    )
    
    # Container para os elementos do PDF
    elementos = []
    
    # Estilos
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'CustomTitle',
        parent=estilos['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    estilo_secao = ParagraphStyle(
        'CustomHeading',
        parent=estilos['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    estilo_info = ParagraphStyle(
        'InfoText',
        parent=estilos['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=TA_CENTER
    )
    estilo_normal = estilos['Normal']
    estilo_normal.fontSize = 10
    estilo_normal.leading = 14
    
    # Título do documento
    elementos.append(Paragraph('DADOS PESSOAIS - LGPD', estilo_titulo))
    elementos.append(Paragraph(
        f'Exportado em: {timezone.now().strftime("%d/%m/%Y às %H:%M")}',
        estilo_info
    ))
    elementos.append(Spacer(1, 20))
    
    # Seção: Dados da Conta
    elementos.append(Paragraph('Dados da Conta', estilo_secao))
    dados_conta = [
        ['Nome de Usuário:', usuario.username],
        ['E-mail:', usuario.email],
        ['Nome Completo:', usuario.get_full_name() or 'Não informado'],
        ['Conta Criada em:', usuario.date_joined.strftime('%d/%m/%Y às %H:%M') if usuario.date_joined else 'N/A'],
        ['Último Acesso:', usuario.last_login.strftime('%d/%m/%Y às %H:%M') if usuario.last_login else 'Nunca'],
        ['Status:', 'Ativa' if usuario.is_active else 'Inativa'],
    ]
    tabela_conta = Table(dados_conta, colWidths=[5*cm, 12*cm])
    tabela_conta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabela_conta)
    elementos.append(Spacer(1, 20))
    
    # Seção: Ministério
    try:
        perfil = usuario.perfil
        ministerio = perfil.ministerio
        
        elementos.append(Paragraph('Ministério/Organização', estilo_secao))
        dados_ministerio = [
            ['Nome:', ministerio.nome_fantasia if ministerio else 'Não vinculado'],
            ['Telefone Contato:', perfil.telefone_contato or 'Não informado'],
            ['WhatsApp:', perfil.whatsapp_contato or 'Não informado'],
        ]
        
        # Igrejas permitidas
        if perfil.igrejas_permitidas.exists():
            igrejas = ', '.join([igreja.nome_igreja for igreja in perfil.igrejas_permitidas.all()])
            dados_ministerio.append(['Igrejas Permitidas:', igrejas])
        
        tabela_ministerio = Table(dados_ministerio, colWidths=[5*cm, 12*cm])
        tabela_ministerio.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elementos.append(tabela_ministerio)
        elementos.append(Spacer(1, 20))
    except:
        pass
    
    # Seção: Dados Pessoais (Membro)
    try:
        membro = None
        if hasattr(usuario, 'membro'):
            membro = usuario.membro
        else:
            membro = Membro.objects.filter(email=usuario.email).first()
        
        if membro:
            elementos.append(Paragraph('Dados Pessoais (Cadastro)', estilo_secao))
            dados_membro = [
                ['Nome Completo:', membro.nome],
                ['CPF:', membro.cpf or 'Não informado'],
                ['RG:', membro.rg or 'Não informado'],
                ['Data Nascimento:', membro.nascimento.strftime('%d/%m/%Y') if membro.nascimento else 'Não informado'],
                ['Gênero:', membro.get_genero_display() if membro.genero else 'Não informado'],
                ['Estado Civil:', membro.estado_civil or 'Não informado'],
                ['Telefone:', membro.telefone or 'Não informado'],
                ['E-mail:', membro.email or 'Não informado'],
            ]
            
            # Endereço
            if any([membro.rua, membro.numero_casa, membro.bairro_distrito, membro.cidade]):
                endereco_partes = []
                if membro.rua:
                    endereco_partes.append(membro.rua)
                if membro.numero_casa:
                    endereco_partes.append(f'nº {membro.numero_casa}')
                if membro.complemento:
                    endereco_partes.append(membro.complemento)
                if membro.bairro_distrito:
                    endereco_partes.append(f'Bairro: {membro.bairro_distrito}')
                if membro.cidade and membro.estado:
                    endereco_partes.append(f'{membro.cidade}/{membro.estado}')
                if membro.cep:
                    endereco_partes.append(f'CEP: {membro.cep}')
                
                dados_membro.append(['Endereço:', ', '.join(endereco_partes)])
            
            # Outros dados
            if membro.profissao:
                dados_membro.append(['Profissão:', membro.profissao])
            if membro.escolaridade:
                dados_membro.append(['Escolaridade:', membro.escolaridade])
            if membro.naturalidade:
                dados_membro.append(['Naturalidade:', membro.naturalidade])
            if membro.nacionalidade:
                dados_membro.append(['Nacionalidade:', membro.nacionalidade])
            
            tabela_membro = Table(dados_membro, colWidths=[5*cm, 12*cm])
            tabela_membro.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elementos.append(tabela_membro)
            elementos.append(Spacer(1, 20))
    except:
        pass
    
    # Seção: Consentimentos LGPD
    consentimentos = ConsentimentoLGPD.objects.filter(usuario=usuario).order_by('-data_consentimento')
    if consentimentos.exists():
        elementos.append(PageBreak())
        elementos.append(Paragraph('Histórico de Consentimentos LGPD', estilo_secao))
        
        dados_consentimentos = [['Data', 'Termos', 'Privacidade', 'IP', 'Versão']]
        for cons in consentimentos:
            dados_consentimentos.append([
                cons.data_consentimento.strftime('%d/%m/%Y %H:%M'),
                'Sim' if cons.aceite_termos else 'Não',
                'Sim' if cons.aceite_privacidade else 'Não',
                cons.ip_consentimento or 'N/A',
                f'T:{cons.versao_termos} / P:{cons.versao_privacidade}'
            ])
        
        tabela_consentimentos = Table(dados_consentimentos, colWidths=[4*cm, 2*cm, 2.5*cm, 3*cm, 3.5*cm])
        tabela_consentimentos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elementos.append(tabela_consentimentos)
        elementos.append(Spacer(1, 20))
    
    # Rodapé informativo
    elementos.append(Spacer(1, 30))
    elementos.append(Paragraph(
        '<para alignment="center"><font size=8 color="#7f8c8d">'
        'Este documento foi gerado automaticamente em conformidade com a LGPD (Lei 13.709/2018).<br/>'
        'Para mais informações, entre em contato com o responsável pela proteção de dados.<br/>'
        f'Documento gerado em: {timezone.now().strftime("%d/%m/%Y às %H:%M:%S")}'
        '</font></para>',
        estilo_info
    ))
    
    # Construir PDF
    doc.build(elementos)
    
    # Preparar resposta
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f'meus_dados_{usuario.username}_{timestamp}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    
    # Log da exportação (auditoria)
    logger.info(f"Usuário '{usuario.username}' exportou seus dados em PDF em {timezone.now()}")
    
    return response


@login_required
def historico_consentimentos(request):
    """
    Exibe histórico detalhado de todos os consentimentos LGPD do usuário.
    """
    from .models import ConsentimentoLGPD
    
    usuario = request.user
    consentimentos = ConsentimentoLGPD.objects.filter(usuario=usuario).order_by('-data_consentimento')
    
    contexto = {
        'consentimentos': consentimentos,
        'total_consentimentos': consentimentos.count(),
    }
    
    return render(request, 'contas/historico_consentimentos.html', contexto)


# ==============================================================================
# LGPD - FASE 6 (PENDENTE): EXCLUSÃO/ANONIMIZAÇÃO DE CONTA
# ==============================================================================
# TODO CRÍTICO: Implementar exclusão/anonimização de dados do usuário
#
# DECISÃO NECESSÁRIA: Escolher entre 3 abordagens
#
# OPÇÃO 1 - ANONIMIZAÇÃO (Recomendada LGPD):
#   @login_required
#   def solicitar_exclusao_conta(request):
#       """
#       Anonimiza dados do usuário mantendo registro funcional.
#       - Limpa: nome, email, CPF, RG, endereço, telefone
#       - Mantém: ID, relacionamentos (ex: administrador_principal)
#       - Atende: LGPD Art. 18, VI (eliminação de dados pessoais)
#       """
#       # 1. Verificar se é administrador_principal
#       # 2. Confirmar com senha
#       # 3. Exportar dados automaticamente (JSON)
#       # 4. Anonimizar User, PerfilUsuario, Membro
#       # 5. Registrar em ConsentimentoLGPD
#       # 6. Email de confirmação
#       # 7. Logout
#       pass
#
# OPÇÃO 2 - TRANSFERÊNCIA + EXCLUSÃO:
#   @login_required
#   def solicitar_exclusao_conta(request):
#       """Exige transferência de propriedade antes de excluir."""
#       ministerios = Ministerio.objects.filter(administrador_principal=request.user)
#       if ministerios.exists():
#           # Redirecionar para transferir_propriedade()
#           pass
#       else:
#           # Redirecionar para confirmar_exclusao_definitiva()
#           pass
#
#   @login_required
#   def transferir_propriedade(request, ministerio_id):
#       """Interface para selecionar novo administrador."""
#       pass
#
#   @login_required
#   def confirmar_exclusao_definitiva(request):
#       """Excluir registro completamente após transferência."""
#       pass
#
# OPÇÃO 3 - HÍBRIDA:
#   Anonimizar se for admin, permitir escolha se for usuário comum.
#
# PROBLEMA TÉCNICO:
#   configuracao/models.py linha 136:
#   administrador_principal = ForeignKey(..., on_delete=models.PROTECT)
#   → Impede exclusão de administradores (lança ProtectedError)
#
# DOCUMENTAÇÃO COMPLETA:
#   Ver: docs/LGPD_IMPLEMENTACAO.md
#   Ver: melhorias no gereigreja.txt (seção === LGPD ===)
#   Ver: todo (linha 1)
#
# ARQUIVOS A MODIFICAR:
#   - contas/views.py (este arquivo) - criar views
#   - contas/urls.py - adicionar URLs
#   - contas/templates/contas/solicitar_exclusao.html - criar
#   - contas/templates/contas/meus_dados.html linha 257 - ativar botão
#   - contas/models.py - adicionar método anonimizar_usuario()?
#
# STATUS: ❌ PENDENTE - Aguardando decisão de design
# PRIORIDADE: ALTA (requisito legal LGPD)
# DATA: 08/03/2026
# ==============================================================================


# ==============================================================================
# LGPD - EDIÇÃO DE DADOS PESSOAIS (Art. 18, III)
# ==============================================================================

@login_required
def editar_meu_perfil(request):
    """
    Permite ao usuário editar seus dados pessoais (User + PerfilUsuario).
    
    Conformidade LGPD Art. 18, III - Direito de correção de dados incompletos,
    inexatos ou desatualizados.
    
    Detecta se há Membro vinculado e mostra comparação de dados para
    sincronização opcional.
    """
    from .forms import EditarMeuPerfilForm
    from secretaria.models import Membro
    from configuracao.models import PerfilUsuario
    
    usuario = request.user
    
    # Buscar ou criar PerfilUsuario
    try:
        perfil = usuario.perfil
    except PerfilUsuario.DoesNotExist:
        perfil = PerfilUsuario.objects.create(
            user=usuario,
            ministerio=usuario.ministerios_administrados.first()  # Fallback
        )
    
    # Detectar Membro vinculado
    membro = None
    membro_vinculo_tipo = None
    
    if hasattr(usuario, 'membro_secretaria') and usuario.membro_secretaria:
        # Vínculo direto OneToOne
        membro = usuario.membro_secretaria
        membro_vinculo_tipo = 'direto'
    else:
        # Busca por email
        membro = Membro.objects.filter(email__iexact=usuario.email).first()
        if membro:
            membro_vinculo_tipo = 'email'
    
    # Comparar dados se houver membro
    dados_diferentes = False
    diferencas = {}
    
    if membro:
        # Comparar nome
        nome_completo_user = f"{usuario.first_name} {usuario.last_name}".strip()
        if nome_completo_user != membro.nome:
            dados_diferentes = True
            diferencas['nome'] = {
                'usuario': nome_completo_user or 'Não informado',
                'membro': membro.nome or 'Não informado'
            }
        
        # Comparar email
        if usuario.email.lower() != (membro.email or '').lower():
            dados_diferentes = True
            diferencas['email'] = {
                'usuario': usuario.email,
                'membro': membro.email or 'Não informado'
            }
        
        # Comparar telefone
        telefone_user = perfil.telefone_contato or ''
        telefone_membro = membro.telefone or ''
        if telefone_user != telefone_membro:
            dados_diferentes = True
            diferencas['telefone'] = {
                'usuario': telefone_user or 'Não informado',
                'membro': telefone_membro or 'Não informado'
            }
    
    if request.method == 'POST':
        form = EditarMeuPerfilForm(
            request.POST,
            request.FILES,
            initial={'user_id': usuario.id}
        )
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Atualizar User
                    usuario.first_name = form.cleaned_data['primeiro_nome']
                    usuario.last_name = form.cleaned_data['ultimo_nome']
                    usuario.email = form.cleaned_data['email']
                    usuario.username = form.cleaned_data['email']  # Sincronizar username
                    usuario.save()
                    
                    # Atualizar PerfilUsuario
                    perfil.telefone_contato = form.cleaned_data.get('telefone_contato', '')
                    perfil.whatsapp_contato = form.cleaned_data.get('whatsapp_contato', '')
                    
                    # Foto de perfil
                    if 'foto_perfil' in request.FILES:
                        perfil.foto_perfil = form.cleaned_data['foto_perfil']
                    
                    perfil.save()
                    
                    logger.info(f"Usuário '{usuario.username}' atualizou seus dados pessoais")
                    messages.success(request, '✅ Seus dados foram atualizados com sucesso!')
                    
                    # Redirecionar de volta para a página (recarregar com novos dados)
                    return redirect('contas:editar_meu_perfil')
                    
            except Exception as e:
                logger.error(f"Erro ao atualizar perfil do usuário '{usuario.username}': {e}")
                messages.error(request, f'❌ Erro ao salvar alterações: {str(e)}')
        else:
            messages.error(request, '❌ Por favor, corrija os erros no formulário.')
    
    else:
        # GET - Preencher form com dados atuais
        initial_data = {
            'user_id': usuario.id,
            'primeiro_nome': usuario.first_name,
            'ultimo_nome': usuario.last_name,
            'email': usuario.email,
            'telefone_contato': perfil.telefone_contato,
            'whatsapp_contato': perfil.whatsapp_contato,
        }
        form = EditarMeuPerfilForm(initial=initial_data)
    
    contexto = {
        'form': form,
        'membro': membro,
        'membro_vinculo_tipo': membro_vinculo_tipo,
        'dados_diferentes': dados_diferentes,
        'diferencas': diferencas,
        'perfil': perfil,
    }
    
    return render(request, 'contas/editar_meu_perfil.html', contexto)


@login_required
def sincronizar_dados_membro(request):
    """
    Sincroniza dados de User/PerfilUsuario para o registro de Membro.
    
    Copia:
    - User.first_name + last_name → Membro.nome
    - User.email → Membro.email
    - PerfilUsuario.telefone_contato → Membro.telefone
    
    Requer confirmação via POST para segurança.
    """
    from secretaria.models import Membro
    from configuracao.models import PerfilUsuario
    
    if request.method != 'POST':
        messages.warning(request, '⚠️ Método não permitido.')
        return redirect('contas:editar_meu_perfil')
    
    usuario = request.user
    
    # Buscar PerfilUsuario
    try:
        perfil = usuario.perfil
    except PerfilUsuario.DoesNotExist:
        messages.error(request, '❌ Perfil de usuário não encontrado.')
        return redirect('contas:editar_meu_perfil')
    
    # Buscar Membro vinculado
    membro = None
    if hasattr(usuario, 'membro_secretaria') and usuario.membro_secretaria:
        membro = usuario.membro_secretaria
    else:
        membro = Membro.objects.filter(email__iexact=usuario.email).first()

    # Permitir acesso sem membro apenas para Admin Ministerio
    if not membro:
        if not usuario.groups.filter(name="Admin Ministerio").exists():
            messages.error(request, '❌ Você não possui cadastro de membro vinculado.')
            return redirect('contas:editar_meu_perfil')
    
    try:
        with transaction.atomic():
            # Sincronizar dados
            nome_completo = f"{usuario.first_name} {usuario.last_name}".strip()
            
            dados_anteriores = {
                'nome': membro.nome,
                'email': membro.email,
                'telefone': membro.telefone
            }
            
            membro.nome = nome_completo
            membro.email = usuario.email
            membro.telefone = perfil.telefone_contato or membro.telefone  # Não apaga se vazio
            membro.save()
            
            logger.info(
                f"Usuário '{usuario.username}' sincronizou dados com Membro ID {membro.chave}. "
                f"Dados anteriores: {dados_anteriores}"
            )
            
            messages.success(
                request,
                '✅ Dados sincronizados com sucesso! '
                f'Seu cadastro de membro em "{membro.igreja.nome_igreja}" foi atualizado.'
            )
            
    except Exception as e:
        logger.error(f"Erro ao sincronizar dados de '{usuario.username}' com Membro: {e}")
        messages.error(request, f'❌ Erro ao sincronizar dados: {str(e)}')
    
    return redirect('contas:editar_meu_perfil')


def _resolve_ministerio_for_permissions(request):
    perfil = getattr(request.user, 'perfil', None)
    ministerio = getattr(perfil, 'ministerio', None)
    if ministerio:
        return ministerio

    igreja_ativa = getattr(request, 'igreja_ativa', None)
    if igreja_ativa:
        return igreja_ativa.ministerio
    return None


@login_required
def hub_permissoes(request):
    ministerio = _resolve_ministerio_for_permissions(request)
    igreja_ativa = getattr(request, 'igreja_ativa', None)
    is_admin = user_has_permission_level_or_higher(request.user, ADMIN_MINISTERIO)

    minhas_solicitacoes = PermissionRequest.objects.filter(
        usuario_solicitante=request.user
    ).select_related('grupo_solicitado', 'usuario_aprovador').order_by('-data_solicitacao')[:10]

    stats_usuario = {
        'pendentes': PermissionRequest.objects.filter(usuario_solicitante=request.user, status='pending').count(),
        'aprovadas': PermissionRequest.objects.filter(usuario_solicitante=request.user, status='approved').count(),
        'rejeitadas': PermissionRequest.objects.filter(usuario_solicitante=request.user, status='rejected').count(),
    }

    solicitacoes_pendentes = None
    stats_admin = None
    if is_admin:
        solicitacoes_pendentes = PermissionRequest.objects.select_related(
            'usuario_solicitante',
            'grupo_solicitado',
            'igreja_contexto',
        ).filter(status='pending')
        if ministerio:
            solicitacoes_pendentes = solicitacoes_pendentes.filter(ministerio=ministerio)
        solicitacoes_pendentes = solicitacoes_pendentes.order_by('-data_solicitacao')[:10]

        stats_admin = {
            'pendentes': PermissionRequest.objects.filter(status='pending', ministerio=ministerio).count() if ministerio else PermissionRequest.objects.filter(status='pending').count(),
            'aprovadas_hoje': PermissionRequest.objects.filter(
                status='approved',
                data_resposta__date=timezone.now().date(),
            ).count(),
        }

    if request.method == 'POST':
        form = PermissionRequestForm(request.POST, user=request.user, ministerio=ministerio, igreja_ativa=igreja_ativa)
        if form.is_valid():
            solicitacao = PermissionRequest.objects.create(
                usuario_solicitante=request.user,
                grupo_solicitado=form.cleaned_data['grupo'],
                justificativa=form.cleaned_data['justificativa'],
                prioridade=form.cleaned_data['prioridade'],
                ministerio=ministerio,
                igreja_contexto=form.cleaned_data.get('igreja_contexto'),
            )
            messages.success(
                request,
                f'Solicitacao enviada com sucesso. Grupo solicitado: {solicitacao.grupo_solicitado.name}.',
            )
            return redirect('contas:hub_permissoes')
    else:
        form = PermissionRequestForm(user=request.user, ministerio=ministerio, igreja_ativa=igreja_ativa)

    context = {
        'form': form,
        'minhas_solicitacoes': minhas_solicitacoes,
        'stats_usuario': stats_usuario,
        'is_admin': is_admin,
        'solicitacoes_pendentes': solicitacoes_pendentes,
        'stats_admin': stats_admin,
        'grupos_atuais': request.user.groups.all(),
    }
    return render(request, 'contas/hub_permissoes.html', context)


@login_required
def solicitar_permissao(request):
    ministerio = _resolve_ministerio_for_permissions(request)
    igreja_ativa = getattr(request, 'igreja_ativa', None)

    if request.method == 'POST':
        form = PermissionRequestForm(request.POST, user=request.user, ministerio=ministerio, igreja_ativa=igreja_ativa)
        if form.is_valid():
            PermissionRequest.objects.create(
                usuario_solicitante=request.user,
                grupo_solicitado=form.cleaned_data['grupo'],
                justificativa=form.cleaned_data['justificativa'],
                prioridade=form.cleaned_data['prioridade'],
                ministerio=ministerio,
                igreja_contexto=form.cleaned_data.get('igreja_contexto'),
            )
            messages.success(request, 'Solicitacao enviada com sucesso.')
            return redirect('contas:minhas_solicitacoes')
        messages.error(request, 'Erro no formulario. Verifique os campos.')
    else:
        form = PermissionRequestForm(user=request.user, ministerio=ministerio, igreja_ativa=igreja_ativa)

    stats = {
        'pendentes': PermissionRequest.objects.filter(usuario_solicitante=request.user, status='pending').count(),
        'aprovadas': PermissionRequest.objects.filter(usuario_solicitante=request.user, status='approved').count(),
        'rejeitadas': PermissionRequest.objects.filter(usuario_solicitante=request.user, status='rejected').count(),
    }
    return render(
        request,
        'contas/solicitar_permissao.html',
        {
            'form': form,
            'stats': stats,
            'grupos_atuais': request.user.groups.all(),
        },
    )


@login_required
def minhas_solicitacoes(request):
    solicitacoes = PermissionRequest.objects.filter(
        usuario_solicitante=request.user
    ).select_related('grupo_solicitado', 'usuario_aprovador')

    status_filter = request.GET.get('status')
    if status_filter:
        solicitacoes = solicitacoes.filter(status=status_filter)

    return render(
        request,
        'contas/minhas_solicitacoes.html',
        {'solicitacoes': solicitacoes.order_by('-data_solicitacao'), 'status_filter': status_filter},
    )


@login_required
def cancelar_solicitacao(request, pk):
    solicitacao = get_object_or_404(PermissionRequest, pk=pk, usuario_solicitante=request.user)
    if solicitacao.status != 'pending':
        messages.error(request, 'Apenas solicitacoes pendentes podem ser canceladas.')
        return redirect('contas:minhas_solicitacoes')

    if request.method == 'POST':
        solicitacao.cancelar()
        messages.success(request, 'Solicitacao cancelada com sucesso.')
        return redirect('contas:minhas_solicitacoes')

    return render(request, 'contas/cancelar_solicitacao.html', {'solicitacao': solicitacao})


@login_required
def listar_solicitacoes_pendentes(request):
    if not user_has_permission_level_or_higher(request.user, ADMIN_MINISTERIO):
        messages.error(request, 'Voce nao tem permissao para acessar esta pagina.')
        return redirect('contas:hub_permissoes')

    ministerio = _resolve_ministerio_for_permissions(request)
    solicitacoes_qs = PermissionRequest.objects.select_related(
        'usuario_solicitante',
        'grupo_solicitado',
        'igreja_contexto',
        'usuario_aprovador',
    )
    if ministerio:
        solicitacoes_qs = solicitacoes_qs.filter(ministerio=ministerio)

    status_filter = request.GET.get('status', '').strip()
    prioridade_filter = request.GET.get('prioridade', '').strip()

    if status_filter:
        solicitacoes_qs = solicitacoes_qs.filter(status=status_filter)
    if prioridade_filter:
        solicitacoes_qs = solicitacoes_qs.filter(prioridade=prioridade_filter)

    stats_base = PermissionRequest.objects.all()
    if ministerio:
        stats_base = stats_base.filter(ministerio=ministerio)

    stats = {
        'pendentes': stats_base.filter(status='pending').count(),
        'aprovadas_hoje': stats_base.filter(status='approved', data_resposta__date=timezone.now().date()).count(),
        'rejeitadas_hoje': stats_base.filter(status='rejected', data_resposta__date=timezone.now().date()).count(),
    }

    paginator = Paginator(solicitacoes_qs.order_by('-data_solicitacao'), 20)
    page_number = request.GET.get('page')
    solicitacoes = paginator.get_page(page_number)

    return render(
        request,
        'contas/listar_solicitacoes.html',
        {
            'solicitacoes': solicitacoes,
            'stats': stats,
            'status_filter': status_filter,
            'prioridade_filter': prioridade_filter,
        },
    )


@login_required
def avaliar_solicitacao(request, pk):
    if not user_has_permission_level_or_higher(request.user, ADMIN_MINISTERIO):
        messages.error(request, 'Voce nao tem permissao para avaliar solicitacoes.')
        return redirect('contas:hub_permissoes')

    ministerio = _resolve_ministerio_for_permissions(request)
    solicitacao_qs = PermissionRequest.objects.select_related(
        'usuario_solicitante',
        'grupo_solicitado',
        'usuario_aprovador',
    )
    if ministerio:
        solicitacao_qs = solicitacao_qs.filter(ministerio=ministerio)

    solicitacao = get_object_or_404(solicitacao_qs, pk=pk)
    if solicitacao.status != 'pending':
        messages.warning(request, 'Esta solicitacao ja foi processada.')
        return redirect('contas:listar_solicitacoes')

    if request.method == 'POST':
        form = PermissionRequestResponseForm(request.POST)
        if form.is_valid():
            acao = form.cleaned_data['acao']
            observacao = form.cleaned_data['observacao']
            if acao == 'aprovar':
                solicitacao.aprovar(request.user, observacao)
                messages.success(request, 'Solicitacao aprovada com sucesso.')
            else:
                solicitacao.rejeitar(request.user, observacao)
                messages.success(request, 'Solicitacao rejeitada com sucesso.')
            return redirect('contas:listar_solicitacoes')
    else:
        form = PermissionRequestResponseForm()

    return render(request, 'contas/avaliar_solicitacao.html', {'solicitacao': solicitacao, 'form': form})
