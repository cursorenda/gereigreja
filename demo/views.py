from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
import unicodedata
from contas.page_permissions import user_can_access_page


def _resolve_demo_username(perfil_raw):
    """Resolve o username demo a partir do perfil selecionado no formulário."""
    perfil = (perfil_raw or '').strip().lower()
    perfil = unicodedata.normalize('NFKD', perfil).encode('ascii', 'ignore').decode('ascii')

    perfil_to_username = {
        'admin': 'demo_admin',
        'administrador': 'demo_admin',
        'tesoureiro': 'demo_tesoureiro',
        'pastor': 'demo_pastor',
        'secretario': 'demo_secretario',
        'membro': 'demo_membro',
    }
    return perfil_to_username.get(perfil)


def _demo_redirect_home(user):
    """Define landing page por permissão para evitar acesso negado no modo demo."""
    if user_can_access_page(user, 'dashboard_secretaria'):
        return redirect('secretaria:dashboard')
    return redirect('secretaria:portal_membro')

# View para login demo: seleção de perfil e login automático
def demo_login_view(request):
    if request.method == 'POST':
        perfil = request.POST.get('perfil')
        username = _resolve_demo_username(perfil)
        if not username:
            messages.error(request, 'Perfil demo inválido.')
            return redirect('demo:demo_login')
        user = authenticate(request, username=username, password='demo123')
        if user is not None:
            login(request, user)
            messages.success(request, 'Você entrou no modo demonstração. Explore o sistema à vontade!')
            return _demo_redirect_home(user)
        else:
            messages.error(request, 'Usuário demo não encontrado.')
    return render(request, 'demo/demo_login.html', {
        'perfis': [
            {'nome': 'Admin', 'label': 'Administrador'},
            {'nome': 'Tesoureiro', 'label': 'Tesoureiro'},
            {'nome': 'Pastor', 'label': 'Pastor'},
            {'nome': 'Secretário', 'label': 'Secretário'},
            {'nome': 'Membro', 'label': 'Membro'},
        ]
    })

# View para dashboard demo — redireciona para o dashboard real do sistema
def demo_dashboard_view(request):
    return _demo_redirect_home(request.user)

# View para trocar de perfil demo
def demo_trocar_perfil_view(request):
    if not request.user.username.startswith('demo_'):
        return redirect('demo:demo_login')
    if request.method == 'POST':
        perfil = request.POST.get('perfil')
        username = _resolve_demo_username(perfil)
        if not username:
            messages.error(request, 'Perfil demo inválido.')
            return redirect('demo:demo_trocar_perfil')
        user = authenticate(request, username=username, password='demo123')
        if user is not None:
            login(request, user)
            messages.success(request, f'Perfil alterado para {perfil}!')
            return _demo_redirect_home(user)
        else:
            messages.error(request, 'Usuário demo não encontrado.')
    return render(request, 'demo/demo_trocar_perfil.html', {
        'perfis': [
            {'nome': 'Admin', 'label': 'Administrador'},
            {'nome': 'Tesoureiro', 'label': 'Tesoureiro'},
            {'nome': 'Pastor', 'label': 'Pastor'},
            {'nome': 'Secretário', 'label': 'Secretário'},
            {'nome': 'Membro', 'label': 'Membro'},
        ]
    })

# View para resetar dados demo (apenas admin demo)
def demo_reset_view(request):
    if not request.user.is_authenticated or not request.user.username.startswith('demo_'):
        return redirect('demo:demo_login')
    if request.user.username != 'demo_admin':
        messages.error(request, 'Apenas o admin demo pode resetar os dados demo.')
        return _demo_redirect_home(request.user)
    import subprocess
    from django.conf import settings
    try:
        subprocess.run(['python', 'manage.py', 'reset_demo'], cwd=settings.BASE_DIR, check=True)
        subprocess.run(['python', 'manage.py', 'popular_demo'], cwd=settings.BASE_DIR, check=True)
        messages.success(request, 'Dados demo resetados com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao resetar dados demo: {e}')
        return _demo_redirect_home(request.user)
    return _demo_redirect_home(request.user)
