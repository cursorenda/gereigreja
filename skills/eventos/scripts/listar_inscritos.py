"""
Script para listar inscritos em um evento
Uso: python listar_inscritos.py <evento_id> [--exportar csv]
"""

import os
import sys
import django
from datetime import datetime
import csv
from pathlib import Path

# Adicionar o diretório raiz ao path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from eventos.models import Evento, ParticipacaoEvento

class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def listar_inscritos(evento_id, exportar=False):
    """Lista todos os inscritos de um evento"""
    try:
        evento = Evento.objects.get(id=evento_id)
    except Evento.DoesNotExist:
        print(f"{Colors.RED}❌ Evento não encontrado: {evento_id}{Colors.NC}")
        return False
    
    inscricoes = ParticipacaoEvento.objects.filter(evento=evento).select_related('membro').order_by('criado_em')
    
    # Cabeçalho
    print(f"\n{Colors.BLUE}{'='*70}{Colors.NC}")
    print(f"{Colors.BLUE}📋 INSCRITOS: {evento.titulo}{Colors.NC}")
    print(f"{Colors.BLUE}📅 Data: {evento.data_inicio.strftime('%d/%m/%Y')}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*70}{Colors.NC}\n")
    
    if not inscricoes:
        print(f"{Colors.YELLOW}Nenhuma inscrição encontrada.{Colors.NC}\n")
        return True
    
    # Estatísticas
    total = inscricoes.count()
    confirmados = inscricoes.filter(status='CONFIRMADO').count()
    pendentes = total - confirmados
    
    print(f"{Colors.GREEN}Total: {total} inscrição(ões){Colors.NC}")
    print(f"{Colors.GREEN}Confirmados: {confirmados}{Colors.NC}")
    print(f"{Colors.YELLOW}Pendentes: {pendentes}{Colors.NC}\n")
    
    # Lista de inscritos
    print(f"{'#':<4} {'Nome':<35} {'Telefone':<15} {'Status':<12} {'Data':<12}")
    print("─" * 80)
    
    for i, inscricao in enumerate(inscricoes, 1):
        membro = inscricao.membro or inscricao.convidado_nome
        nome = membro.nome if hasattr(membro, 'nome') else str(membro)
        telefone = membro.telefone if hasattr(membro, 'telefone') else '-'
        status = f"{Colors.GREEN}✅ Confirmado{Colors.NC}" if inscricao.status == 'CONFIRMADO' else f"{Colors.YELLOW}⏳ Pendente{Colors.NC}"
        data = inscricao.criado_em.strftime('%d/%m/%Y')
        
        # Remove cores para alinhamento correto
        status_plain = "Confirmado" if inscricao.status == 'CONFIRMADO' else "Pendente"
        
        print(f"{i:<4} {nome:<35} {telefone:<15} {status_plain:<12} {data:<12}")
    
    print("\n")
    
    # Exportar para CSV se solicitado
    if exportar:
        exportar_csv(evento, inscricoes)
    
    return True

def exportar_csv(evento, inscricoes):
    """Exporta lista de inscritos para CSV"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f"inscritos_{evento.id}_{timestamp}.csv"
    
    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Cabeçalho do arquivo
        writer.writerow(['INSCRITOS NO EVENTO'])
        writer.writerow([f'Evento: {evento.titulo}'])
        writer.writerow([f'Data: {evento.data_inicio.strftime("%d/%m/%Y")}'])
        writer.writerow([f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}'])
        writer.writerow([])
        
        # Cabeçalho da tabela
        writer.writerow(['#', 'Nome', 'Telefone', 'Email', 'Status', 'Data Inscrição'])
        
        # Dados
        for i, inscricao in enumerate(inscricoes, 1):
            membro = inscricao.membro
            nome = membro.nome if membro else inscricao.convidado_nome
            telefone = membro.telefone if membro else ''
            email = membro.email if membro else inscricao.convidado_email or ''
            status = 'Confirmado' if inscricao.status == 'CONFIRMADO' else 'Pendente'
            data = inscricao.criado_em.strftime('%d/%m/%Y')
            
            writer.writerow([
                i,
                nome,
                telefone,
                email,
                status,
                data
            ])
    
    print(f"{Colors.GREEN}✅ Exportado para: {nome_arquivo}{Colors.NC}\n")

def listar_eventos():
    """Lista todos os eventos disponíveis"""
    eventos = Evento.objects.all().order_by('-data_inicio')[:20]
    
    print(f"\n{Colors.BLUE}📋 EVENTOS DISPONÍVEIS{Colors.NC}\n")
    print(f"{'ID':<6} {'Título':<40} {'Data':<12} {'Inscritos':<10}")
    print("─" * 70)
    
    for evento in eventos:
        total_inscritos = evento.participacoes.count()
        data = evento.data_inicio.strftime('%d/%m/%Y')
        print(f"{evento.id:<6} {evento.titulo:<40} {data:<12} {total_inscritos:<10}")
    
    print("\n")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print(f"\n{Colors.YELLOW}Uso: python listar_inscritos.py <evento_id> [--exportar csv]{Colors.NC}")
        print(f"{Colors.YELLOW}Ou: python listar_inscritos.py --lista (para ver eventos){Colors.NC}\n")
        sys.exit(1)
    
    # Listar eventos
    if sys.argv[1] == '--lista':
        listar_eventos()
        return
    
    # Obter ID do evento
    try:
        evento_id = int(sys.argv[1])
    except ValueError:
        print(f"{Colors.RED}❌ ID do evento deve ser um número{Colors.NC}")
        sys.exit(1)
    
    # Verificar se deve exportar
    exportar = '--exportar' in sys.argv or 'csv' in sys.argv
    
    # Listar inscritos
    sucesso = listar_inscritos(evento_id, exportar)
    sys.exit(0 if sucesso else 1)

if __name__ == '__main__':
    main()
