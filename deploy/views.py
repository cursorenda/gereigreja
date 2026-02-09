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
