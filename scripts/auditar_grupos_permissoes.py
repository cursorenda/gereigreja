"""
Script de auditoria completa de grupos e permissões.
Mostra estado atual do sistema para análise e reestruturação.
"""
import os
import django
from pathlib import Path

# Carrega variáveis de ambiente
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import Group, Permission, User
from django.db.models import Count
from collections import defaultdict

def auditar_grupos():
    print("=" * 100)
    print("AUDITORIA COMPLETA DE GRUPOS E PERMISSÕES - GEREIGREJA")
    print("=" * 100)
    print()
    
    # 1. ESTATÍSTICAS GERAIS
    total_usuarios = User.objects.count()
    usuarios_ativos = User.objects.filter(is_active=True).count()
    superusuarios = User.objects.filter(is_superuser=True).count()
    usuarios_sem_grupo = User.objects.filter(groups__isnull=True, is_superuser=False).count()
    
    print("📊 ESTATÍSTICAS GERAIS")
    print("-" * 100)
    print(f"Total de usuários: {total_usuarios}")
    print(f"Usuários ativos: {usuarios_ativos}")
    print(f"Superusuários: {superusuarios}")
    print(f"Usuários sem grupo: {usuarios_sem_grupo}")
    if usuarios_sem_grupo > 0:
        print(f"   ⚠️  ATENÇÃO: {usuarios_sem_grupo} usuários verão página 'Aguardando Permissões'")
    print()
    
    # 2. ANÁLISE DETALHADA POR GRUPO
    print("=" * 100)
    print("📋 ANÁLISE DETALHADA DOS GRUPOS")
    print("=" * 100)
    print()
    
    grupos = Group.objects.annotate(
        num_usuarios=Count('user', distinct=True),
        num_permissoes=Count('permissions', distinct=True)
    ).order_by('name')
    
    for grupo in grupos:
        print(f"🏷️  {grupo.name}")
        print(f"   ID: {grupo.id}")
        print(f"   Usuários: {grupo.num_usuarios}")
        print(f"   Permissões: {grupo.num_permissoes}")
        
        # Lista usuários (se não forem muitos)
        if grupo.num_usuarios > 0 and grupo.num_usuarios <= 10:
            print(f"   └─ Usuários:")
            for user in grupo.user_set.all().order_by('email'):
                nome = user.get_full_name() or user.username
                print(f"      • {nome} ({user.email})")
        elif grupo.num_usuarios > 10:
            print(f"   └─ Usuários: (mais de 10, listagem omitida)")
        
        # Mostra permissões (primeiras 10)
        if grupo.num_permissoes > 0:
            print(f"   └─ Permissões:")
            perms = grupo.permissions.select_related('content_type').all()[:10]
            for perm in perms:
                print(f"      • {perm.content_type.app_label}.{perm.codename}")
            if grupo.num_permissoes > 10:
                print(f"      ... e mais {grupo.num_permissoes - 10} permissões")
        else:
            print(f"   └─ ⚠️  SEM PERMISSÕES ATRIBUÍDAS")
        
        print()
    
    # 3. GRUPOS PROBLEMÁTICOS
    print("=" * 100)
    print("⚠️  GRUPOS PROBLEMÁTICOS")
    print("=" * 100)
    print()
    
    problemas = []
    
    # Grupos sem usuários
    grupos_vazios = [g for g in grupos if g.num_usuarios == 0]
    if grupos_vazios:
        print(f"❌ Grupos SEM usuários ({len(grupos_vazios)}):")
        for g in grupos_vazios:
            print(f"   • {g.name} (pode ser removido ou está aguardando uso)")
        problemas.append(f"{len(grupos_vazios)} grupos vazios")
        print()
    
    # Grupos sem permissões
    grupos_sem_perm = [g for g in grupos if g.num_permissoes == 0]
    if grupos_sem_perm:
        print(f"⚠️  Grupos SEM permissões ({len(grupos_sem_perm)}):")
        for g in grupos_sem_perm:
            usuarios_count = g.num_usuarios
            print(f"   • {g.name} ({usuarios_count} usuários NÃO TÊM ACESSO A NADA)")
        problemas.append(f"{len(grupos_sem_perm)} grupos sem permissões")
        print()
    
    # Grupos com muitos usuários mas sem permissões
    grupos_criticos = [g for g in grupos if g.num_usuarios > 0 and g.num_permissoes == 0]
    if grupos_criticos:
        print(f"🚨 CRÍTICO: Grupos COM usuários mas SEM permissões:")
        for g in grupos_criticos:
            print(f"   • {g.name}: {g.num_usuarios} usuários sem acesso")
        print()
    
    # 4. DISTRIBUIÇÃO DE USUÁRIOS
    print("=" * 100)
    print("👥 DISTRIBUIÇÃO DE USUÁRIOS POR GRUPO")
    print("=" * 100)
    print()
    
    grupos_ordenados = sorted(grupos, key=lambda g: g.num_usuarios, reverse=True)
    
    print(f"{'Grupo':<30} {'Usuários':>10} {'Permissões':>12}")
    print("-" * 100)
    for grupo in grupos_ordenados:
        print(f"{grupo.name:<30} {grupo.num_usuarios:>10} {grupo.num_permissoes:>12}")
    
    print()
    
    # 5. USUÁRIOS COM MÚLTIPLOS GRUPOS
    print("=" * 100)
    print("🔀 USUÁRIOS COM MÚLTIPLOS GRUPOS")
    print("=" * 100)
    print()
    
    usuarios_multiplos = User.objects.annotate(
        num_grupos=Count('groups')
    ).filter(num_grupos__gt=1, is_superuser=False).order_by('-num_grupos')
    
    if usuarios_multiplos.exists():
        print(f"Total: {usuarios_multiplos.count()} usuários com mais de 1 grupo")
        print()
        for user in usuarios_multiplos[:20]:  # Mostra até 20
            grupos_usuario = ", ".join([g.name for g in user.groups.all()])
            nome = user.get_full_name() or user.username
            print(f"   • {nome} ({user.email})")
            print(f"     └─ {user.groups.count()} grupos: {grupos_usuario}")
        if usuarios_multiplos.count() > 20:
            print(f"   ... e mais {usuarios_multiplos.count() - 20} usuários")
    else:
        print("✅ Nenhum usuário com múltiplos grupos (estrutura simples)")
    
    print()
    
    # 6. RESUMO FINAL
    print("=" * 100)
    print("📝 RESUMO E RECOMENDAÇÕES")
    print("=" * 100)
    print()
    
    if problemas:
        print("Problemas identificados:")
        for problema in problemas:
            print(f"   • {problema}")
        print()
    
    # Recomendações específicas
    print("Recomendações:")
    
    if usuarios_sem_grupo > 0:
        print(f"   🔴 CRÍTICO: Atribuir grupo a {usuarios_sem_grupo} usuários sem grupo")
    
    if grupos_sem_perm:
        print(f"   🔴 CRÍTICO: Configurar permissões para {len(grupos_sem_perm)} grupos")
    
    if grupos_vazios:
        print(f"   🟡 ATENÇÃO: Revisar {len(grupos_vazios)} grupos sem usuários")
    
    # Nomenclatura
    nomes_plurais = [g.name for g in grupos if g.name.endswith('s') or 'Equipe de' in g.name]
    if nomes_plurais:
        print(f"   🟡 PADRONIZAÇÃO: Revisar nomenclatura (plural vs singular)")
    
    print()
    print("=" * 100)

if __name__ == '__main__':
    try:
        auditar_grupos()
    except Exception as e:
        print(f"❌ Erro ao executar auditoria: {e}")
        import traceback
        traceback.print_exc()
