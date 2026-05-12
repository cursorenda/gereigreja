from django.contrib import admin
from django.urls import path
from django.http import HttpResponse, FileResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from django.core.management import call_command
from django.core import serializers
from django.apps import apps
from deploy.models import BackupHistorico
from django.core.files.storage import default_storage

import subprocess
import os
import datetime
import io
import sys
from django.utils import timezone
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _rotacao_backups(dias_retencao=30):
    """Remove backups mais antigos que dias_retencao dias (padrão: 30 dias)."""
    try:
        limite_data = timezone.now() - datetime.timedelta(days=dias_retencao)
        backups_antigos = BackupHistorico.objects.filter(criado_em__lt=limite_data)
        
        deletados = 0
        for backup in backups_antigos:
            # Tentar deletar arquivo físico
            try:
                filepath = os.path.join('backup', backup.arquivo)
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception:
                pass
            
            # Registrar em log
            try:
                os.makedirs('backup', exist_ok=True)
                log_path = os.path.join('backup', 'backup_log.txt')
                ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                with open(log_path, 'a', encoding='utf-8') as lf:
                    lf.write(f"{ts} - Backup rotacionado (deletado): {backup.arquivo}\n")
            except Exception:
                pass
            
            # Deletar do banco
            backup.delete()
            deletados += 1
        
        if deletados > 0:
            try:
                log_path = os.path.join('backup', 'backup_log.txt')
                with open(log_path, 'a', encoding='utf-8') as lf:
                    lf.write(f"--- Total deletado por rotação: {deletados} backup(s)\n")
            except Exception:
                pass
    except Exception:
        pass


def _registrar_backup(request, filename, filepath, tipo):
    """Registra backup em log de arquivo e no banco de dados. Executa rotação de backups antigos."""
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
    
    # Executar rotação de backups antigos (a cada novo backup)
    _rotacao_backups(dias_retencao=30)


def _executar_backup_json(filepath):
    """Gera backup JSON válido de forma incremental, ignorando modelos com falha."""
    excluded_app_labels = {
        'contenttypes',
        'admin',
        'sessions',
    }
    excluded_model_labels = {
        'auth.permission',
        'admin.logentry',
        'sessions.session',
        'contenttypes.contenttype',
    }

    models_to_dump = []
    for model in apps.get_models():
        meta = model._meta
        app_label = meta.app_label
        model_label = f'{app_label}.{meta.model_name}'

        if app_label in excluded_app_labels:
            continue
        if model_label in excluded_model_labels:
            continue
        if meta.proxy or not meta.managed:
            continue

        models_to_dump.append(model)

    serialized_any = False
    errors = []

    with open(filepath, 'w', encoding='utf-8') as out:
        out.write('[\n')

        for model in models_to_dump:
            model_label = f'{model._meta.app_label}.{model._meta.model_name}'
            try:
                queryset = model._default_manager.all().iterator(chunk_size=200)

                for obj in queryset:
                    payload = serializers.serialize('json', [obj], ensure_ascii=False)
                    item = payload[1:-1].strip()
                    if not item:
                        continue

                    if serialized_any:
                        out.write(',\n')

                    out.write(item)
                    serialized_any = True
            except Exception as exc:
                errors.append(f'{model_label}: {exc}')

        out.write('\n]\n')

    if not serialized_any:
        detail = '; '.join(errors[:5]) if errors else 'nenhum registro encontrado'
        raise RuntimeError(f'Falha ao gerar backup JSON: {detail}')

    if errors:
        try:
            os.makedirs('backup', exist_ok=True)
            log_path = os.path.join('backup', 'backup_log.txt')
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            with open(log_path, 'a', encoding='utf-8') as lf:
                lf.write(f"{ts} - Backup JSON com modelos ignorados: {len(errors)}\n")
                for err in errors[:20]:
                    lf.write(f"  - {err}\n")
        except Exception:
            pass


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
