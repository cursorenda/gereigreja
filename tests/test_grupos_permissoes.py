"""
Script de Teste Automático - Sistema de Grupos e Permissões
Verifica se a implementação FASE 2 está funcional.

Uso: python test_grupos_permissoes.py
"""

import os
import sys
import django

# Carrega variáveis de ambiente do .env
from dotenv import load_dotenv
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Group
from contas.constants import *

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

# ===================================
# TESTES
# ===================================

def test_grupos_existem():
    """Testa se todos os 13 grupos existem no banco."""
    print_header("TESTE 1: Verificando existência dos grupos")
    
    grupos_esperados = [
        ADMIN_MINISTERIO,
        LIDERANCA_SECRETARIA,
        LIDERANCA_FINANCEIRA,
        PASTOR_REGIONAL,
        SECRETARIO_LOCAL,
        TESOUREIRO,
        SUPERINTENDENTE_EBD,
        EQUIPE_EVENTOS,
        EQUIPE_MIDIA,
        EQUIPE_RECEPCAO,
        PROFESSOR_EBD,
        SECRETARIA_EBD,
        MEMBRO_COMUM,
    ]
    
    todos_ok = True
    for nome_grupo in grupos_esperados:
        try:
            grupo = Group.objects.get(name=nome_grupo)
            print_success(f"Grupo '{nome_grupo}' existe ({grupo.permissions.count()} permissões)")
        except Group.DoesNotExist:
            print_error(f"Grupo '{nome_grupo}' NÃO EXISTE!")
            todos_ok = False
    
    return todos_ok


def test_grupos_renomeados():
    """Testa se os grupos antigos foram renomeados."""
    print_header("TESTE 2: Verificando renomeação dos grupos")
    
    grupos_antigos = [
        'Superintendentes',
        'Lider Igreja',
        'Secretario',
    ]
    
    grupos_novos = [
        SUPERINTENDENTE_EBD,
        PASTOR_REGIONAL,
        SECRETARIO_LOCAL,
    ]
    
    todos_ok = True
    
    # Verifica se grupos antigos NÃO existem
    for nome_antigo in grupos_antigos:
        if Group.objects.filter(name=nome_antigo).exists():
            print_error(f"Grupo antigo '{nome_antigo}' ainda existe!")
            todos_ok = False
        else:
            print_success(f"Grupo antigo '{nome_antigo}' foi removido")
    
    # Verifica se grupos novos EXISTEM
    for nome_novo in grupos_novos:
        if Group.objects.filter(name=nome_novo).exists():
            print_success(f"Grupo novo '{nome_novo}' existe")
        else:
            print_error(f"Grupo novo '{nome_novo}' NÃO existe!")
            todos_ok = False
    
    return todos_ok


def test_permissoes_admin():
    """Testa se Admin tem muitas permissões."""
    print_header("TESTE 3: Verificando permissões do Admin")
    
    try:
        grupo_admin = Group.objects.get(name=ADMIN_MINISTERIO)
        count = grupo_admin.permissions.count()
        
        if count > 300:
            print_success(f"Admin tem {count} permissões (esperado: >300)")
            return True
        else:
            print_warning(f"Admin tem apenas {count} permissões (esperado: >300)")
            return False
    except Group.DoesNotExist:
        print_error("Grupo Admin não existe!")
        return False


def test_funcoes_helper():
    """Testa se as funções helper estão funcionando."""
    print_header("TESTE 4: Testando funções helper")
    
    # Cria usuário de teste
    test_user, created = User.objects.get_or_create(
        username='test_helper_user',
        defaults={'email': 'test@test.com'}
    )
    
    if created:
        print_info("Usuário de teste criado")
    
    todos_ok = True
    
    # Testa user_tem_grupo
    try:
        grupo_admin = Group.objects.get(name=ADMIN_MINISTERIO)
        test_user.groups.add(grupo_admin)
        
        if user_tem_grupo(test_user, ADMIN_MINISTERIO):
            print_success("user_tem_grupo() funciona")
        else:
            print_error("user_tem_grupo() não funciona")
            todos_ok = False
        
        # Testa user_is_admin
        if user_is_admin(test_user):
            print_success("user_is_admin() funciona")
        else:
            print_error("user_is_admin() não funciona")
            todos_ok = False
        
        # Testa user_is_lideranca
        if user_is_lideranca(test_user):
            print_success("user_is_lideranca() funciona")
        else:
            print_error("user_is_lideranca() não funciona")
            todos_ok = False
        
        # Testa escopo ministerial
        if user_escopo_ministerial(test_user):
            print_success("user_escopo_ministerial() funciona")
        else:
            print_error("user_escopo_ministerial() não funciona")
            todos_ok = False
        
        # Limpa
        test_user.groups.clear()
        
    except Exception as e:
        print_error(f"Erro ao testar funções: {e}")
        todos_ok = False
    
    # Remove usuário de teste
    test_user.delete()
    print_info("Usuário de teste removido")
    
    return todos_ok


def test_hierarquia_grupos():
    """Testa se as hierarquias estão corretas."""
    print_header("TESTE 5: Verificando hierarquias")
    
    print_info(f"GRUPOS_ADMIN: {len(GRUPOS_ADMIN)} grupos")
    print_info(f"GRUPOS_LIDERANCA_MINISTERIAL: {len(GRUPOS_LIDERANCA_MINISTERIAL)} grupos")
    print_info(f"GRUPOS_LIDERANCA: {len(GRUPOS_LIDERANCA)} grupos")
    print_info(f"GRUPOS_OPERACIONAL: {len(GRUPOS_OPERACIONAL)} grupos")
    print_info(f"GRUPOS_EQUIPES: {len(GRUPOS_EQUIPES)} grupos")
    print_info(f"GRUPOS_TODOS: {len(GRUPOS_TODOS)} grupos")
    
    todos_ok = True
    
    # Hierarquia deve ser crescente
    if len(GRUPOS_ADMIN) < len(GRUPOS_LIDERANCA_MINISTERIAL) < len(GRUPOS_LIDERANCA) < len(GRUPOS_OPERACIONAL):
        print_success("Hierarquia crescente correta")
    else:
        print_error("Hierarquia não está crescente")
        todos_ok = False
    
    # Total deve ser 13
    if len(GRUPOS_TODOS) == 13:
        print_success("Total de 13 grupos correto")
    else:
        print_warning(f"Total de grupos: {len(GRUPOS_TODOS)} (esperado: 13)")
        todos_ok = False
    
    return todos_ok


def test_imports_no_codigo():
    """Testa se os imports estão corretos nos arquivos."""
    print_header("TESTE 6: Verificando imports no código")
    
    arquivos = [
        'contas/views.py',
        'suporte/views.py',
        'core/views.py',
        'core/decorators.py',
        'financeiro/utils.py',
        'secretaria/views.py',
        'secretaria/utils.py',
        'configuracao/views.py',
        'configuracao/utils.py',
        'comunicacao/utils.py',
    ]
    
    todos_ok = True
    for arquivo in arquivos:
        caminho = os.path.join('c:/Gereigreja', arquivo)
        if os.path.exists(caminho):
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                if 'contas.constants' in conteudo:
                    print_success(f"{arquivo}: import encontrado")
                else:
                    print_warning(f"{arquivo}: import não encontrado (pode ser opcional)")
        else:
            print_error(f"{arquivo}: arquivo não existe")
            todos_ok = False
    
    return todos_ok


def test_permissoes_por_grupo():
    """Lista permissões de cada grupo."""
    print_header("TESTE 7: Resumo de permissões por grupo")
    
    grupos = Group.objects.all().order_by('-permissions__count')
    
    for grupo in grupos:
        count = grupo.permissions.count()
        if count > 0:
            print_info(f"{grupo.name}: {count} permissões")
        else:
            print_warning(f"{grupo.name}: 0 permissões")
    
    return True


def test_usuarios_existentes():
    """Lista usuários e seus grupos."""
    print_header("TESTE 8: Usuários e grupos atuais")
    
    usuarios = User.objects.all().prefetch_related('groups')
    
    if usuarios.count() == 0:
        print_warning("Nenhum usuário encontrado no sistema")
        return True
    
    for user in usuarios[:10]:  # Primeiros 10
        grupos = list(user.groups.values_list('name', flat=True))
        if grupos:
            print_info(f"{user.username}: {', '.join(grupos)}")
        else:
            print_warning(f"{user.username}: sem grupos")
    
    if usuarios.count() > 10:
        print_info(f"... e mais {usuarios.count() - 10} usuários")
    
    return True


# ===================================
# MAIN
# ===================================

def main():
    print(f"\n{Colors.BOLD}{'='*60}")
    print("TESTE AUTOMÁTICO - SISTEMA DE GRUPOS E PERMISSÕES")
    print(f"{'='*60}{Colors.END}\n")
    
    resultados = []
    
    # Executa testes
    resultados.append(("Grupos existem", test_grupos_existem()))
    resultados.append(("Grupos renomeados", test_grupos_renomeados()))
    resultados.append(("Permissões Admin", test_permissoes_admin()))
    resultados.append(("Funções helper", test_funcoes_helper()))
    resultados.append(("Hierarquia", test_hierarquia_grupos()))
    resultados.append(("Imports no código", test_imports_no_codigo()))
    resultados.append(("Permissões por grupo", test_permissoes_por_grupo()))
    resultados.append(("Usuários existentes", test_usuarios_existentes()))
    
    # Resumo final
    print_header("RESUMO FINAL")
    
    total = len(resultados)
    passou = sum(1 for _, ok in resultados if ok)
    falhou = total - passou
    
    for nome, ok in resultados:
        if ok:
            print_success(f"{nome}: PASSOU")
        else:
            print_error(f"{nome}: FALHOU")
    
    print(f"\n{Colors.BOLD}Total: {total} testes{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}Passou: {passou}{Colors.END}")
    
    if falhou > 0:
        print(f"{Colors.RED}{Colors.BOLD}Falhou: {falhou}{Colors.END}")
        print(f"\n{Colors.RED}{Colors.BOLD}❌ IMPLEMENTAÇÃO TEM PROBLEMAS{Colors.END}\n")
        return False
    else:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ IMPLEMENTAÇÃO ESTÁ FUNCIONAL!{Colors.END}\n")
        return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print_error(f"Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
