"""
Painel de Testes de Permissões/Hierarquias - GereIgreja
Testes avançados: cria usuários temporários para cada cenário e simula acessos reais usando Django Test Client.
"""
from django.contrib.auth.models import User, Group
from contas.constants import *
from django.test import Client

def _cria_usuario_teste(username, is_staff=False, is_superuser=False, grupos=None):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    User.objects.filter(username=username).delete()
    user = User.objects.create_user(username=username, password='123', is_staff=is_staff, is_superuser=is_superuser)
    try:
        from configuracao.models import Ministerio, PerfilUsuario, ConfiguracaoSistema
        # Cria um Ministério válido e ativo, se não existir
        ministerio = Ministerio.objects.filter(ativo=True).first()
        if not ministerio:
            ministerio = Ministerio.objects.create(
                nome_fantasia='Teste Permissão',
                administrador_principal=user,
                ativo=True
            )
            # Cria configuração obrigatória para o Ministério
            ConfiguracaoSistema.objects.create(ministerio=ministerio)
        else:
            # Garante que o Ministério tenha configuração
            if not hasattr(ministerio, 'configuracao'):
                ConfiguracaoSistema.objects.create(ministerio=ministerio)
        PerfilUsuario.objects.create(user=user, ministerio=ministerio)
    except Exception as e:
        print(f'Erro ao criar PerfilUsuario/Configuracao: {e}')
    if grupos:
        for nome in grupos:
            grupo, _ = Group.objects.get_or_create(name=nome)
            user.groups.add(grupo)
    return user

def teste_superuser_tem_acesso_total(_):
    user = _cria_usuario_teste('superuser_teste', is_superuser=True, is_staff=True, grupos=[ADMIN_MINISTERIO])
    client = Client()
    client.force_login(user)
    resp = client.get('/teste-permissao/admin-ministerio/')
    User.objects.filter(username='superuser_teste').delete()
    if resp.status_code == 200:
        return True, "Superuser tem acesso total."
    return False, f"Superuser não conseguiu acesso total (HTTP {resp.status_code})."

def teste_staff_sem_grupo_nao_tem_acesso(_):
    user = _cria_usuario_teste('staff_sem_grupo', is_staff=True)
    user.is_active = True
    user.save()
    client = Client()
    client.force_login(user)
    # Checagem extra: garantir que o usuário está autenticado
    session = client.session
    if '_auth_user_id' not in session:
        User.objects.filter(username='staff_sem_grupo').delete()
        return False, "Sessão não autenticada para staff_sem_grupo."
    resp = client.get('/teste-permissao/admin-ministerio/', follow=False)
    User.objects.filter(username='staff_sem_grupo').delete()
    if resp.status_code == 403:
        return True, "Staff sem grupo bloqueado corretamente (HTTP 403)."
    elif resp.status_code == 400:
        return False, "Erro 400: Usuário de teste está sem dados obrigatórios (perfil/ministério)."
    elif resp.status_code == 302:
        location = resp.headers.get('Location', '(sem location)')
        return False, f"Staff sem grupo foi redirecionado (HTTP 302) para {location}."
    return False, f"Staff sem grupo conseguiu acesso indevido (HTTP {resp.status_code})."

def teste_staff_com_grupo_correto_tem_acesso(_):
    user = _cria_usuario_teste('staff_admin_min', is_staff=True, grupos=[ADMIN_MINISTERIO])
    client = Client()
    client.force_login(user)
    resp = client.get('/teste-permissao/admin-ministerio/')
    User.objects.filter(username='staff_admin_min').delete()
    if resp.status_code == 200:
        return True, "Staff com grupo correto acessou normalmente."
    return False, f"Staff com grupo correto não conseguiu acesso (HTTP {resp.status_code})."

def teste_staff_com_grupo_errado_bloqueado(_):
    user = _cria_usuario_teste('staff_grupo_errado', is_staff=True, grupos=[PASTOR_LOCAL])
    client = Client()
    client.force_login(user)
    resp = client.get('/teste-permissao/admin-ministerio/')
    User.objects.filter(username='staff_grupo_errado').delete()
    if resp.status_code == 403:
        return True, "Staff com grupo errado bloqueado corretamente (HTTP 403)."
    return False, f"Staff com grupo errado conseguiu acesso indevido (HTTP {resp.status_code})."

def teste_usuario_comum_bloqueado(_):
    user = _cria_usuario_teste('usuario_comum')
    client = Client()
    client.force_login(user)
    resp = client.get('/teste-permissao/admin-ministerio/')
    User.objects.filter(username='usuario_comum').delete()
    if resp.status_code == 403:
        return True, "Usuário comum bloqueado corretamente (HTTP 403)."
    return False, f"Usuário comum conseguiu acesso indevido (HTTP {resp.status_code})."

def lista_testes():
    return [
        ("Superuser tem acesso total", teste_superuser_tem_acesso_total),
        ("Staff sem grupo não tem acesso", teste_staff_sem_grupo_nao_tem_acesso),
        ("Staff com grupo correto tem acesso", teste_staff_com_grupo_correto_tem_acesso),
        ("Staff com grupo errado bloqueado", teste_staff_com_grupo_errado_bloqueado),
        ("Usuário comum bloqueado", teste_usuario_comum_bloqueado),
    ]