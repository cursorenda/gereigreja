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
from django.utils import timezone
from datetime import datetime, timedelta
import psutil
from pathlib import Path
import os
import subprocess
from deploy.models import BackupHistorico
from hinario.models import HinoGlobal, HinoDaIgreja, HinoAuditLog
from painel_desenvolvedor.services_custo_risco import analisar_risco_whatsapp_assinaturas


@staff_member_required
def dashboard_desenvolvedor(request):
    """Dashboard principal do desenvolvedor"""
    metricas = obter_metricas_sistema()
    logs = obter_logs_recentes()
    backups = obter_info_backups()
    hinario_compliance = obter_info_hinario_compliance()
    foco_operacional = obter_foco_operacional(metricas, logs, backups, hinario_compliance)
    
    context = {
        'title': 'Dashboard do Desenvolvedor',
        'metricas': metricas,
        'database': obter_info_database(),
        'logs': logs,
        'backups': backups,
        'hinario_compliance': hinario_compliance,
        'hinario_liberados_recentes': obter_hinarios_liberados_recentes(),
        'scripts': obter_scripts_disponiveis(),
        'foco_operacional': foco_operacional,
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
    ultimo_backup_db = BackupHistorico.objects.order_by('-criado_em').first()
    if ultimo_backup_db:
        data_ultimo = ultimo_backup_db.criado_em
        if timezone.is_naive(data_ultimo):
            data_ultimo = timezone.make_aware(data_ultimo)

        total_backups = BackupHistorico.objects.count()

        return {
            'total': total_backups,
            'ultimo': {
                'data': timezone.localtime(data_ultimo).strftime('%d/%m/%Y %H:%M'),
                'dias_atras': (timezone.now() - data_ultimo).days,
                'arquivo': ultimo_backup_db.arquivo,
                'tamanho': f"{(ultimo_backup_db.tamanho_bytes or 0) / (1024*1024):.1f} MB"
            },
            'tamanho_total': f"{(sum(BackupHistorico.objects.values_list('tamanho_bytes', flat=True)) or 0) / (1024 * 1024):.1f} MB"
        }

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


def obter_info_hinario_compliance():
    """Obtém indicadores da fila de compliance de hinos."""
    status_pendentes = ['pending_review', 'unknown', 'restricted']

    pendentes_global = HinoGlobal.objects.filter(
        blocked_for_public_use=True,
        license_status__in=status_pendentes,
    ).count()

    pendentes_igreja = HinoDaIgreja.objects.filter(
        blocked_for_public_use=True,
        license_status__in=status_pendentes,
    ).count()

    return {
        'pendentes_global': pendentes_global,
        'pendentes_igreja': pendentes_igreja,
        'pendentes_total': pendentes_global + pendentes_igreja,
    }


def obter_hinarios_liberados_recentes(limite=5):
    """Retorna os hinos mais recentemente liberados na auditoria."""
    eventos = (
        HinoAuditLog.objects.filter(action='unblocked')
        .select_related('actor_user', 'tenant_igreja')
        .order_by('-created_at')[:limite]
    )

    itens = []
    for evento in eventos:
        dados_after = evento.after_json or {}
        colecao = dados_after.get('colecao', '-')
        numero = dados_after.get('numero', '-')
        titulo = dados_after.get('titulo', '-')
        igreja_nome = getattr(evento.tenant_igreja, 'nome', None)

        itens.append({
            'id': evento.id,
            'target_type': evento.target_type,
            'colecao': colecao,
            'numero': numero,
            'titulo': titulo,
            'igreja_nome': igreja_nome,
            'actor': getattr(evento.actor_user, 'username', None) or '-',
            'data': timezone.localtime(evento.created_at).strftime('%d/%m/%Y %H:%M'),
        })

    return itens


def obter_foco_operacional(metricas, logs, backups, hinario_compliance):
    """Consolida prioridades do dia e estado operacional para o dashboard dev."""
    prioridades = []
    estados = []

    # 1) Backup
    backup_dias_atras = 999
    if backups.get('ultimo'):
        backup_dias_atras = backups['ultimo'].get('dias_atras', 999) or 999
    if backup_dias_atras <= 1:
        backup_status = 'ok'
        backup_texto = 'Backup recente em dia.'
    elif backup_dias_atras <= 3:
        backup_status = 'alerta'
        backup_texto = f'Ultimo backup ha {backup_dias_atras} dia(s).'
    else:
        backup_status = 'critico'
        backup_texto = f'Backup atrasado ha {backup_dias_atras} dia(s).'

    estados.append({
        'nome': 'Backups',
        'status': backup_status,
        'detalhe': backup_texto,
    })
    if backup_status != 'ok':
        prioridades.append({
            'titulo': 'Revisar rotina de backup',
            'detalhe': backup_texto,
            'status': backup_status,
        })

    # 2) Infra (CPU e memoria)
    cpu = float(metricas.get('cpu', {}).get('percent', 0) or 0)
    memoria = float(metricas.get('memoria', {}).get('percent', 0) or 0)
    if cpu >= 90 or memoria >= 90:
        infra_status = 'critico'
    elif cpu >= 75 or memoria >= 80:
        infra_status = 'alerta'
    else:
        infra_status = 'ok'
    estados.append({
        'nome': 'Infra',
        'status': infra_status,
        'detalhe': f'CPU {cpu}% | RAM {memoria}%',
    })
    if infra_status != 'ok':
        prioridades.append({
            'titulo': 'Monitorar recursos do servidor',
            'detalhe': f'CPU em {cpu}% e RAM em {memoria}%.',
            'status': infra_status,
        })

    # 3) Logs
    erros_logs = len([l for l in logs if l.get('nivel') == 'error'])
    if erros_logs == 0:
        logs_status = 'ok'
        logs_texto = 'Sem erros recentes no log.'
    elif erros_logs <= 5:
        logs_status = 'alerta'
        logs_texto = f'{erros_logs} erro(s) recente(s) no log.'
    else:
        logs_status = 'critico'
        logs_texto = f'{erros_logs} erros recentes no log.'
    estados.append({
        'nome': 'Aplicacao',
        'status': logs_status,
        'detalhe': logs_texto,
    })
    if logs_status != 'ok':
        prioridades.append({
            'titulo': 'Investigar erros de aplicacao',
            'detalhe': logs_texto,
            'status': logs_status,
        })

    # 4) Compliance de hinos
    pendentes_hinario = int(hinario_compliance.get('pendentes_total', 0) or 0)
    if pendentes_hinario == 0:
        compliance_status = 'ok'
        compliance_texto = 'Sem pendencias de compliance.'
    elif pendentes_hinario <= 20:
        compliance_status = 'alerta'
        compliance_texto = f'{pendentes_hinario} pendencia(s) de compliance.'
    else:
        compliance_status = 'critico'
        compliance_texto = f'{pendentes_hinario} pendencias de compliance em fila.'
    estados.append({
        'nome': 'Compliance',
        'status': compliance_status,
        'detalhe': compliance_texto,
    })
    if compliance_status != 'ok':
        prioridades.append({
            'titulo': 'Limpar fila de compliance',
            'detalhe': compliance_texto,
            'status': compliance_status,
        })

    # 5) Financeiro operacional do WhatsApp
    try:
        analise = analisar_risco_whatsapp_assinaturas()
        risco_global = analise.get('resumo', {}).get('risco_global', 'indefinido')
        share = float(analise.get('resumo', {}).get('share_total', 0) or 0)
        if risco_global == 'alto' or share >= 0.9:
            custo_status = 'critico'
        elif risco_global == 'medio' or share >= 0.6:
            custo_status = 'alerta'
        else:
            custo_status = 'ok'

        custo_texto = f'Risco {risco_global} | Share {share:.2f}x'
        estados.append({
            'nome': 'Custo WhatsApp',
            'status': custo_status,
            'detalhe': custo_texto,
        })
        if custo_status != 'ok':
            prioridades.append({
                'titulo': 'Revisar margem do WhatsApp',
                'detalhe': custo_texto,
                'status': custo_status,
            })
    except Exception:
        estados.append({
            'nome': 'Custo WhatsApp',
            'status': 'alerta',
            'detalhe': 'Analise indisponivel no momento.',
        })

    ordem = {'critico': 0, 'alerta': 1, 'ok': 2}
    prioridades.sort(key=lambda p: ordem.get(p.get('status', 'ok'), 3))

    total_critico = len([e for e in estados if e.get('status') == 'critico'])
    total_alerta = len([e for e in estados if e.get('status') == 'alerta'])
    total_ok = len([e for e in estados if e.get('status') == 'ok'])

    if total_critico > 0:
        panorama = 'critico'
    elif total_alerta > 0:
        panorama = 'alerta'
    else:
        panorama = 'ok'

    if not prioridades:
        prioridades = [{
            'titulo': 'Operacao estavel',
            'detalhe': 'Nenhuma prioridade critica para hoje.',
            'status': 'ok',
        }]

    return {
        'prioridades': prioridades[:5],
        'estados': estados,
        'resumo': {
            'critico': total_critico,
            'alerta': total_alerta,
            'ok': total_ok,
            'panorama': panorama,
        },
    }

