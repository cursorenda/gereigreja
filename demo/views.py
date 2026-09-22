import logging

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.core.management import call_command
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
import unicodedata
from contas.constants import ADMIN_MINISTERIO, LIDERANCA_FINANCEIRA, LIDERANCA_SECRETARIA, user_tem_grupo
from contas.page_permissions import user_can_access_page


logger = logging.getLogger(__name__)


DEMO_PROFILE_OPTIONS = [
    {'nome': 'Administrador', 'label': 'Administrador', 'aliases': ['admin', 'administrador'], 'username': 'demo_admin'},
    {'nome': 'Pastor Regional', 'label': 'Pastor Regional', 'aliases': ['pastor regional', 'pastorregional', 'regional'], 'username': 'demo_pastor_regional'},
    {'nome': 'Pastor Local', 'label': 'Pastor Local', 'aliases': ['pastor local', 'pastorlocal', 'pastor'], 'username': 'demo_pastor_local'},
    {'nome': 'Secretaria Ministerial', 'label': 'Secretaria Ministerial', 'aliases': ['secretaria ministerial', 'lideranca secretaria', 'secretaria'], 'username': 'demo_lideranca_secretaria'},
    {'nome': 'Financeiro Ministerial', 'label': 'Financeiro Ministerial', 'aliases': ['financeiro ministerial', 'tesouraria ministerial', 'lideranca financeira', 'financeiro'], 'username': 'demo_lideranca_financeira'},
    {'nome': 'Secretário Local', 'label': 'Secretário Local', 'aliases': ['secretario local', 'secretariolocal'], 'username': 'demo_secretario_local'},
    {'nome': 'Tesoureiro', 'label': 'Tesoureiro', 'aliases': ['tesoureiro'], 'username': 'demo_tesoureiro'},
    {'nome': 'Superintendente EBD', 'label': 'Superintendente EBD', 'aliases': ['superintendente ebd', 'superintendente'], 'username': 'demo_superintendente_ebd'},
    {'nome': 'Professor EBD', 'label': 'Professor EBD', 'aliases': ['professor ebd', 'professor'], 'username': 'demo_professor_ebd'},
    {'nome': 'Equipe de Recepção', 'label': 'Equipe de Recepção', 'aliases': ['recepcao', 'equipe recepcao', 'equipe de recepcao'], 'username': 'demo_recepcao'},
    {'nome': 'Equipe de Eventos', 'label': 'Equipe de Eventos', 'aliases': ['eventos', 'equipe eventos', 'equipe de eventos'], 'username': 'demo_eventos'},
    {'nome': 'Equipe de Mídia', 'label': 'Equipe de Mídia', 'aliases': ['midia', 'equipe midia', 'equipe de midia'], 'username': 'demo_midia'},
    {'nome': 'Membro', 'label': 'Membro', 'aliases': ['membro'], 'username': 'demo_membro'},
]


def _demo_profile_choices():
    return [
        {'nome': item['nome'], 'label': item['label']}
        for item in DEMO_PROFILE_OPTIONS
    ]


def _authenticate_demo_user(request, username):
    """Autentica usuário demo; se não existir, tenta repopular dados demo uma vez."""
    user = authenticate(request, username=username, password='demo123')
    if user is not None:
        return user

    if username and username.startswith('demo_'):
        try:
            call_command('popular_demo')
        except Exception:
            logger.exception(
                'Falha ao provisionar dados demo para o usuario "%s". '
                'O comando popular_demo levantou excecao.',
                username,
            )
            return None
        return authenticate(request, username=username, password='demo123')

    return None


def _resolve_demo_username(perfil_raw):
    """Resolve o username demo a partir do perfil selecionado no formulário."""
    perfil = (perfil_raw or '').strip().lower()
    perfil = unicodedata.normalize('NFKD', perfil).encode('ascii', 'ignore').decode('ascii')

    for item in DEMO_PROFILE_OPTIONS:
        normalized_name = unicodedata.normalize('NFKD', item['nome'].lower()).encode('ascii', 'ignore').decode('ascii')
        normalized_username = unicodedata.normalize('NFKD', item['username'].lower()).encode('ascii', 'ignore').decode('ascii')
        if perfil == normalized_name or perfil == normalized_username:
            return item['username']
        for alias in item.get('aliases', []):
            normalized_alias = unicodedata.normalize('NFKD', alias.lower()).encode('ascii', 'ignore').decode('ascii')
            if perfil == normalized_alias:
                return item['username']
    return None


def _demo_redirect_home(request, user=None):
    """Define a landing page pos-login para usuarios demo.

    Admin Ministerio: Centro Ministerial (visao consolidada do ministerio).
    Liderancas ministeriais: seus paineis especificos de supervisao.
    Demais perfis: dashboard da secretaria ou portal do membro.
    """
    if user is None:
        user = request.user

    # Admin Ministerio: landing ministerial consolidada (Centro Ministerial).
    # Evita portal_membro, dashboard local de Secretaria, painel financeiro local
    # e definicao arbitraria de igreja local.
    if user_tem_grupo(user, ADMIN_MINISTERIO):
        return redirect('configuracao:centro_ministerial')

    # Perfis de lideranca ministerial devem abrir seus respectivos paineis.
    if user_tem_grupo(user, LIDERANCA_FINANCEIRA):
        return redirect('financeiro:painel_lideranca_financeiro')

    if user_tem_grupo(user, LIDERANCA_SECRETARIA):
        return redirect('secretaria:painel_lideranca_secretaria')

    if user_can_access_page(user, 'dashboard_secretaria', request=request):
        return redirect('secretaria:dashboard')

    return redirect('secretaria:portal_membro')

# View para login demo: seleção de perfil e login automático
@never_cache
@ensure_csrf_cookie
@csrf_exempt
def demo_login_view(request):
    if request.method == 'POST':
        perfil = request.POST.get('perfil')
        username = _resolve_demo_username(perfil)
        if not username:
            messages.error(request, 'Perfil demo inválido.')
            return redirect('demo:demo_login')
        user = _authenticate_demo_user(request, username)
        if user is not None:
            login(request, user)
            messages.success(request, 'Você entrou no modo demonstração. Explore o sistema à vontade!')
            return _demo_redirect_home(request, user)
        else:
            messages.error(request, 'Usuário demo não encontrado. Tente "Resetar dados" e repita.')
    return render(request, 'demo/demo_login.html', {
        'perfis': _demo_profile_choices()
    })

# View para dashboard demo — redireciona para o dashboard real do sistema
def demo_dashboard_view(request):
    return _demo_redirect_home(request)

# View para trocar de perfil demo
@never_cache
@ensure_csrf_cookie
@csrf_exempt
def demo_trocar_perfil_view(request):
    if not request.user.username.startswith('demo_'):
        return redirect('demo:demo_login')
    if request.method == 'POST':
        perfil = request.POST.get('perfil')
        username = _resolve_demo_username(perfil)
        if not username:
            messages.error(request, 'Perfil demo inválido.')
            return redirect('demo:demo_trocar_perfil')
        user = _authenticate_demo_user(request, username)
        if user is not None:
            login(request, user)
            messages.success(request, f'Perfil alterado para {perfil}!')
            return _demo_redirect_home(request, user)
        else:
            messages.error(request, 'Usuário demo não encontrado. Tente "Resetar dados" e repita.')
    return render(request, 'demo/demo_trocar_perfil.html', {
        'perfis': _demo_profile_choices()
    })

# View para resetar dados demo (apenas admin demo)
def demo_reset_view(request):
    if not request.user.is_authenticated or not request.user.username.startswith('demo_'):
        return redirect('demo:demo_login')
    if request.user.username != 'demo_admin':
        messages.error(request, 'Apenas o admin demo pode resetar os dados demo.')
        return _demo_redirect_home(request)
    import subprocess
    from django.conf import settings
    try:
        subprocess.run(['python', 'manage.py', 'reset_demo'], cwd=settings.BASE_DIR, check=True)
        subprocess.run(['python', 'manage.py', 'popular_demo'], cwd=settings.BASE_DIR, check=True)
        messages.success(request, 'Dados demo resetados com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao resetar dados demo: {e}')
        return _demo_redirect_home(request)
    return _demo_redirect_home(request)
