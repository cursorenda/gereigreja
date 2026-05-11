from django.contrib import admin
from django.urls import path
from django.http import HttpResponse, FileResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from django.core.management import call_command
from deploy.models import BackupHistorico
from django.core.files.storage import default_storage

import subprocess
import os
import datetime
import io
import sys
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _registrar_backup(request, filename, filepath, tipo):
    """Registra backup em log de arquivo e no banco de dados."""
    # Log em arquivo (compatibilidade com rotina existente)
    try:
        os.makedirs('backup', exist_ok=True)
        log_path = os.path.join('backup', 'backup_log.txt')
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(log_path, 'a', encoding='utf-8') as lf:
            lf.write(f"{ts} - Backup criado: {filename}\n")
    except Exception:
        pass

    # Persistencia no banco (fonte de verdade para producao)
    try:
        tamanho_bytes = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        BackupHistorico.objects.create(
            arquivo=filename,
            tipo=tipo,
            tamanho_bytes=tamanho_bytes,
            usuario=request.user if request.user.is_authenticated else None,
        )
    except Exception:
        pass


def _executar_backup_json(filepath):
    """Executa dumpdata em subprocesso com opções seguras para evitar recursão."""
    command = [
        sys.executable,
        'manage.py',
        'dumpdata',
        '--exclude=contenttypes',
        '--exclude=auth.permission',
        '--exclude=sessions.session',
        '--exclude=admin.logentry',
        '--indent=2',
        '--output',
        filepath,
    ]

    result = subprocess.run(
        command,
        cwd=os.path.dirname(os.path.dirname(__file__)),
        capture_output=True,
        text=True,
        timeout=300,
        encoding='utf-8',
        errors='replace',
    )
    if result.returncode != 0:
        erro = result.stderr.strip() or result.stdout.strip() or 'Erro desconhecido ao executar dumpdata'
        raise RuntimeError(erro)


def _adicionar_storage_ao_zip(zipf, storage, path=''):
    """Adiciona arquivos do storage Django ao zip de forma recursiva."""
    total_arquivos = 0
    diretorios, arquivos = storage.listdir(path)

    for nome_arquivo in arquivos:
        storage_path = f'{path}/{nome_arquivo}' if path else nome_arquivo
        with storage.open(storage_path, 'rb') as arquivo_origem:
            zipf.writestr(storage_path, arquivo_origem.read())
        total_arquivos += 1

    for nome_diretorio in diretorios:
        diretorio_path = f'{path}/{nome_diretorio}' if path else nome_diretorio
        total_arquivos += _adicionar_storage_ao_zip(zipf, storage, diretorio_path)

    return total_arquivos

# View para backup JSON (funciona em qualquer ambiente)
@staff_member_required
def backup_json(request):
    """Backup usando Django dumpdata - funciona no servidor sem pg_dump"""
    try:
        filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join('backup', filename)
        
        # Criar diretório se não existir
        os.makedirs('backup', exist_ok=True)

        # Usar dumpdata em subprocesso com exclusões seguras
        _executar_backup_json(filepath)

        _registrar_backup(request, filename, filepath, 'json')
        
        # Retornar arquivo para download
        response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
        return response
    except Exception as e:
        return HttpResponse(f'Erro ao gerar backup JSON: {e}', status=500)

# View para backup SQL (apenas para ambiente local com pg_dump)
# View para backup SQL (apenas para ambiente local com pg_dump)
@staff_member_required
def backup_custom(request):
    """Backup usando pg_dump - apenas funciona localmente ou com pg_dump instalado"""
    try:
        # Verificar se pg_dump está disponível (Windows usa 'where', Linux/Mac usa 'which')
        import platform
        check_command = 'where' if platform.system() == 'Windows' else 'which'
        
        try:
            check_cmd = subprocess.run([check_command, 'pg_dump'], capture_output=True, text=True)
            if check_cmd.returncode != 0:
                raise FileNotFoundError("pg_dump não encontrado")
        except FileNotFoundError:
            # pg_dump não disponível
            return HttpResponse(
                '<h2>❌ pg_dump não está disponível</h2>'
                '<p>O comando pg_dump não foi encontrado no sistema.</p>'
                '<p><strong>Solução:</strong> Use o <a href="/backup/json/">💾 Backup JSON</a> que funciona em qualquer ambiente.</p>'
                '<br><p><small>Para usar pg_dump, instale o PostgreSQL client tools.</small></p>',
                status=400
            )
        
        filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.dump"
        filepath = os.path.join('backup', filename)
        
        # Criar diretório se não existir
        os.makedirs('backup', exist_ok=True)
        
        cmd = [
            'pg_dump',
            '-h', os.environ.get('DB_HOST', 'aws-0-us-east-2.pooler.supabase.com'),
            '-U', os.environ.get('DB_USER', 'postgres.vxzntgknvejluffgttpg'),
            '-d', os.environ.get('DB_NAME', 'postgres'),
            '-F', 'c',
            '-b',
            '-v',
            '-f', filepath
        ]
        env = os.environ.copy()
        env['PGPASSWORD'] = os.environ.get('PGPASSWORD', '')
        
        subprocess.run(cmd, check=True, env=env)
        _registrar_backup(request, filename, filepath, 'dump')
        response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
        return response
    except Exception as e:
        return HttpResponse(f'Erro ao gerar backup: {e}<br><br>Use <a href="/backup/json/">Backup JSON</a> que funciona em qualquer ambiente.', status=500)

# View para backup SQL
@staff_member_required
def backup_sql(request):
    """Backup SQL usando pg_dump - apenas funciona localmente"""
    try:
        # Verificar se pg_dump está disponível (Windows usa 'where', Linux/Mac usa 'which')
        import platform
        check_command = 'where' if platform.system() == 'Windows' else 'which'
        
        try:
            check_cmd = subprocess.run([check_command, 'pg_dump'], capture_output=True, text=True)
            if check_cmd.returncode != 0:
                raise FileNotFoundError("pg_dump não encontrado")
        except FileNotFoundError:
            return HttpResponse(
                '<h2>❌ pg_dump não está disponível</h2>'
                '<p>O comando pg_dump não foi encontrado no sistema.</p>'
                '<p><strong>Solução:</strong> Use o <a href="/backup/json/">💾 Backup JSON</a> que funciona em qualquer ambiente.</p>'
                '<br><p><small>Para usar pg_dump, instale o PostgreSQL client tools.</small></p>',
                status=400
            )
        
        filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        filepath = os.path.join('backup', filename)
        
        # Criar diretório se não existir
        os.makedirs('backup', exist_ok=True)
        
        cmd = [
            'pg_dump',
            '-h', os.environ.get('DB_HOST', 'aws-0-us-east-2.pooler.supabase.com'),
            '-U', os.environ.get('DB_USER', 'postgres.vxzntgknvejluffgttpg'),
            '-d', os.environ.get('DB_NAME', 'postgres'),
            '-F', 'p',
            '-b',
            '-v',
            '-f', filepath
        ]
        env = os.environ.copy()
        env['PGPASSWORD'] = os.environ.get('PGPASSWORD', '')
        
        subprocess.run(cmd, check=True, env=env)
        _registrar_backup(request, filename, filepath, 'sql')
        response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
        return response
    except Exception as e:
        return HttpResponse(f'Erro ao gerar backup: {e}<br><br>Use <a href="/backup/json/">Backup JSON</a> que funciona em qualquer ambiente.', status=500)

# View para backup de arquivos (media)
@staff_member_required
def backup_arquivos(request):
    """Backup de todos os arquivos da pasta media (uploads, fotos, documentos)"""
    try:
        import zipfile
        from django.conf import settings
        
        filename = f"backup_arquivos_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        filepath = os.path.join('backup', filename)
        
        # Criar diretório se não existir
        os.makedirs('backup', exist_ok=True)

        # Criar ZIP a partir do backend de storage configurado (local ou remoto)
        try:
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                total_arquivos = _adicionar_storage_ao_zip(zipf, default_storage)
        except NotImplementedError:
            return HttpResponse(
                'O storage atual não suporta listagem de arquivos para gerar ZIP automático. '
                'No ambiente atual, os arquivos estão em storage remoto e exigem rotina específica de exportação.',
                status=400,
            )

        if total_arquivos == 0:
            return HttpResponse(
                'Nenhum arquivo foi encontrado no storage configurado para gerar o ZIP de backup.',
                status=404,
            )
        
        # Verificar se o arquivo foi criado
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            return HttpResponse('Erro ao criar arquivo de backup.', status=500)

        _registrar_backup(request, filename, filepath, 'zip')
        
        # Retornar arquivo para download
        response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
        return response
        
    except Exception as e:
        return HttpResponse(f'Erro ao gerar backup de arquivos: {e}', status=500)

# URLs para as views de backup
backup_urls = [
    path('backup/json/', backup_json, name='backup_json'),
    path('backup/arquivos/', backup_arquivos, name='backup_arquivos'),
    path('backup/custom/', backup_custom, name='backup_custom'),
    path('backup/sql/', backup_sql, name='backup_sql'),
]
