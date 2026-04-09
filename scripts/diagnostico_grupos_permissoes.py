"""
Script de diagnóstico para analisar todos os grupos e permissões do sistema.
Identifica estrutura de papéis, hierarquia e possíveis problemas.
"""
import os
import django

# Carrega variáveis de ambiente do .env se existir
from pathlib import Path
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)
    print("✅ Variáveis de ambiente carregadas do .env")
else:
    print("⚠️  Arquivo .env não encontrado, usando variáveis do sistema")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from collections import defaultdict

def analisar_grupos_permissoes():
    """Analisa e exibe todos os grupos, permissões e estrutura do sistema."""
    
    print("=" * 80)
    print("ANÁLISE DE GRUPOS E PERMISSÕES DO SISTEMA GEREIGREJA")
    print("=" * 80)
    print()
    
    # 1. LISTAR TODOS OS GRUPOS
    grupos = Group.objects.all().order_by('name')
    print(f"📊 TOTAL DE GRUPOS CADASTRADOS: {grupos.count()}")
    print("-" * 80)
    
    if not grupos.exists():
        print("⚠️  NENHUM GRUPO CADASTRADO NO SISTEMA!")
        print()
    else:
        for grupo in grupos:
            usuarios_count = grupo.user_set.count()
            permissoes_count = grupo.permissions.count()
            
            print(f"\n🏷️  GRUPO: {grupo.name}")
            print(f"   └─ ID: {grupo.id}")
            print(f"   └─ Usuários com este grupo: {usuarios_count}")
            print(f"   └─ Permissões atribuídas: {permissoes_count}")
            
            # Listar usuários deste grupo
            if usuarios_count > 0 and usuarios_count <= 10:
                usuarios = grupo.user_set.all()[:10]
                print(f"   └─ Usuários:")
                for user in usuarios:
                    print(f"      • {user.get_full_name() or user.username} ({user.email})")
            elif usuarios_count > 10:
                print(f"   └─ (Mais de 10 usuários - listagem omitida)")
            
            # Listar permissões deste grupo
            if permissoes_count > 0:
                print(f"   └─ Permissões:")
                permissoes = grupo.permissions.select_related('content_type').all()[:15]
                for perm in permissoes:
                    print(f"      • {perm.content_type.app_label}.{perm.codename}")
                if permissoes_count > 15:
                    print(f"      ... e mais {permissoes_count - 15} permissões")
    
    print()
    print("=" * 80)
    
    # 2. ANÁLISE DE USUÁRIOS POR GRUPO
    print()
    print("👥 DISTRIBUIÇÃO DE USUÁRIOS POR GRUPO")
    print("-" * 80)
    
    usuarios_sem_grupo = User.objects.filter(groups__isnull=True, is_superuser=False).count()
    superusuarios = User.objects.filter(is_superuser=True).count()
    usuarios_totais = User.objects.count()
    
    print(f"Total de usuários: {usuarios_totais}")
    print(f"Superusuários: {superusuarios}")
    print(f"Usuários SEM grupo: {usuarios_sem_grupo}")
    print()
    
    for grupo in grupos:
        count = grupo.user_set.count()
        print(f"{grupo.name:30} → {count:3} usuários")
    
    print()
    print("=" * 80)
    
    # 3. ANÁLISE DE PADRÕES PROFISSIONAIS
    print()
    print("🔍 ANÁLISE DE PADRÕES PROFISSIONAIS (RBAC)")
    print("-" * 80)
    
    # Grupos esperados em um sistema de gestão de igreja
    grupos_esperados = {
        'Admin Ministerio': 'Administrador geral do ministério',
        'Pastor': 'Líder espiritual, acesso amplo',
        'Secretaria': 'Gestão de membros e documentação',
        'Tesouraria': 'Gestão financeira',
        'Líder de Célula': 'Gestão de grupos pequenos',
        'Liderança': 'Líderes diversos',
        'Membro': 'Acesso básico para membros',
    }
    
    grupos_existentes = {g.name for g in grupos}
    
    print("\n✅ Grupos implementados:")
    for nome in grupos_existentes:
        print(f"   • {nome}")
    
    print("\n💡 Grupos sugeridos (não implementados):")
    for nome, descricao in grupos_esperados.items():
        if nome not in grupos_existentes and not any(similar in grupos_existentes for similar in [nome.lower(), nome.replace(' ', '')]):
            print(f"   • {nome} - {descricao}")
    
    print()
    print("=" * 80)
    
    # 4. PROBLEMAS IDENTIFICADOS
    print()
    print("⚠️  PROBLEMAS E RECOMENDAÇÕES")
    print("-" * 80)
    
    problemas = []
    
    # Verifica se há grupos vazios
    grupos_vazios = [g for g in grupos if g.user_set.count() == 0]
    if grupos_vazios:
        problemas.append(
            f"• {len(grupos_vazios)} grupo(s) sem usuários: {', '.join([g.name for g in grupos_vazios])}"
        )
    
    # Verifica se há usuários sem grupo
    if usuarios_sem_grupo > 0:
        problemas.append(
            f"• {usuarios_sem_grupo} usuário(s) sem grupo atribuído (verão página 'Aguardando Permissões')"
        )
    
    # Verifica se há grupos sem permissões
    grupos_sem_permissoes = [g for g in grupos if g.permissions.count() == 0]
    if grupos_sem_permissoes:
        problemas.append(
            f"• {len(grupos_sem_permissoes)} grupo(s) sem permissões: {', '.join([g.name for g in grupos_sem_permissoes])}"
        )
    
    # Verifica se há grupos com nomes similares (possível duplicação)
    nomes_normalizados = defaultdict(list)
    for g in grupos:
        normalizado = g.name.lower().replace(' ', '').replace('_', '').replace('-', '')
        nomes_normalizados[normalizado].append(g.name)
    
    for normalizado, nomes in nomes_normalizados.items():
        if len(nomes) > 1:
            problemas.append(
                f"• Possível duplicação: {', '.join(nomes)}"
            )
    
    # Verifica hierarquia básica
    tem_admin = 'Admin Ministerio' in grupos_existentes or 'Admin' in grupos_existentes
    tem_membro_basico = any(nome in grupos_existentes for nome in ['Membro', 'Membros', 'Usuario', 'Usuário'])
    
    if not tem_admin:
        problemas.append("• Não há grupo de administrador claramente definido")
    
    if not tem_membro_basico:
        problemas.append("• Não há grupo de membro básico (todos os usuários precisam pertencer a um grupo)")
    
    if problemas:
        for problema in problemas:
            print(problema)
    else:
        print("✅ Nenhum problema crítico identificado!")
    
    print()
    print("=" * 80)
    
    # 5. RECOMENDAÇÕES ESPECÍFICAS
    print()
    print("💡 RECOMENDAÇÕES PARA ESTRUTURA PROFISSIONAL")
    print("-" * 80)
    print("""
    Estrutura recomendada para sistema de gestão de igreja:
    
    1. HIERARQUIA DE PERMISSÕES (do maior para o menor):
       ├─ Admin Ministerio (acesso total)
       ├─ Pastor (acesso amplo, pode ver dados sensíveis)
       ├─ Secretaria (gerenciar membros, eventos, relatórios)
       ├─ Tesouraria (gerenciar finanças)
       ├─ Superintendente EBD (gerenciar escola bíblica)
       ├─ Líder de Célula (gerenciar grupo pequeno)
       └─ Membro (acesso básico: ver próprio perfil, eventos)
    
    2. PRINCÍPIOS RBAC (Role-Based Access Control):
       • Separação de responsabilidades (Separation of Duties)
       • Menor privilégio (Least Privilege)
       • Grupos mutuamente exclusivos para funções sensíveis
       • Auditoria de permissões
    
    3. BOAS PRÁTICAS:
       • Todo usuário deve ter pelo menos 1 grupo
       • Grupos devem ter permissões claras e documentadas
       • Evitar grupos com "todas as permissões" (exceto Admin)
       • Usar hierarquia: Admin > Líder > Membro
       • Revisar permissões trimestralmente
    
    4. PERMISSÕES POR MÓDULO:
       • Secretaria: view/add/change/delete pessoa, membro, cargo
       • Financeiro: view/add/change/delete transações (somente Tesouraria)
       • EBD: view/add/change/delete classes, alunos (Superintendente)
       • Eventos: view para todos, add/change para líderes
    """)
    
    print()
    print("=" * 80)
    
    # 6. VERIFICAÇÃO DE CÓDIGO
    print()
    print("🔎 VERIFICAÇÃO DE USO NO CÓDIGO")
    print("-" * 80)
    
    # Lista grupos mencionados no código mas não cadastrados
    grupos_no_codigo = [
        'Admin Ministerio',
        'Superintendentes', 
        'Secretaria EBD',
        'Tesouraria Ministerial',
        'Tesoureiro',
        'Lider Igreja',
        'Gestor',
        'Pastor',
    ]
    
    print("\nGrupos referenciados no código:")
    for grupo_nome in grupos_no_codigo:
        existe = grupo_nome in grupos_existentes
        status = "✅" if existe else "❌"
        print(f"   {status} {grupo_nome}")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    analisar_grupos_permissoes()
