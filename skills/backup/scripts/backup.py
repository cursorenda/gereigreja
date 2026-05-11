"""
Script Python para backup automático do banco de dados
Uso: python backup.py
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path e carregar .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    print("⚠️ python-dotenv não instalado. Usando variáveis do sistema.")

# Configurações
BACKUP_DIR = BASE_DIR / 'backup'
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
FILENAME = f'backup_{TIMESTAMP}.dump'
FILEPATH = BACKUP_DIR / FILENAME

# Criar diretório se não existir
BACKUP_DIR.mkdir(exist_ok=True)

def fazer_backup():
    """Executa backup do banco PostgreSQL"""
    print("🔄 Iniciando backup do banco de dados...")
    print(f"📁 Destino: {FILEPATH}")
    
    # Tentar ler do Django settings primeiro
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        from django.conf import settings
        from deploy.models import BackupHistorico
        
        db_config = settings.DATABASES['default']
        db_host = db_config.get('HOST')
        db_user = db_config.get('USER')
        db_name = db_config.get('NAME')
        db_password = db_config.get('PASSWORD')
        
        print("✅ Credenciais carregadas do Django settings")
    except Exception as e:
        # Fallback: tentar ler do .env com nomes corretos
        print(f"⚠️ Django não disponível, tentando .env: {e}")
        db_host = os.getenv('DB_HOST') or os.getenv('SUPABASE_DB_HOST')
        db_user = os.getenv('DB_USER') or os.getenv('SUPABASE_DB_USER')
        db_name = os.getenv('DB_NAME') or os.getenv('SUPABASE_DB_NAME')
        db_password = os.getenv('DB_PASSWORD') or os.getenv('SUPABASE_DB_PASSWORD')
    
    # Debug: mostrar quais variáveis estão faltando
    if not all([db_host, db_user, db_name, db_password]):
        print("❌ Erro: Variáveis de ambiente não configuradas!")
        if not db_host: print("   - DB_HOST não encontrada")
        if not db_user: print("   - DB_USER não encontrada")
        if not db_name: print("   - DB_NAME não encontrada")
        if not db_password: print("   - DB_PASSWORD não encontrada")
        print(f"   - Arquivo .env: {BASE_DIR / '.env'}")
        print(f"   - Arquivo existe: {(BASE_DIR / '.env').exists()}")
        return False
    
    # Comando pg_dump
    print(f"🔌 Conectando ao banco: {db_host}")
    print(f"👤 Usuário: {db_user}")
    print(f"🗄️ Database: {db_name}")
    
    command = [
        'pg_dump',
        '-h', db_host,
        '-U', db_user,
        '-d', db_name,
        '-F', 'c',  # Formato custom (comprimido)
        '-f', str(FILEPATH),
        '-w'  # Nunca pedir senha (usar PGPASSWORD)
    ]
    
    # Definir senha via ambiente
    env = os.environ.copy()
    env['PGPASSWORD'] = db_password
    
    try:
        print("⏳ Executando pg_dump (pode demorar alguns minutos)...")
        
        # Executar backup com timeout de 2 minutos
        result = subprocess.run(
            command, 
            check=True, 
            env=env,
            timeout=120,  # 2 minutos
            capture_output=True,
            text=True
        )
        
        # Mostrar stderr se houver avisos (não necessariamente erros)
        if result.stderr:
            print(f"⚠️ Avisos: {result.stderr}")
        
        # Registrar no log
        log_file = BACKUP_DIR / 'backup_log.txt'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f'{TIMESTAMP} - Backup criado: {FILENAME}\n')

        # Persistir historico no banco para os dashboards
        try:
            BackupHistorico.objects.create(
                arquivo=FILENAME,
                tipo='dump',
                tamanho_bytes=FILEPATH.stat().st_size,
                usuario=None,
            )
        except Exception as exc:
            print(f"⚠️ Não foi possível registrar BackupHistorico: {exc}")
        
        # Informações
        size_mb = FILEPATH.stat().st_size / (1024 * 1024)
        print(f"✅ Backup concluído com sucesso!")
        print(f"📦 Arquivo: {FILENAME}")
        print(f"📊 Tamanho: {size_mb:.2f} MB")
        
        # Limpar backups antigos
        limpar_backups_antigos()
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout: Backup demorou mais de 2 minutos")
        print(f"   Isso pode indicar:")
        print(f"   - Banco de dados muito grande")
        print(f"   - Conexão lenta com o servidor")
        print(f"   - pg_dump não está instalado ou configurado")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar pg_dump: {e}")
        if e.stderr:
            print(f"   Detalhes: {e.stderr}")
        return False
        
    except FileNotFoundError:
        print(f"❌ Erro: pg_dump não encontrado!")
        print(f"   Instale o PostgreSQL client: https://www.postgresql.org/download/")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def limpar_backups_antigos(dias=30):
    """Remove backups com mais de X dias"""
    from datetime import timedelta
    
    limite = datetime.now() - timedelta(days=dias)
    removidos = 0
    
    for backup in BACKUP_DIR.glob('backup_*.dump'):
        # Obter data do nome do arquivo
        try:
            data_str = backup.stem.split('_')[1] + '_' + backup.stem.split('_')[2]
            data_backup = datetime.strptime(data_str, '%Y%m%d_%H%M%S')
            
            if data_backup < limite:
                backup.unlink()
                removidos += 1
        except:
            continue
    
    if removidos > 0:
        print(f"🧹 {removidos} backup(s) antigo(s) removido(s) (>{dias} dias)")

if __name__ == '__main__':
    # Carregar variáveis de ambiente do .env
    from dotenv import load_dotenv
    load_dotenv()
    
    fazer_backup()
