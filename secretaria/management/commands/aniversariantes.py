"""
Comando Django para listar aniversariantes do mês
Uso: python manage.py aniversariantes [--mes MM] [--whatsapp]
"""

from django.core.management.base import BaseCommand
from secretaria.models import Pessoa
from datetime import datetime


class Command(BaseCommand):
    help = 'Lista aniversariantes do mês'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mes',
            type=int,
            default=datetime.now().month,
            help='Mês (1-12)'
        )
        parser.add_argument(
            '--whatsapp',
            action='store_true',
            help='Gerar mensagem para WhatsApp'
        )

    def handle(self, *args, **options):
        mes = options['mes']
        whatsapp = options['whatsapp']
        
        if mes < 1 or mes > 12:
            self.stdout.write(self.style.ERROR('❌ Mês inválido. Use valores entre 1 e 12.'))
            return
        
        self.stdout.write('Carregando aniversariantes...')
        membros = self.obter_aniversariantes(mes)
        
        self.imprimir_aniversariantes(mes, membros)
        
        if whatsapp and membros:
            self.gerar_whatsapp_message(mes, membros)

    def obter_aniversariantes(self, mes):
        """Obtém aniversariantes do mês ordenados por dia"""
        membros = Pessoa.objects.filter(
            status_pessoa__nome='Ativo',
            nascimento__month=mes
        ).order_by('nascimento__day', 'nome')
        
        return list(membros)

    def calcular_idade(self, nascimento):
        """Calcula idade em anos"""
        hoje = datetime.now().date()
        idade = hoje.year - nascimento.year
        if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
            idade -= 1
        return idade

    def imprimir_aniversariantes(self, mes, membros):
        """Imprime lista de aniversariantes"""
        MESES = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(f"🎂 ANIVERSARIANTES DE {MESES[mes].upper()} - {datetime.now().year}")
        self.stdout.write("="*60 + "\n")
        
        if not membros:
            self.stdout.write(self.style.WARNING('Nenhum aniversariante encontrado para este mês.\n'))
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
            self.stdout.write(self.style.SUCCESS(f"📅 Dia {dia:02d}/{mes:02d}"))
            
            for membro in membros_do_dia:
                idade = self.calcular_idade(membro.nascimento)
                telefone = membro.telefone or 'Sem telefone'
                self.stdout.write(f"   • {membro.nome} - {idade} anos ({telefone})")
            
            self.stdout.write('')  # Linha em branco entre dias
        
        self.stdout.write("="*60)
        self.stdout.write(self.style.SUCCESS(f"Total: {len(membros)} aniversariante(s)\n"))

    def gerar_whatsapp_message(self, mes, membros):
        """Gera mensagem formatada para WhatsApp"""
        MESES = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        
        self.stdout.write("\n" + self.style.WARNING("📱 MENSAGEM PARA WHATSAPP:\n"))
        self.stdout.write("─" * 50)
        
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
                idade = self.calcular_idade(membro.nascimento)
                mensagem += f"   • {membro.nome} - {idade} anos\n"
            
            mensagem += "\n"
        
        mensagem += "🎉 Parabéns a todos! Que Deus abençoe muito suas vidas!"
        
        self.stdout.write(mensagem)
        self.stdout.write("─" * 50)
        self.stdout.write("\n💡 Copie a mensagem acima e cole no WhatsApp\n")
