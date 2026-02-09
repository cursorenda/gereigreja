"""
Views para Dashboard de Monitoramento do Sistema
Mostra saúde do servidor em tempo real
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connection
from datetime import datetime, timedelta
import psutil
from pathlib import Path
import os

@login_required
def dashboard_sistema(request):
    """Renderiza página do dashboard"""
    return render(request, 'configuracao/dashboard_sistema.html')

@login_required
def api_metricas_sistema(request):
    """API que retorna métricas do sistema em JSON"""
    
    metricas = {
        'timestamp': datetime.now().isoformat(),
        'banco': verificar_banco(),
        'memoria': verificar_memoria(),
        'disco': verificar_disco(),
        'backups': verificar_backups(),
        'logs': verificar_logs(),
        'servidor': obter_info_servidor()
    }
    
    # Calcular status geral
    checks = [
        metricas['banco']['ok'],
        metricas['memoria']['ok'],
        metricas['disco']['ok'],
        metricas['backups']['ok'],
        metricas['logs']['ok']
    ]
    
    metricas['geral'] = {
        'total': len(checks),
        'ok': sum(checks),
        'status': 'ok' if sum(checks) == len(checks) else 'warning' if sum(checks) >= len(checks) * 0.7 else 'error'
    }
    
    return JsonResponse(metricas)

def verificar_banco():
    """Verifica conexão com banco"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return {
            'ok': True,
            'status': 'ok',
            'mensagem': 'Conexão estabelecida'
        }
    except Exception as e:
        return {
            'ok': False,
            'status': 'error',
            'mensagem': str(e)
        }

def verificar_memoria():
    """Verifica uso de memória"""
    mem = psutil.virtual_memory()
    percent = mem.percent
    
    if percent < 70:
        status = 'ok'
    elif percent < 90:
        status = 'warning'
    else:
        status = 'error'
    
    return {
        'ok': status == 'ok',
        'status': status,
        'percent': round(percent, 1),
        'usado_gb': round(mem.used / (1024**3), 1),
        'total_gb': round(mem.total / (1024**3), 1),
        'livre_gb': round(mem.available / (1024**3), 1),
        'mensagem': f'{percent:.1f}% em uso ({mem.used // (1024**3)}GB/{mem.total // (1024**3)}GB)'
    }

def verificar_disco():
    """Verifica espaço em disco"""
    disk = psutil.disk_usage('/')
    percent = disk.percent
    
    if percent < 80:
        status = 'ok'
    elif percent < 95:
        status = 'warning'
    else:
        status = 'error'
    
    return {
        'ok': status != 'error',
        'status': status,
        'percent': round(percent, 1),
        'usado_gb': round(disk.used / (1024**3), 1),
        'total_gb': round(disk.total / (1024**3), 1),
        'livre_gb': round(disk.free / (1024**3), 1),
        'mensagem': f'{percent:.1f}% em uso ({disk.used // (1024**3)}GB/{disk.total // (1024**3)}GB)'
    }

def verificar_backups():
    """Verifica existência de backups recentes"""
    backup_dir = Path('backup')
    
    if not backup_dir.exists():
        return {
            'ok': False,
            'status': 'warning',
            'mensagem': 'Diretório não encontrado',
            'ultimo': None,
            'dias': None
        }
    
    backups = list(backup_dir.glob('backup_*.dump'))
    
    if not backups:
        return {
            'ok': False,
            'status': 'error',
            'mensagem': 'Nenhum backup encontrado',
            'ultimo': None,
            'dias': None
        }
    
    # Backup mais recente
    ultimo_backup = max(backups, key=lambda p: p.stat().st_mtime)
    data_backup = datetime.fromtimestamp(ultimo_backup.stat().st_mtime)
    dias = (datetime.now() - data_backup).days
    
    if dias == 0:
        status = 'ok'
        mensagem = 'Backup hoje'
    elif dias <= 3:
        status = 'ok'
        mensagem = f'Último backup há {dias} dia(s)'
    elif dias <= 7:
        status = 'warning'
        mensagem = f'Último backup há {dias} dias'
    else:
        status = 'error'
        mensagem = f'Último backup há {dias} dias!'
    
    return {
        'ok': status != 'error',
        'status': status,
        'mensagem': mensagem,
        'ultimo': data_backup.strftime('%d/%m/%Y %H:%M'),
        'dias': dias,
        'total': len(backups)
    }

def verificar_logs():
    """Verifica tamanho e erros recentes nos logs"""
    log_file = Path('logs/django_errors.log')
    
    if not log_file.exists():
        return {
            'ok': True,
            'status': 'ok',
            'mensagem': 'Nenhum log de erro',
            'tamanho_mb': 0,
            'erros_recentes': 0
        }
    
    size_mb = log_file.stat().st_size / (1024 * 1024)
    
    # Ler últimas 50 linhas
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            linhas = f.readlines()[-50:]
        erros_criticos = sum(1 for linha in linhas if 'CRITICAL' in linha or 'ERROR' in linha)
    except:
        erros_criticos = 0
    
    if size_mb > 100:
        status = 'warning'
        mensagem = f'{size_mb:.1f}MB (considere limpar)'
    elif erros_criticos > 5:
        status = 'warning'
        mensagem = f'{erros_criticos} erros recentes'
    else:
        status = 'ok'
        mensagem = f'{size_mb:.1f}MB'
    
    return {
        'ok': status != 'error',
        'status': status,
        'mensagem': mensagem,
        'tamanho_mb': round(size_mb, 1),
        'erros_recentes': erros_criticos
    }

def obter_info_servidor():
    """Obtém informações gerais do servidor"""
    import platform
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    # Uptime
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    return {
        'sistema': platform.system(),
        'versao': platform.release(),
        'arquitetura': platform.machine(),
        'processador': platform.processor()[:50],
        'cpu_percent': round(cpu_percent, 1),
        'cpu_cores': cpu_count,
        'uptime_dias': uptime.days,
        'uptime_str': f'{uptime.days}d {uptime.seconds // 3600}h'
    }
