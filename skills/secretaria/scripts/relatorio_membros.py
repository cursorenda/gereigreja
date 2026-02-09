"""
Script para gerar relatório de membros ativos/inativos
Uso: python relatorio_membros.py [--formato csv|json|txt]
"""

import os
import sys
import django
from datetime import datetime
import json
import csv
from pathlib import Path

# Adicionar o diretório raiz ao path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from secretaria.models import Pessoa

class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'

def obter_estatisticas():
    """Obtém estatísticas gerais"""
    total = Pessoa.objects.count()
    ativos = Pessoa.objects.filter(status_pessoa__nome='Ativo').count()
    inativos = total - ativos
    
    # Por sexo
    masculino = Pessoa.objects.filter(status_pessoa__nome='Ativo', genero='M').count()
    feminino = Pessoa.objects.filter(status_pessoa__nome='Ativo', genero='F').count()
    
    # Por faixa etária
    from django.db.models import Count, Q
    from django.utils import timezone
    hoje = timezone.now().date()
    
    criancas = Pessoa.objects.filter(
        status_pessoa__nome='Ativo',
        nascimento__gte=hoje.replace(year=hoje.year-12)
    ).count()
    
    jovens = Pessoa.objects.filter(
        status_pessoa__nome='Ativo',
        nascimento__gte=hoje.replace(year=hoje.year-30),
        nascimento__lt=hoje.replace(year=hoje.year-12)
    ).count()
    
    adultos = Pessoa.objects.filter(
        status_pessoa__nome='Ativo',
        nascimento__lt=hoje.replace(year=hoje.year-30),
        nascimento__gte=hoje.replace(year=hoje.year-60)
    ).count()
    
    idosos = Pessoa.objects.filter(
        status_pessoa__nome='Ativo',
        nascimento__lt=hoje.replace(year=hoje.year-60)
    ).count()
    
    return {
        'total': total,
        'ativos': ativos,
        'inativos': inativos,
        'masculino': masculino,
        'feminino': feminino,
        'criancas': criancas,
        'jovens': jovens,
        'adultos': adultos,
        'idosos': idosos
    }

def formato_texto(stats):
    """Gera relatório em texto"""
    print(f"\n{Colors.BLUE}{'='*50}{Colors.NC}")
    print(f"{Colors.BLUE}RELATÓRIO DE MEMBROS - {datetime.now().strftime('%d/%m/%Y %H:%M')}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}\n")
    
    print(f"📊 GERAL")
    print(f"   Total de membros:    {stats['total']}")
    print(f"   {Colors.GREEN}✅ Ativos:{Colors.NC}    {stats['ativos']} ({stats['ativos']/stats['total']*100:.1f}%)")
    print(f"   {Colors.YELLOW}⏸️  Inativos:{Colors.NC}  {stats['inativos']} ({stats['inativos']/stats['total']*100:.1f}%)")
    
    print(f"\n👥 POR SEXO (Ativos)")
    print(f"   Masculino: {stats['masculino']}")
    print(f"   Feminino:  {stats['feminino']}")
    
    print(f"\n📆 POR FAIXA ETÁRIA (Ativos)")
    print(f"   Crianças (0-12):   {stats['criancas']}")
    print(f"   Jovens (13-30):    {stats['jovens']}")
    print(f"   Adultos (31-60):   {stats['adultos']}")
    print(f"   Idosos (60+):      {stats['idosos']}")
    
    print(f"\n{Colors.BLUE}{'='*50}{Colors.NC}\n")

def formato_csv(stats):
    """Gera relatório em CSV"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo = f'relatorio_membros_{timestamp}.csv'
    
    with open(arquivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Métrica', 'Valor', 'Percentual'])
        writer.writerow(['Total de Membros', stats['total'], '100%'])
        writer.writerow(['Ativos', stats['ativos'], f"{stats['ativos']/stats['total']*100:.1f}%"])
        writer.writerow(['Inativos', stats['inativos'], f"{stats['inativos']/stats['total']*100:.1f}%"])
        writer.writerow(['', '', ''])
        writer.writerow(['Sexo (Ativos)', '', ''])
        writer.writerow(['Masculino', stats['masculino'], ''])
        writer.writerow(['Feminino', stats['feminino'], ''])
        writer.writerow(['', '', ''])
        writer.writerow(['Faixa Etária (Ativos)', '', ''])
        writer.writerow(['Crianças (0-12)', stats['criancas'], ''])
        writer.writerow(['Jovens (13-30)', stats['jovens'], ''])
        writer.writerow(['Adultos (31-60)', stats['adultos'], ''])
        writer.writerow(['Idosos (60+)', stats['idosos'], ''])
    
    print(f"{Colors.GREEN}✅ Relatório salvo: {arquivo}{Colors.NC}")

def formato_json(stats):
    """Gera relatório em JSON"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo = f'relatorio_membros_{timestamp}.json'
    
    dados = {
        'timestamp': datetime.now().isoformat(),
        'geral': {
            'total': stats['total'],
            'ativos': stats['ativos'],
            'inativos': stats['inativos']
        },
        'por_sexo': {
            'masculino': stats['masculino'],
            'feminino': stats['feminino']
        },
        'por_faixa_etaria': {
            'criancas_0_12': stats['criancas'],
            'jovens_13_30': stats['jovens'],
            'adultos_31_60': stats['adultos'],
            'idosos_60_mais': stats['idosos']
        }
    }
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    print(f"{Colors.GREEN}✅ Relatório salvo: {arquivo}{Colors.NC}")

def main():
    """Função principal"""
    formato = 'txt'
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--formato', '-f'] and len(sys.argv) > 2:
            formato = sys.argv[2]
        elif sys.argv[1] in ['csv', 'json', 'txt']:
            formato = sys.argv[1]
    
    print(f"Carregando dados...")
    stats = obter_estatisticas()
    
    if formato == 'csv':
        formato_csv(stats)
    elif formato == 'json':
        formato_json(stats)
    else:
        formato_texto(stats)

if __name__ == '__main__':
    main()
