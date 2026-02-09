"""
Script para gerar lista de aniversariantes do mês
Uso: python aniversariantes.py [--mes MM]
"""

import os
import sys
import django
from datetime import datetime
from calendar import monthrange
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
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'

MESES = [
    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

def obter_aniversariantes(mes):
    """Obtém aniversariantes do mês ordenados por dia"""
    membros = Pessoa.objects.filter(
        status_pessoa__nome='Ativo',
        nascimento__month=mes
    ).order_by('nascimento__day', 'nome')
    
    return list(membros)

def calcular_idade(nascimento):
    """Calcula idade em anos"""
    hoje = datetime.now().date()
    idade = hoje.year - nascimento.year
    if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
        idade -= 1
    return idade

def imprimir_aniversariantes(mes, membros):
    """Imprime lista de aniversariantes"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}🎂 ANIVERSARIANTES DE {MESES[mes].upper()} - {datetime.now().year}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    if not membros:
        print(f"{Colors.MAGENTA}Nenhum aniversariante encontrado para este mês.{Colors.NC}\n")
        return
    
    # Agrupar por dia
    por_dia = {}
    for membro in membros:
        dia = membro.nascimento.day
        if dia not in por_dia:
            por_dia[dia] = []
        por_dia[dia].append(membro)
    
    # Imprimir agrupado por dia
    for dia in sorted(por_dia.keys()):
        membros_do_dia = por_dia[dia]
        print(f"{Colors.GREEN}📅 Dia {dia:02d}/{mes:02d}{Colors.NC}")
        
        for membro in membros_do_dia:
            idade = calcular_idade(membro.nascimento)
            telefone = membro.telefone or 'Sem telefone'
            print(f"   • {membro.nome} - {idade} anos ({telefone})")
        
        print()  # Linha em branco entre dias
    
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.GREEN}Total: {len(membros)} aniversariante(s){Colors.NC}\n")

def gerar_whatsapp_message(mes, membros):
    """Gera mensagem formatada para WhatsApp"""
    if not membros:
        return
    
    print(f"\n{Colors.MAGENTA}📱 MENSAGEM PARA WHATSAPP:{Colors.NC}\n")
    print("─" * 50)
    
    mensagem = f"🎂 *ANIVERSARIANTES DE {MESES[mes].upper()}* 🎂\n\n"
    
    por_dia = {}
    for membro in membros:
        dia = membro.nascimento.day
        if dia not in por_dia:
            por_dia[dia] = []
        por_dia[dia].append(membro)
    
    for dia in sorted(por_dia.keys()):
        membros_do_dia = por_dia[dia]
        mensagem += f"📅 *Dia {dia:02d}/{mes:02d}*\n"
        
        for membro in membros_do_dia:
            idade = calcular_idade(membro.nascimento)
            mensagem += f"   • {membro.nome} - {idade} anos\n"
        
        mensagem += "\n"
    
    mensagem += "🎉 Parabéns a todos! Que Deus abençoe muito suas vidas!"
    
    print(mensagem)
    print("─" * 50)
    print("\n💡 Copie a mensagem acima e cole no WhatsApp\n")

def main():
    """Função principal"""
    # Determinar o mês
    mes_atual = datetime.now().month
    mes = mes_atual
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--mes', '-m'] and len(sys.argv) > 2:
            try:
                mes = int(sys.argv[2])
                if mes < 1 or mes > 12:
                    print(f"{Colors.RED}❌ Mês inválido. Use valores entre 1 e 12.{Colors.NC}")
                    sys.exit(1)
            except ValueError:
                print(f"{Colors.RED}❌ Mês deve ser um número entre 1 e 12.{Colors.NC}")
                sys.exit(1)
    
    # Obter aniversariantes
    print(f"Carregando aniversariantes...")
    membros = obter_aniversariantes(mes)
    
    # Imprimir
    imprimir_aniversariantes(mes, membros)
    
    # Gerar mensagem WhatsApp se tiver aniversariantes
    if membros and len(sys.argv) > 1 and '--whatsapp' in sys.argv:
        gerar_whatsapp_message(mes, membros)

if __name__ == '__main__':
    main()
