"""
Script para gerar relatório financeiro mensal
Uso: python relatorio_financeiro.py [--mes MM] [--ano YYYY]
"""

import os
import sys
import django
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Adicionar o diretório raiz ao path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from financeiro.models import Receitas, Despesas

class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'

MESES = [
    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

def gerar_relatorio(mes, ano):
    """Gera relatório financeiro do mês"""
    
    # Obter dados
    receitas = Receitas.objects.filter(
        data__month=mes,
        data__year=ano
    )
    
    despesas = Despesas.objects.filter(
        data__month=mes,
        data__year=ano
    )
    
    # Calcular totais
    total_receitas = sum(r.valor for r in receitas) or Decimal('0.00')
    total_despesas = sum(d.valor for d in despesas) or Decimal('0.00')
    saldo = total_receitas - total_despesas
    
    # Cabeçalho
    print(f"\n{Colors.BLUE}{'='*70}{Colors.NC}")
    print(f"{Colors.BLUE}💰 RELATÓRIO FINANCEIRO - {MESES[mes].upper()}/{ano}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*70}{Colors.NC}\n")
    
    # Resumo
    print(f"{Colors.GREEN}📈 RECEITAS{Colors.NC}")
    print(f"   Total: R$ {total_receitas:,.2f}")
    print(f"   Quantidade: {receitas.count()} lançamento(s)\n")
    
    print(f"{Colors.RED}📉 DESPESAS{Colors.NC}")
    print(f"   Total: R$ {total_despesas:,.2f}")
    print(f"   Quantidade: {despesas.count()} lançamento(s)\n")
    
    # Saldo
    saldo_cor = Colors.GREEN if saldo >= 0 else Colors.RED
    saldo_emoji = "✅" if saldo >= 0 else "⚠️"
    print(f"{saldo_cor}{saldo_emoji} SALDO: R$ {saldo:,.2f}{Colors.NC}\n")
    
    # Detalhamento por categoria
    print(f"{Colors.BLUE}📊 POR CATEGORIA{Colors.NC}\n")
    
    # Receitas por categoria
    from django.db.models import Sum
    receitas_cat = receitas.values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')
    
    if receitas_cat:
        print(f"{Colors.GREEN}Receitas:{Colors.NC}")
        for cat in receitas_cat:
            nome = cat['categoria__nome'] or 'Sem categoria'
            valor = cat['total']
            percentual = (valor / total_receitas * 100) if total_receitas > 0 else 0
            print(f"   • {nome:<30} R$ {valor:>10,.2f} ({percentual:>5.1f}%)")
        print()
    
    # Despesas por categoria
    despesas_cat = despesas.values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')
    
    if despesas_cat:
        print(f"{Colors.RED}Despesas:{Colors.NC}")
        for cat in despesas_cat:
            nome = cat['categoria__nome'] or 'Sem categoria'
            valor = cat['total']
            percentual = (valor / total_despesas * 100) if total_despesas > 0 else 0
            print(f"   • {nome:<30} R$ {valor:>10,.2f} ({percentual:>5.1f}%)")
        print()
    
    # Análise
    print(f"{Colors.BLUE}{'='*70}{Colors.NC}")
    print(f"{Colors.YELLOW}📋 ANÁLISE{Colors.NC}\n")
    
    if total_receitas > 0:
        despesas_percentual = (total_despesas / total_receitas * 100)
        print(f"   Despesas representam {despesas_percentual:.1f}% das receitas")
    
    if saldo < 0:
        print(f"   {Colors.RED}⚠️  ATENÇÃO: Déficit de R$ {abs(saldo):,.2f}{Colors.NC}")
    elif saldo == 0:
        print(f"   {Colors.YELLOW}⚠️  Receitas e despesas equilibradas{Colors.NC}")
    else:
        print(f"   {Colors.GREEN}✅ Superávit de R$ {saldo:,.2f}{Colors.NC}")
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.NC}\n")
    
    return {
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'saldo': saldo
    }

def main():
    """Função principal"""
    # Determinar mês e ano
    hoje = datetime.now()
    mes = hoje.month
    ano = hoje.year
    
    # Parse argumentos
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] in ['--mes', '-m'] and i + 1 < len(sys.argv):
            try:
                mes = int(sys.argv[i + 1])
                if mes < 1 or mes > 12:
                    print(f"{Colors.RED}❌ Mês inválido. Use valores entre 1 e 12.{Colors.NC}")
                    sys.exit(1)
                i += 2
            except ValueError:
                print(f"{Colors.RED}❌ Mês deve ser um número.{Colors.NC}")
                sys.exit(1)
        elif sys.argv[i] in ['--ano', '-a'] and i + 1 < len(sys.argv):
            try:
                ano = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print(f"{Colors.RED}❌ Ano deve ser um número.{Colors.NC}")
                sys.exit(1)
        else:
            i += 1
    
    # Gerar relatório
    print(f"Carregando dados financeiros...")
    gerar_relatorio(mes, ano)

if __name__ == '__main__':
    main()
