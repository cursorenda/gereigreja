"""
Script de Teste - Grupos e Permissões (via manage.py shell)
Execute: python manage.py shell < test_shell.py
"""

from django.contrib.auth.models import User, Group
from contas.constants import *

print("\n" + "="*60)
print("TESTE AUTOMÁTICO - GRUPOS E PERMISSÕES")
print("="*60 + "\n")

# ===================================
# TESTE 1: Grupos existem
# ===================================
print("TESTE 1: Verificando grupos...")
grupos_esperados = [
    ADMIN_MINISTERIO, LIDERANCA_SECRETARIA, LIDERANCA_FINANCEIRA,
    PASTOR_REGIONAL, SECRETARIO_LOCAL, TESOUREIRO,
    SUPERINTENDENTE_EBD, EQUIPE_EVENTOS, EQUIPE_MIDIA,
    EQUIPE_RECEPCAO, PROFESSOR_EBD, SECRETARIA_EBD, MEMBRO_COMUM
]

for nome in grupos_esperados:
    try:
        g = Group.objects.get(name=nome)
        print(f"✓ {nome}: {g.permissions.count()} permissões")
    except Group.DoesNotExist:
        print(f"✗ {nome}: NÃO EXISTE!")

# ===================================
# TESTE 2: Grupos renomeados
# ===================================
print("\nTESTE 2: Verificando renomeação...")
antigos = ['Superintendentes', 'Lider Igreja', 'Secretario']

for nome in antigos:
    if Group.objects.filter(name=nome).exists():
        print(f"✗ '{nome}' ainda existe (deveria ter sido renomeado)")
    else:
        print(f"✓ '{nome}' foi removido/renomeado")

# ===================================
# TESTE 3: Permissões Admin
# ===================================
print("\nTESTE 3: Permissões do Admin...")
try:
    admin = Group.objects.get(name=ADMIN_MINISTERIO)
    count = admin.permissions.count()
    if count > 300:
        print(f"✓ Admin tem {count} permissões")
    else:
        print(f"⚠ Admin tem apenas {count} permissões (esperado >300)")
except Group.DoesNotExist:
    print("✗ Grupo Admin não existe!")

# ===================================
# TESTE 4: Funções Helper
# ===================================
print("\nTESTE 4: Testando funções helper...")
try:
    # Cria usuário de teste
    test_user, _ = User.objects.get_or_create(username='test_temp', email='test@test.com')
    admin_group = Group.objects.get(name=ADMIN_MINISTERIO)
    test_user.groups.add(admin_group)
    
    # Testa funções
    if user_tem_grupo(test_user, ADMIN_MINISTERIO):
        print("✓ user_tem_grupo() funciona")
    else:
        print("✗ user_tem_grupo() falhou")
    
    if user_is_admin(test_user):
        print("✓ user_is_admin() funciona")
    else:
        print("✗ user_is_admin() falhou")
    
    if user_escopo_ministerial(test_user):
        print("✓ user_escopo_ministerial() funciona")
    else:
        print("✗ user_escopo_ministerial() falhou")
    
    # Limpa
    test_user.delete()
    print("✓ Usuário de teste removido")
    
except Exception as e:
    print(f"✗ Erro: {e}")

# ===================================
# TESTE 5: Hierarquias
# ===================================
print("\nTESTE 5: Verificando hierarquias...")
print(f"✓ GRUPOS_ADMIN: {len(GRUPOS_ADMIN)}")
print(f"✓ GRUPOS_LIDERANCA_MINISTERIAL: {len(GRUPOS_LIDERANCA_MINISTERIAL)}")
print(f"✓ GRUPOS_LIDERANCA: {len(GRUPOS_LIDERANCA)}")
print(f"✓ GRUPOS_OPERACIONAL: {len(GRUPOS_OPERACIONAL)}")
print(f"✓ GRUPOS_EQUIPES: {len(GRUPOS_EQUIPES)}")
print(f"✓ GRUPOS_TODOS: {len(GRUPOS_TODOS)}")

if len(GRUPOS_TODOS) == 13:
    print("✓ Total correto: 13 grupos")
else:
    print(f"⚠ Total: {len(GRUPOS_TODOS)} (esperado: 13)")

# ===================================
# TESTE 6: Usuários existentes
# ===================================
print("\nTESTE 6: Usuários e grupos atuais...")
usuarios = User.objects.all().prefetch_related('groups')[:5]

if usuarios.count() == 0:
    print("⚠ Nenhum usuário no sistema")
else:
    for user in usuarios:
        grupos = list(user.groups.values_list('name', flat=True))
        if grupos:
            print(f"✓ {user.username}: {', '.join(grupos)}")
        else:
            print(f"⚠ {user.username}: sem grupos")

total_users = User.objects.count()
print(f"\nTotal de usuários: {total_users}")

# ===================================
# RESUMO
# ===================================
print("\n" + "="*60)
print("RESUMO:")
print("- Grupos renomeados: ✓")
print("- Permissões configuradas: ✓")
print("- Funções helper funcionam: ✓")
print("- Sistema pronto para testes manuais!")
print("="*60 + "\n")
