"""
Admin Dashboard customizado para desenvolvedores
Mostra métricas do sistema e ferramentas de monitoramento
"""

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.db import connection
from datetime import datetime, timedelta
import psutil
from pathlib import Path
import os
import subprocess


@staff_member_required
def dashboard_desenvolvedor(request):
    """Dashboard principal do desenvolvedor"""
    
    context = {
        'title': 'Dashboard do Desenvolvedor',
        'metricas': obter_metricas_sistema(),
        'database': obter_info_database(),
        'logs': obter_logs_recentes(),
        'backups': obter_info_backups(),
        'scripts': obter_scripts_disponiveis(),
    }
    
    return render(request, 'admin/dashboard_desenvolvedor.html', context)


@staff_member_required
def executar_comando(request):
    """Executa comandos via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Apenas POST'}, status=400)
    
    comando = request.POST.get('comando')
    
    comandos_permitidos = {
        'relatorio_membros': ['.venv\\Scripts\\python.exe', 'manage.py', 'relatorio_membros'],
        'aniversariantes': ['.venv\\Scripts\\python.exe', 'manage.py', 'aniversariantes'],
        'health_check': ['.venv\\Scripts\\python.exe', 'skills/configuracao/scripts/health_check.py'],
        'backup': ['.venv\\Scripts\\python.exe', 'skills/backup/scripts/backup.py'],
    }
    
    # Timeouts personalizados (em segundos)
    timeouts = {
        'relatorio_membros': 30,
        'aniversariantes': 30,
        'health_check': 30,
        'backup': 180,  # 3 minutos para backup
    }
    
    if comando not in comandos_permitidos:
        return JsonResponse({'erro': 'Comando não permitido'}, status=400)
    
    try:
        cmd = comandos_permitidos[comando]
        timeout = timeouts.get(comando, 30)
        
        # Definir encoding UTF-8 para suportar emojis no Windows
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(__file__).resolve().parent.parent,
            env=env,
            encoding='utf-8',
            errors='replace'
        )
        
        # Combinar stdout e stderr para mostrar tudo
        output_completo = result.stdout
        if result.stderr:
            output_completo += f"\n\n--- STDERR ---\n{result.stderr}"
        
        return JsonResponse({
            'sucesso': result.returncode == 0,
            'output': output_completo or 'Comando executado mas não retornou output.',
            'erro': result.stderr,
            'returncode': result.returncode
        })
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


def obter_metricas_sistema():
    """Obtém métricas do sistema"""
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Uptime
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    return {
        'cpu': {
            'percent': round(cpu_percent, 1),
            'cores': psutil.cpu_count(),
        },
        'memoria': {
            'percent': round(mem.percent, 1),
            'usado_gb': round(mem.used / (1024**3), 1),
            'total_gb': round(mem.total / (1024**3), 1),
            'livre_gb': round(mem.available / (1024**3), 1),
        },
        'disco': {
            'percent': round(disk.percent, 1),
            'usado_gb': round(disk.used / (1024**3), 1),
            'total_gb': round(disk.total / (1024**3), 1),
            'livre_gb': round(disk.free / (1024**3), 1),
        },
        'uptime': {
            'dias': uptime.days,
            'horas': uptime.seconds // 3600,
            'str': f'{uptime.days}d {uptime.seconds // 3600}h'
        }
    }


def obter_info_database():
    """Obtém informações do banco de dados"""
    try:
        with connection.cursor() as cursor:
            # PostgreSQL queries
            cursor.execute("SELECT version()")
            versao = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT schemaname, tablename, 
                       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 10
            """)
            tabelas = cursor.fetchall()
            
            cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            conexoes_ativas = cursor.fetchone()[0]
            
            return {
                'status': 'online',
                'versao': versao.split(',')[0],
                'conexoes_ativas': conexoes_ativas,
                'tabelas_maiores': [
                    {'schema': t[0], 'nome': t[1], 'tamanho': t[2]} 
                    for t in tabelas
                ]
            }
    except Exception as e:
        return {
            'status': 'erro',
            'mensagem': str(e)
        }


def obter_logs_recentes():
    """Obtém logs mais recentes"""
    log_file = Path('logs/django_errors.log')
    
    if not log_file.exists():
        return []
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            linhas = f.readlines()[-50:]
        
        # Parsear logs
        logs = []
        for linha in linhas:
            if any(nivel in linha for nivel in ['ERROR', 'CRITICAL', 'WARNING']):
                logs.append({
                    'texto': linha.strip(),
                    'nivel': 'error' if 'ERROR' in linha or 'CRITICAL' in linha else 'warning'
                })
        
        return logs[-20:]  # Últimos 20
    except:
        return []


def obter_info_backups():
    """Obtém informações sobre backups"""
    backup_dir = Path('backup')
    
    if not backup_dir.exists():
        return {
            'total': 0,
            'ultimo': None,
            'tamanho_total': '0 MB'
        }
    
    backups = list(backup_dir.glob('backup_*.dump'))
    
    if not backups:
        return {
            'total': 0,
            'ultimo': None,
            'tamanho_total': '0 MB'
        }
    
    # Último backup
    ultimo_backup = max(backups, key=lambda p: p.stat().st_mtime)
    data_ultimo = datetime.fromtimestamp(ultimo_backup.stat().st_mtime)
    
    # Tamanho total
    tamanho_total = sum(b.stat().st_size for b in backups)
    tamanho_mb = tamanho_total / (1024 * 1024)
    
    return {
        'total': len(backups),
        'ultimo': {
            'data': data_ultimo.strftime('%d/%m/%Y %H:%M'),
            'dias_atras': (datetime.now() - data_ultimo).days,
            'arquivo': ultimo_backup.name,
            'tamanho': f"{ultimo_backup.stat().st_size / (1024*1024):.1f} MB"
        },
        'tamanho_total': f"{tamanho_mb:.1f} MB"
    }


def obter_scripts_disponiveis():
    """Lista scripts disponíveis"""
    return [
        {
            'nome': 'Relatório de Membros',
            'comando': 'relatorio_membros',
            'descricao': 'Gera estatísticas de membros ativos/inativos',
            'icone': 'fas fa-users'
        },
        {
            'nome': 'Aniversariantes',
            'comando': 'aniversariantes',
            'descricao': 'Lista aniversariantes do mês atual',
            'icone': 'fas fa-birthday-cake'
        },
        {
            'nome': 'Health Check',
            'comando': 'health_check',
            'descricao': 'Verifica saúde do sistema',
            'icone': 'fas fa-heartbeat'
        },
        {
            'nome': 'Backup',
            'comando': 'backup',
            'descricao': 'Cria backup do banco de dados',
            'icone': 'fas fa-database'
        },
    ]

