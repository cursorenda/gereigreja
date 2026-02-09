"""
Script para gerar release notes automaticamente
Analisa commits desde última versão e gera texto amigável
Uso: python generate_release_notes.py v1.0.9
"""

import sys
import subprocess
from datetime import datetime

def executar_git(comando):
    """Executa comando git e retorna output"""
    resultado = subprocess.run(
        f'git {comando}',
        shell=True,
        capture_output=True,
        text=True
    )
    return resultado.stdout.strip()

def obter_commits_desde_tag(tag):
    """Obtém lista de commits desde a última tag"""
    comando = f'log {tag}..HEAD --oneline'
    commits = executar_git(comando)
    
    if not commits:
        return []
    
    return [linha for linha in commits.split('\n') if linha]

def categorizar_commits(commits):
    """Categoriza commits por tipo"""
    categorias = {
        'features': [],
        'fixes': [],
        'improvements': [],
        'docs': [],
        'tests': [],
        'other': []
    }
    
    for commit in commits:
        commit_lower = commit.lower()
        
        if any(palavra in commit_lower for palavra in ['feat', 'feature', 'add', 'novo', 'nova']):
            categorias['features'].append(commit)
        elif any(palavra in commit_lower for palavra in ['fix', 'bug', 'corrige', 'corrigido']):
            categorias['fixes'].append(commit)
        elif any(palavra in commit_lower for palavra in ['improve', 'melhora', 'otimiza', 'refactor']):
            categorias['improvements'].append(commit)
        elif any(palavra in commit_lower for palavra in ['doc', 'readme']):
            categorias['docs'].append(commit)
        elif 'test' in commit_lower:
            categorias['tests'].append(commit)
        else:
            categorias['other'].append(commit)
    
    return categorias

def gerar_release_notes(versao_anterior, nova_versao):
    """Gera release notes completas"""
    print(f"📝 Gerando release notes de {versao_anterior} para {nova_versao}...")
    
    # Obter commits
    commits = obter_commits_desde_tag(versao_anterior)
    
    if not commits:
        print("⚠️  Nenhum commit encontrado desde última versão!")
        return None
    
    # Categorizar
    categorias = categorizar_commits(commits)
    
    # Data atual
    data = datetime.now().strftime('%d/%m/%Y')
    
    # Gerar texto
    texto = f"""# 🎉 Versão {nova_versao} - {data}

## O que há de novo?

"""
    
    # Features
    if categorias['features']:
        texto += "### 🚀 Novas Funcionalidades\n\n"
        for commit in categorias['features']:
            # Remover hash do commit
            msg = ' '.join(commit.split()[1:])
            texto += f"- ✨ {msg}\n"
        texto += "\n"
    
    # Fixes
    if categorias['fixes']:
        texto += "### 🐛 Correções\n\n"
        for commit in categorias['fixes']:
            msg = ' '.join(commit.split()[1:])
            texto += f"- ✅ {msg}\n"
        texto += "\n"
    
    # Improvements
    if categorias['improvements']:
        texto += "### 📈 Melhorias\n\n"
        for commit in categorias['improvements']:
            msg = ' '.join(commit.split()[1:])
            texto += f"- 🔧 {msg}\n"
        texto += "\n"
    
    # Outros
    if categorias['other']:
        texto += "### 📋 Outras Mudanças\n\n"
        for commit in categorias['other']:
            msg = ' '.join(commit.split()[1:])
            texto += f"- {msg}\n"
        texto += "\n"
    
    # Rodapé
    texto += f"""---

**Versão**: {nova_versao} | **Data**: {data}
**Total de commits**: {len(commits)}
"""
    
    return texto

def salvar_release_notes(versao, texto):
    """Salva release notes em arquivo"""
    filename = f"RELEASE_NOTES_{versao}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(texto)
    
    print(f"✅ Release notes salvas em: {filename}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python generate_release_notes.py <versao_anterior>")
        print("Exemplo: python generate_release_notes.py v1.0.9")
        sys.exit(1)
    
    versao_anterior = sys.argv[1]
    
    # Obter versão atual (próxima)
    import re
    match = re.search(r'v?(\d+)\.(\d+)\.(\d+)', versao_anterior)
    if match:
        major, minor, patch = map(int, match.groups())
        nova_versao = f"v{major}.{minor}.{patch + 1}"
    else:
        nova_versao = input("Digite a nova versão (ex: v1.0.10): ")
    
    # Gerar
    texto = gerar_release_notes(versao_anterior, nova_versao)
    
    if texto:
        print("\n" + "="*60)
        print(texto)
        print("="*60 + "\n")
        
        salvar = input("Salvar release notes? (s/n): ")
        if salvar.lower() == 's':
            salvar_release_notes(nova_versao.replace('v', 'v'), texto)
