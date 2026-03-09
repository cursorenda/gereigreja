import subprocess
import os
from datetime import datetime
from django.conf import settings
from .models import DeployHistorico


def obter_mudancas_git():
    """Detecta automaticamente as mudanças via git diff"""
    try:
        # Git status para ver arquivos modificados
        result = subprocess.run(
            ['git', 'status', '--short'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR
        )
        
        if result.returncode == 0:
            arquivos = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            modificados = []
            adicionados = []
            deletados = []
            
            for linha in arquivos:
                if linha:
                    status = linha[:2].strip()
                    arquivo = linha[3:].strip()
                    
                    if status == 'M':
                        modificados.append(arquivo)
                    elif status in ['A', '??']:
                        adicionados.append(arquivo)
                    elif status == 'D':
                        deletados.append(arquivo)
            
            return {
                'sucesso': True,
                'modificados': modificados,
                'adicionados': adicionados,
                'deletados': deletados,
                'total': len(modificados) + len(adicionados) + len(deletados)
            }
        else:
            return {
                'sucesso': False,
                'erro': 'Erro ao executar git status'
            }
    
    except Exception as e:
        return {
            'sucesso': False,
            'erro': str(e)
        }


def obter_commits_desde_ultimo_deploy():
    """
    Obtém mudanças LOCAIS que ainda não foram enviadas ao servidor.
    Mostra commits feitos localmente mas que ainda não foram para o remote (origin).
    """
    # DEBUG: Logar diretório corrente, branch e resultado do git log
    import logging
    logger = logging.getLogger('deploy_debug')
    logger.warning('DEBUG deploy: cwd=%s', settings.BASE_DIR)
    branch_result_dbg = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        capture_output=True,
        text=True,
        cwd=settings.BASE_DIR,
        encoding='utf-8'
    )
    logger.warning('DEBUG deploy: branch local=%s', branch_result_dbg.stdout.strip())
    log_result_dbg = subprocess.run(
        ['git', 'log', 'origin/master..HEAD', '--oneline'],
        capture_output=True,
        text=True,
        cwd=settings.BASE_DIR,
        encoding='utf-8'
    )
    logger.warning('DEBUG deploy: git log origin/master..HEAD --oneline = %s', log_result_dbg.stdout.strip())
    try:
        from .models import DeployHistorico
        
        # Palavras-chave para filtrar commits automáticos/irrelevantes
        filtros = [
            'release v',
            'deploy v',
            'merge branch',
            'merge pull request',
            'auto-generated',
            'automated',
        ]
        
        # 0. Atualizar referência do remote para garantir precisão
        subprocess.run(
            ['git', 'fetch'],
            capture_output=True,
            cwd=settings.BASE_DIR,
            encoding='utf-8'
        )

        # 1. Verificar se há mudanças não commitadas (unstaged/staged)
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            encoding='utf-8'
        )
        
        mudancas_nao_commitadas = []
        if status_result.returncode == 0 and status_result.stdout.strip():
            linhas = status_result.stdout.strip().split('\n')
            for linha in linhas[:10]:  # Limitar a 10 arquivos
                # Formato: "M arquivo.py" ou "?? novo.py"
                if linha.strip():
                    mudancas_nao_commitadas.append(f"- [Não commitado] {linha.strip()}")
        
        # 2. Buscar commits locais realmente pendentes (git log origin/master..HEAD)
        commits_pendentes = []
        result = subprocess.run(
            ['git', 'log', 'origin/master..HEAD', '--pretty=format:%s'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            encoding='utf-8'
        )
        if result.returncode == 0 and result.stdout.strip():
            commits = result.stdout.strip().split('\n')
            for commit in commits:
                commit = commit.strip()
                if commit and not any(filtro.lower() in commit.lower() for filtro in filtros):
                    commits_pendentes.append(f"- {commit}")

        # Combinar mudanças não commitadas + commits pendentes
        resultado = []
        if mudancas_nao_commitadas:
            resultado.append("Arquivos alterados neste deploy:")
            resultado.extend(mudancas_nao_commitadas)
            resultado.append("")
        if commits_pendentes:
            resultado.append("# 📝 Commits locais que serão enviados:")
            resultado.extend(commits_pendentes)
        if resultado:
            return '\n'.join(resultado)
        else:
            return ""
    
    except Exception as e:
        return f"- (Erro ao obter commits: {str(e)})"


def obter_versao_atual():
    """Lê a versão atual do CHANGELOG.md"""
    try:
        changelog_path = os.path.join(settings.BASE_DIR, 'CHANGELOG.md')
        with open(changelog_path, 'r', encoding='utf-8') as f:
            for linha in f:
                if linha.startswith('## v'):
                    # Extrai a versão (ex: "## v1.0.9" -> "1.0.9")
                    versao = linha.split('—')[0].replace('## v', '').strip()
                    return versao
        return '1.0.0'
    except:
        return '1.0.0'


def incrementar_versao(versao_atual, tipo):
    """Incrementa a versão baseado no tipo (patch, minor, major)"""
    try:
        partes = versao_atual.split('.')
        major, minor, patch = int(partes[0]), int(partes[1]), int(partes[2])
        
        if tipo == 'major':
            return f"{major + 1}.0.0"
        elif tipo == 'minor':
            return f"{major}.{minor + 1}.0"
        else:  # patch
            return f"{major}.{minor}.{patch + 1}"
    except:
        return '1.0.1'


def verificar_migrations_pendentes():
    """
    Verifica se há models alterados sem migration ou migrations não aplicadas.
    Retorna dict com status da validação.
    """
    try:
        # 1. Verificar se há models alterados sem migration (makemigrations --check)
        resultado_check = subprocess.run(
            ['python', 'manage.py', 'makemigrations', '--check', '--dry-run'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            timeout=30
        )
        
        # Se returncode != 0, há mudanças nos models sem migration
        if resultado_check.returncode != 0:
            return {
                'ok': False,
                'tipo': 'erro',
                'mensagem': '❌ Existem alterações nos models sem migration correspondente',
                'detalhes': 'Execute: python manage.py makemigrations'
            }
        
        # 2. Verificar se há migrations não aplicadas (showmigrations --plan)
        resultado_plan = subprocess.run(
            ['python', 'manage.py', 'showmigrations', '--plan'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            timeout=30
        )
        
        if resultado_plan.returncode == 0:
            linhas = resultado_plan.stdout.strip().split('\n')
            migrations_pendentes = [l for l in linhas if l.strip().startswith('[ ]')]
            
            if migrations_pendentes:
                lista = '\n'.join(migrations_pendentes[:5])  # Mostrar até 5
                return {
                    'ok': False,
                    'tipo': 'aviso',
                    'mensagem': f'⚠️ Há {len(migrations_pendentes)} migration(s) não aplicada(s) no banco',
                    'detalhes': f'Será aplicado automaticamente durante o deploy:\n{lista}'
                }
        
        return {
            'ok': True,
            'tipo': 'sucesso',
            'mensagem': '✅ Migrations: Tudo sincronizado',
            'detalhes': ''
        }
        
    except subprocess.TimeoutExpired:
        return {
            'ok': False,
            'tipo': 'erro',
            'mensagem': '❌ Timeout ao verificar migrations',
            'detalhes': 'Processo demorou mais de 30 segundos'
        }
    except Exception as e:
        return {
            'ok': False,
            'tipo': 'erro',
            'mensagem': '❌ Erro ao verificar migrations',
            'detalhes': str(e)
        }


def verificar_branch_correta():
    """
    Verifica se está na branch master/main.
    Deploy só deve ser feito na branch principal.
    """
    try:
        resultado = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            timeout=5
        )
        
        if resultado.returncode == 0:
            branch_atual = resultado.stdout.strip()
            
            if branch_atual not in ['master', 'main']:
                return {
                    'ok': False,
                    'tipo': 'erro',
                    'mensagem': f'❌ Branch incorreta: {branch_atual}',
                    'detalhes': 'Deploy deve ser feito na branch master ou main'
                }
            
            return {
                'ok': True,
                'tipo': 'sucesso',
                'mensagem': f'✅ Branch: {branch_atual}',
                'detalhes': ''
            }
        else:
            return {
                'ok': False,
                'tipo': 'erro',
                'mensagem': '❌ Não foi possível identificar a branch',
                'detalhes': resultado.stderr
            }
            
    except Exception as e:
        return {
            'ok': False,
            'tipo': 'erro',
            'mensagem': '❌ Erro ao verificar branch',
            'detalhes': str(e)
        }


def verificar_sincronizacao_remote():
    """
    Verifica se o repositório local está sincronizado com o remote.
    Avisa sobre commits remotos não puxados ou locais não enviados.
    """
    try:
        # Atualizar referências do remote
        subprocess.run(
            ['git', 'fetch'],
            capture_output=True,
            cwd=settings.BASE_DIR,
            timeout=30
        )
        
        avisos = []
        
        # 1. Verificar commits remotos não puxados (HEAD..origin/master)
        resultado_behind = subprocess.run(
            ['git', 'log', 'HEAD..origin/master', '--oneline'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            timeout=10
        )
        
        if resultado_behind.returncode == 0 and resultado_behind.stdout.strip():
            commits_remotos = len(resultado_behind.stdout.strip().split('\n'))
            avisos.append(f'• {commits_remotos} commit(s) remoto(s) não puxado(s)')
        
        # 2. Verificar commits locais não enviados (origin/master..HEAD)
        resultado_ahead = subprocess.run(
            ['git', 'log', 'origin/master..HEAD', '--oneline'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            timeout=10
        )
        
        if resultado_ahead.returncode == 0 and resultado_ahead.stdout.strip():
            commits_locais = len(resultado_ahead.stdout.strip().split('\n'))
            avisos.append(f'• {commits_locais} commit(s) local(is) será(ão) enviado(s)')
        
        if avisos:
            return {
                'ok': True,
                'tipo': 'aviso',
                'mensagem': '⚠️ Sincronização com remote',
                'detalhes': '\n'.join(avisos)
            }
        else:
            return {
                'ok': True,
                'tipo': 'sucesso',
                'mensagem': '✅ Sincronizado com origin/master',
                'detalhes': ''
            }
            
    except Exception as e:
        return {
            'ok': True,
            'tipo': 'aviso',
            'mensagem': '⚠️ Não foi possível verificar sincronização',
            'detalhes': str(e)
        }


def executar_testes():
    """
    Executa a suite de testes do Django.
    Retorna aviso se falhar, mas não bloqueia o deploy.
    """
    try:
        resultado = subprocess.run(
            ['python', 'manage.py', 'test', '--failfast', '--no-input'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            timeout=300  # 5 minutos
        )
        
        if resultado.returncode == 0:
            # Extrair número de testes executados
            output = resultado.stderr  # Django test output vai para stderr
            if 'Ran' in output:
                linha_testes = [l for l in output.split('\n') if 'Ran' in l]
                if linha_testes:
                    return {
                        'ok': True,
                        'tipo': 'sucesso',
                        'mensagem': '✅ Testes: ' + linha_testes[0].strip(),
                        'detalhes': ''
                    }
            
            return {
                'ok': True,
                'tipo': 'sucesso',
                'mensagem': '✅ Testes executados com sucesso',
                'detalhes': ''
            }
        else:
            return {
                'ok': True,
                'tipo': 'aviso',
                'mensagem': '⚠️ Alguns testes falharam',
                'detalhes': 'Deploy pode continuar, mas revise os testes'
            }
            
    except subprocess.TimeoutExpired:
        return {
            'ok': True,
            'tipo': 'aviso',
            'mensagem': '⚠️ Testes demoraram mais de 5 minutos',
            'detalhes': 'Execução de testes cancelada por timeout'
        }
    except Exception as e:
        return {
            'ok': True,
            'tipo': 'aviso',
            'mensagem': '⚠️ Não foi possível executar testes',
            'detalhes': str(e)
        }


def obter_estatisticas_codigo():
    """
    Obtém estatísticas do código alterado usando git diff --stat.
    Retorna número de arquivos, linhas inseridas e deletadas.
    """
    try:
        resultado = subprocess.run(
            ['git', 'diff', '--stat', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            timeout=10
        )
        
        if resultado.returncode == 0 and resultado.stdout.strip():
            output = resultado.stdout.strip()
            linhas = output.split('\n')
            
            # Última linha geralmente tem o resumo: "X files changed, Y insertions(+), Z deletions(-)"
            if linhas:
                ultima_linha = linhas[-1]
                
                arquivos = 0
                insercoes = 0
                delecoes = 0
                
                # Parsear a linha de resumo
                if 'file' in ultima_linha:
                    partes = ultima_linha.split(',')
                    for parte in partes:
                        if 'file' in parte:
                            arquivos = int(''.join(filter(str.isdigit, parte)))
                        elif 'insertion' in parte:
                            insercoes = int(''.join(filter(str.isdigit, parte)))
                        elif 'deletion' in parte:
                            delecoes = int(''.join(filter(str.isdigit, parte)))
                
                return {
                    'arquivos': arquivos,
                    'insercoes': insercoes,
                    'delecoes': delecoes,
                    'saldo': insercoes - delecoes
                }
        
        # Se não há mudanças
        return {
            'arquivos': 0,
            'insercoes': 0,
            'delecoes': 0,
            'saldo': 0
        }
        
    except Exception as e:
        return {
            'arquivos': 0,
            'insercoes': 0,
            'delecoes': 0,
            'saldo': 0
        }


def criar_release_notes(versao, tipo_versao, descricao, mudancas_git, estatisticas):
    """
    Cria arquivo RELEASE_NOTES_vX.X.X.md automaticamente.
    Gera documentação completa do release com estatísticas e arquivos modificados.
    """
    from datetime import datetime
    
    # Obter commit hash atual
    try:
        result_hash = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            timeout=5
        )
        commit_hash = result_hash.stdout.strip()[:7] if result_hash.returncode == 0 else 'unknown'
    except:
        commit_hash = 'unknown'
    
    # Obter versão anterior
    versao_anterior = obter_versao_atual()
    
    # Mapear tipo de versão para texto descritivo
    tipo_map = {
        'patch': 'PATCH (Correções)',
        'minor': 'MINOR (Funcionalidades)',
        'major': 'MAJOR (Breaking Changes)'
    }
    tipo_texto = tipo_map.get(tipo_versao, tipo_versao.upper())
    
    # Gerar template
    template = f"""# Release Notes - Versão {versao}

**Data de Lançamento:** {datetime.now().strftime('%d/%m/%Y')}  
**Tipo:** {tipo_texto}

---

## 📝 Descrição

{descricao}

---

## 📊 Estatísticas

- **Arquivos Modificados:** {estatisticas['arquivos']}
- **Linhas Adicionadas:** +{estatisticas['insercoes']}
- **Linhas Removidas:** -{estatisticas['delecoes']}
- **Saldo:** {estatisticas['saldo']:+d}

---

## 🔄 Arquivos Alterados
"""
    
    # Adicionar arquivos modificados
    if mudancas_git['sucesso'] and mudancas_git['modificados']:
        template += f"\n### 📝 Modificados ({len(mudancas_git['modificados'])})\n"
        for arquivo in mudancas_git['modificados']:
            template += f"- `{arquivo}`\n"
    
    # Adicionar arquivos adicionados
    if mudancas_git['sucesso'] and mudancas_git['adicionados']:
        template += f"\n### ➕ Adicionados ({len(mudancas_git['adicionados'])})\n"
        for arquivo in mudancas_git['adicionados']:
            template += f"- `{arquivo}`\n"
    
    # Adicionar arquivos deletados
    if mudancas_git['sucesso'] and mudancas_git['deletados']:
        template += f"\n### 🗑️ Removidos ({len(mudancas_git['deletados'])})\n"
        for arquivo in mudancas_git['deletados']:
            template += f"- `{arquivo}`\n"
    
    # Instruções de atualização
    template += f"""

---

## 🚀 Como Atualizar

### Desenvolvimento Local
```bash
git pull origin master
python manage.py migrate
python manage.py collectstatic --noinput
```

### Produção (Render - Automático)
O deploy será acionado automaticamente após o push. Monitorar:
1. ✅ Build logs no dashboard do Render
2. ✅ Execução de migrations
3. ✅ Collectstatic
4. ✅ Reinício do servidor

---

## ⚠️ Breaking Changes

{f'✅ Nenhuma mudança incompatível com versões anteriores.' if tipo_versao != 'major' else '❌ ATENÇÃO: Esta é uma versão MAJOR. Verifique compatibilidade antes de atualizar!'}

---

## 🔗 Informações Técnicas

- **Commit Hash:** `{commit_hash}`
- **Tag Git:** `v{versao}`
- **Versão Anterior:** v{versao_anterior}

---

**📚 Documentação Completa:** [README.md](README.md)  
**📋 Changelog:** [CHANGELOG.md](CHANGELOG.md)
"""
    
    # Salvar arquivo
    filename = f"RELEASE_NOTES_v{versao}.md"
    filepath = os.path.join(settings.BASE_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        return {
            'sucesso': True,
            'arquivo': filename,
            'caminho': filepath
        }
    except Exception as e:
        return {
            'sucesso': False,
            'erro': str(e)
        }


def fazer_backup_pre_deploy(versao):
    """
    Faz backup automático do banco de dados antes do deploy.
    Usa Django dumpdata para criar backup em JSON.
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_pre_deploy_v{versao}_{timestamp}.json"
    backup_path = os.path.join(settings.BASE_DIR, 'backups', backup_filename)
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    
    try:
        # Fazer backup usando dumpdata (todos os dados exceto sessões e logs temporários)
        with open(backup_path, 'w', encoding='utf-8') as f:
            subprocess.run([
                'python', 'manage.py', 'dumpdata',
                '--natural-foreign',
                '--natural-primary',
                '--exclude=contenttypes',
                '--exclude=auth.permission',
                '--exclude=sessions.session',
                '--indent=2'
            ], stdout=f, cwd=settings.BASE_DIR, check=True, timeout=300)
        
        # Obter tamanho do arquivo
        tamanho = os.path.getsize(backup_path)
        tamanho_mb = tamanho / (1024 * 1024)
        
        return {
            'sucesso': True,
            'arquivo': backup_filename,
            'caminho': backup_path,
            'tamanho': tamanho,
            'tamanho_mb': f"{tamanho_mb:.2f} MB"
        }
    except subprocess.TimeoutExpired:
        return {
            'sucesso': False,
            'erro': 'Timeout: backup demorou mais de 5 minutos'
        }
    except Exception as e:
        return {
            'sucesso': False,
            'erro': str(e)
        }


def executar_deploy(tipo_versao, descricao, usuario):
    """Executa todo o processo de deploy automatizado"""
    
    # Criar registro de deploy
    deploy = DeployHistorico.objects.create(
        tipo_versao=tipo_versao,
        descricao=descricao,
        usuario=usuario,
        status='em_andamento'
    )
    
    logs = []
    
    try:
        # 1. Obter versão atual e calcular nova
        logs.append("📖 Lendo versão atual...")
        versao_atual = obter_versao_atual()
        nova_versao = incrementar_versao(versao_atual, tipo_versao)
        deploy.versao = nova_versao
        deploy.save()
        logs.append(f"✅ Nova versão: v{nova_versao}")
        
        # 2. Obter arquivos modificados
        logs.append("\n🔍 Detectando mudanças no Git...")
        mudancas = obter_mudancas_git()
        if mudancas['sucesso']:
            arquivos_texto = f"Modificados: {len(mudancas['modificados'])}\n"
            arquivos_texto += f"Adicionados: {len(mudancas['adicionados'])}\n"
            arquivos_texto += f"Deletados: {len(mudancas['deletados'])}\n\n"
            arquivos_texto += "Detalhes:\n"
            for arq in mudancas['modificados']:
                arquivos_texto += f"  M {arq}\n"
            for arq in mudancas['adicionados']:
                arquivos_texto += f"  A {arq}\n"
            for arq in mudancas['deletados']:
                arquivos_texto += f"  D {arq}\n"
            
            deploy.arquivos_modificados = arquivos_texto
            deploy.save()
            logs.append(f"✅ {mudancas['total']} arquivos detectados")
        
        # 2.1. Obter estatísticas de código
        logs.append("\n📊 Calculando estatísticas de código...")
        estatisticas = obter_estatisticas_codigo()
        logs.append(f"✅ Estatísticas: {estatisticas['arquivos']} arquivo(s), +{estatisticas['insercoes']}/-{estatisticas['delecoes']} linhas")
        
        # 2.2. Fazer backup pré-deploy
        logs.append("\n💾 Fazendo backup pré-deploy...")
        backup_result = fazer_backup_pre_deploy(nova_versao)
        if backup_result['sucesso']:
            logs.append(f"✅ Backup criado: {backup_result['arquivo']} ({backup_result['tamanho_mb']})")
        else:
            logs.append(f"⚠️ Aviso: Backup falhou - {backup_result['erro']}")
            logs.append("   Deploy continuará, mas faça backup manual!")
        
        # 2.3. Criar Release Notes
        logs.append("\n📄 Criando Release Notes...")
        release_notes_result = criar_release_notes(
            nova_versao, 
            tipo_versao, 
            descricao, 
            mudancas, 
            estatisticas
        )
        if release_notes_result['sucesso']:
            logs.append(f"✅ Release Notes criado: {release_notes_result['arquivo']}")
        else:
            logs.append(f"⚠️ Aviso: Release Notes falhou - {release_notes_result['erro']}")
        
        # 3. Atualizar CHANGELOG.md
        logs.append("\n📝 Atualizando CHANGELOG.md...")
        changelog_path = os.path.join(settings.BASE_DIR, 'CHANGELOG.md')
        data_hoje = datetime.now().strftime('%d/%m/%Y')
        
        with open(changelog_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        nova_entrada = f"## v{nova_versao} — {data_hoje}\n{descricao}\n\n"
        conteudo = nova_entrada + conteudo
        
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        logs.append("✅ CHANGELOG.md atualizado")
        
        # 4. Atualizar backup_log.txt
        logs.append("\n📋 Atualizando backup_log.txt...")
        backup_log_path = os.path.join(settings.BASE_DIR, 'backup_log.txt')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,000')
        resumo_descricao = descricao.replace('\n', ' ')[:200]
        
        with open(backup_log_path, 'r', encoding='utf-8') as f:
            conteudo_backup = f.read()
        
        nova_linha_backup = f"{timestamp} - INFO - Deploy v{nova_versao} realizado: {resumo_descricao}\n"
        conteudo_backup = nova_linha_backup + conteudo_backup
        
        with open(backup_log_path, 'w', encoding='utf-8') as f:
            f.write(conteudo_backup)
        logs.append("✅ backup_log.txt atualizado")
        
        # 5. Git add
        logs.append("\n🔄 Adicionando arquivos ao Git...")
        subprocess.run(['git', 'add', '.'], cwd=settings.BASE_DIR, check=True)
        logs.append("✅ Arquivos adicionados ao stage")
        
        # 6. Git commit
        logs.append("\n💾 Criando commit...")
        mensagem_commit = f"Release v{nova_versao}\n\n{descricao}"
        subprocess.run(
            ['git', 'commit', '-m', mensagem_commit],
            cwd=settings.BASE_DIR,
            check=True
        )
        
        # Obter hash do commit
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            check=True
        )
        deploy.commit_hash = result.stdout.strip()
        deploy.save()
        logs.append(f"✅ Commit criado: {deploy.commit_hash[:8]}")
        
        # 7. Criar tag
        logs.append("\n🏷️ Criando tag...")
        subprocess.run(
            ['git', 'tag', '-a', f'v{nova_versao}', '-m', f'Versão {nova_versao}'],
            cwd=settings.BASE_DIR,
            check=True
        )
        deploy.tag_criada = f'v{nova_versao}'
        deploy.save()
        logs.append(f"✅ Tag criada: v{nova_versao}")
        
        # 8. Git push
        logs.append("\n⬆️ Enviando para o repositório remoto...")
        subprocess.run(['git', 'push'], cwd=settings.BASE_DIR, check=True)
        subprocess.run(['git', 'push', '--tags'], cwd=settings.BASE_DIR, check=True)
        logs.append("✅ Push realizado com sucesso")
        
        # Finalizar com sucesso
        deploy.status = 'sucesso'
        deploy.log_execucao = '\n'.join(logs)
        deploy.save()

        # Criar registro de AtualizacaoSistema (publicado=False)
        try:
            from configuracao.models import AtualizacaoSistema
            AtualizacaoSistema.objects.create(
                titulo=f'Atualização do Sistema v{nova_versao}',
                versao=nova_versao,
                data_publicacao=datetime.now().date(),
                conteudo=descricao,
                publicado=False
            )
            logs.append(f"✅ AtualizacaoSistema criada para revisão (v{nova_versao})")
        except Exception as e:
            logs.append(f"⚠️ Erro ao criar AtualizacaoSistema: {str(e)}")
            # Não interrompe o deploy

        return {
            'sucesso': True,
            'versao': nova_versao,
            'deploy_id': deploy.id
        }
    
    except Exception as e:
        # Registrar erro
        logs.append(f"\n❌ ERRO: {str(e)}")
        deploy.status = 'erro'
        deploy.log_execucao = '\n'.join(logs)
        deploy.erro_detalhes = str(e)
        deploy.save()
        
        return {
            'sucesso': False,
            'erro': str(e),
            'deploy_id': deploy.id
        }
