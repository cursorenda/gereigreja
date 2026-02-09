"""
Script para verificar saúde do sistema (health check)
Verifica: banco, memória, disco, processos
Uso: python health_check.py
"""

import os
import sys
import psutil
from pathlib import Path

# Adicionar o diretório raiz ao path para importar Django
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def print_status(item, status, detalhes=""):
    emoji = "✅" if status == "OK" else "⚠️" if status == "WARNING" else "❌"
    color = Colors.GREEN if status == "OK" else Colors.YELLOW if status == "WARNING" else Colors.RED
    print(f"{emoji} {item}: {color}{status}{Colors.NC} {detalhes}")

def verificar_banco():
    """Verifica conexão com banco"""
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        print_status("Banco de Dados", "OK", "Conexão estabelecida")
        return True
    except Exception as e:
        print_status("Banco de Dados", "ERROR", str(e))
        return False

def verificar_memoria():
    """Verifica uso de memória"""
    mem = psutil.virtual_memory()
    percent = mem.percent
    
    if percent < 70:
        status = "OK"
    elif percent < 90:
        status = "WARNING"
    else:
        status = "ERROR"
    
    print_status("Memória", status, f"{percent}% em uso ({mem.used // (1024**3)}GB/{mem.total // (1024**3)}GB)")
    return status != "ERROR"

def verificar_disco():
    """Verifica espaço em disco"""
    disk = psutil.disk_usage('/')
    percent = disk.percent
    
    if percent < 80:
        status = "OK"
    elif percent < 95:
        status = "WARNING"
    else:
        status = "ERROR"
    
    print_status("Disco", status, f"{percent}% em uso ({disk.used // (1024**3)}GB/{disk.total // (1024**3)}GB)")
    return status != "ERROR"

def verificar_backups():
    """Verifica existência de backups recentes"""
    backup_dir = Path('backup')
    
    if not backup_dir.exists():
        print_status("Backups", "WARNING", "Diretório não encontrado")
        return False
    
    backups = list(backup_dir.glob('backup_*.dump'))
    
    if not backups:
        print_status("Backups", "ERROR", "Nenhum backup encontrado")
        return False
    
    # Backup mais recente
    ultimo_backup = max(backups, key=lambda p: p.stat().st_mtime)
    
    from datetime import datetime, timedelta
    data_backup = datetime.fromtimestamp(ultimo_backup.stat().st_mtime)
    dias = (datetime.now() - data_backup).days
    
    if dias == 0:
        status = "OK"
        detalhes = "Backup hoje"
    elif dias <= 3:
        status = "OK"
        detalhes = f"Último backup há {dias} dia(s)"
    elif dias <= 7:
        status = "WARNING"
        detalhes = f"Último backup há {dias} dias"
    else:
        status = "ERROR"
        detalhes = f"Último backup há {dias} dias!"
    
    print_status("Backups", status, detalhes)
    return status != "ERROR"

def verificar_logs():
    """Verifica tamanho e erros recentes nos logs"""
    log_file = Path('logs/django_errors.log')
    
    if not log_file.exists():
        print_status("Logs", "OK", "Nenhum log de erro")
        return True
    
    size_mb = log_file.stat().st_size / (1024 * 1024)
    
    # Ler últimas 50 linhas
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        linhas = f.readlines()[-50:]
    
    erros_criticos = sum(1 for linha in linhas if 'CRITICAL' in linha or 'ERROR' in linha)
    
    if size_mb > 100:
        status = "WARNING"
        detalhes = f"{size_mb:.1f}MB (considere limpar)"
    elif erros_criticos > 5:
        status = "WARNING"
        detalhes = f"{erros_criticos} erros recentes"
    else:
        status = "OK"
        detalhes = f"{size_mb:.1f}MB"
    
    print_status("Logs", status, detalhes)
    return status != "ERROR"

def health_check():
    """Executa verificação completa"""
    print("🏥 Health Check do Gereigreja\n")
    
    checks = [
        ("Banco de Dados", verificar_banco),
        ("Memória", verificar_memoria),
        ("Disco", verificar_disco),
        ("Backups", verificar_backups),
        ("Logs", verificar_logs),
    ]
    
    resultados = []
    for nome, funcao in checks:
        try:
            resultado = funcao()
            resultados.append(resultado)
        except Exception as e:
            print_status(nome, "ERROR", str(e))
            resultados.append(False)
    
    # Resumo
    print("\n" + "="*50)
    total = len(resultados)
    ok = sum(resultados)
    
    if ok == total:
        print(f"{Colors.GREEN}✅ Sistema OK ({ok}/{total} checks){Colors.NC}")
        return True
    elif ok >= total * 0.7:
        print(f"{Colors.YELLOW}⚠️  Sistema com alertas ({ok}/{total} checks){Colors.NC}")
        return True
    else:
        print(f"{Colors.RED}❌ Sistema com problemas críticos ({ok}/{total} checks){Colors.NC}")
        return False

if __name__ == '__main__':
    sucesso = health_check()
    sys.exit(0 if sucesso else 1)
