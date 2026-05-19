"""
Script para restaurar backup do banco de dados
Uso: python restore.py backup_20260205_143000.dump
"""

import os
import sys
import subprocess
from pathlib import Path

# Configurações
BACKUP_DIR = Path(__file__).parent.parent.parent.parent / 'backup'

def restaurar_backup(backup_file):
    """Restaura backup do banco PostgreSQL"""
    backup_path = BACKUP_DIR / backup_file
    
    if not backup_path.exists():
        print(f"❌ Erro: Arquivo {backup_file} não encontrado!")
        return False
    
    print(f"⚠️  ATENÇÃO: Este processo irá SUBSTITUIR todos os dados atuais!")
    print(f"📁 Arquivo: {backup_file}")
    
    confirmar = input("Digite 'CONFIRMO' para prosseguir: ")
    
    if confirmar != 'CONFIRMO':
        print("❌ Restauração cancelada.")
        return False
    
    # Ler credenciais do ambiente
    db_host = os.getenv('SUPABASE_DB_HOST')
    db_user = os.getenv('SUPABASE_DB_USER')
    db_name = os.getenv('SUPABASE_DB_NAME')
    db_password = os.getenv('SUPABASE_DB_PASSWORD')
    
    if not all([db_host, db_user, db_name, db_password]):
        print("❌ Erro: Variáveis de ambiente não configuradas!")
        return False
    
    print("🔄 Iniciando restauração...")
    
    # Comando pg_restore
    command = [
        'pg_restore',
        '-h', db_host,
        '-U', db_user,
        '-d', db_name,
        '-c',  # Clean (drop objetos antes)
        '--if-exists',  # Não dar erro se não existir
        str(backup_path)
    ]
    
    # Definir senha via ambiente
    env = os.environ.copy()
    env['PGPASSWORD'] = db_password
    
    try:
        subprocess.run(command, check=True, env=env)
        print(f"✅ Restauração concluída com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao restaurar backup: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python restore.py <arquivo_backup>")
        print("\nBackups disponíveis:")
        for backup in sorted(BACKUP_DIR.glob('backup_*.dump'), reverse=True)[:10]:
            size_mb = backup.stat().st_size / (1024 * 1024)
            print(f"  - {backup.name} ({size_mb:.2f} MB)")
        sys.exit(1)
    
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    restaurar_backup(sys.argv[1])
