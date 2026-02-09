"""
Script Python para automatizar deploy
Uso: python deploy.py [versao]
Exemplo: python deploy.py 1.0.10
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Cores para output
class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'

def print_color(message, color):
    print(f"{color}{message}{Colors.NC}")

def executar_comando(comando, erro_msg="Erro ao executar comando"):
    """Executa comando shell e retorna resultado"""
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return True, resultado.stdout
    except subprocess.CalledProcessError as e:
        print_color(f"❌ {erro_msg}", Colors.RED)
        print(e.stderr)
        return False, e.stderr

def verificar_branch():
    """Verifica se está na branch main"""
    sucesso, branch = executar_comando('git branch --show-current')
    if not sucesso or branch.strip() != 'main':
        print_color(f"❌ Erro: Você deve estar na branch 'main'!", Colors.RED)
        print(f"Branch atual: {branch.strip()}")
        return False
    return True

def verificar_mudancas_pendentes():
    """Verifica se há mudanças não commitadas"""
    sucesso, status = executar_comando('git status -s')
    if status.strip():
        print_color("❌ Erro: Existem mudanças não commitadas!", Colors.RED)
        print(status)
        return False
    return True

def criar_backup():
    """Cria backup antes do deploy"""
    print("💾 Criando backup de segurança...")
    sucesso, _ = executar_comando(
        'python skills/backup/scripts/backup.py',
        "Erro ao criar backup"
    )
    return sucesso

def executar_testes():
    """Executa testes do Django"""
    print("🧪 Executando testes...")
    return executar_comando(
        'python manage.py test --settings=core.settings_test',
        "Testes falharam! Deploy cancelado."
    )[0]

def verificar_migracoes():
    """Verifica se há migrações pendentes"""
    print("🔍 Verificando migrações...")
    sucesso, output = executar_comando(
        'python manage.py makemigrations --dry-run --check',
        "Existem migrações pendentes!"
    )
    
    if not sucesso:
        print_color("Execute: python manage.py makemigrations", Colors.YELLOW)
    
    return sucesso

def atualizar_changelog(versao):
    """Adiciona nova versão no CHANGELOG.md"""
    print(f"📝 Atualizando CHANGELOG.md para versão {versao}...")
    
    changelog_path = Path('CHANGELOG.md')
    if not changelog_path.exists():
        print_color("⚠️  CHANGELOG.md não encontrado!", Colors.YELLOW)
        return False
    
    # Ler conteúdo atual
    with open(changelog_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Adicionar nova versão no topo
    data = datetime.now().strftime('%d/%m/%Y')
    nova_entrada = f"""## v{versao} — {data}

### Mudanças
- [Adicione as mudanças aqui]

{conteudo}"""
    
    # Escrever de volta
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(nova_entrada)
    
    # Commit
    executar_comando(f'git add CHANGELOG.md')
    executar_comando(f'git commit -m "Release v{versao}"')
    
    return True

def criar_tag(versao):
    """Cria tag Git para a versão"""
    print(f"🏷️  Criando tag v{versao}...")
    return executar_comando(
        f'git tag -a "v{versao}" -m "Release v{versao}"',
        "Erro ao criar tag"
    )[0]

def push_repositorio():
    """Envia mudanças para o repositório"""
    print("📤 Enviando para repositório...")
    
    # Push dos commits
    sucesso1 = executar_comando('git push origin main', "Erro ao fazer push")[0]
    
    # Push das tags
    sucesso2 = executar_comando('git push --tags', "Erro ao fazer push das tags")[0]
    
    return sucesso1 and sucesso2

def deploy(versao=None):
    """Executa processo completo de deploy"""
    print_color("🚀 Iniciando processo de deploy...", Colors.BLUE)
    
    # Checklist de pré-deploy
    checks = [
        ("Branch main", verificar_branch),
        ("Mudanças commitadas", verificar_mudancas_pendentes),
        ("Backup", criar_backup),
        ("Testes", executar_testes),
        ("Migrações", verificar_migracoes),
    ]
    
    for nome, funcao in checks:
        if not funcao():
            print_color(f"\n❌ Falha no check: {nome}", Colors.RED)
            print_color("Deploy cancelado!", Colors.RED)
            return False
    
    # Atualizar CHANGELOG e criar tag (se versão especificada)
    if versao:
        if not atualizar_changelog(versao):
            return False
        if not criar_tag(versao):
            return False
    
    # Push para repositório
    if not push_repositorio():
        return False
    
    # Sucesso!
    print_color("\n✅ Deploy iniciado com sucesso!", Colors.GREEN)
    print_color("🔄 O Render detectará o push e iniciará o deploy automaticamente.", Colors.BLUE)
    print_color("📊 Acompanhe em: https://dashboard.render.com", Colors.BLUE)
    print("\n⏳ Aguarde alguns minutos para o deploy completar...")
    print("✅ Build → Instalar dependências → Migrações → Collectstatic → Restart")
    print_color("\n🎉 Processo de deploy concluído!", Colors.GREEN)
    
    return True

if __name__ == '__main__':
    versao = sys.argv[1] if len(sys.argv) > 1 else None
    
    if versao:
        print(f"Versão: {versao}")
    
    sucesso = deploy(versao)
    sys.exit(0 if sucesso else 1)
