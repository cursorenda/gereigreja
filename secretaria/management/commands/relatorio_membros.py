"""
Comando Django para gerar relatório de membros
Uso: python manage.py relatorio_membros [--formato csv|json|txt]
"""

from django.core.management.base import BaseCommand
from secretaria.models import Pessoa
from datetime import datetime
from decimal import Decimal
import csv
import json


class Command(BaseCommand):
    help = 'Gera relatório de membros ativos/inativos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--formato',
            type=str,
            default='txt',
            choices=['txt', 'csv', 'json'],
            help='Formato do relatório (txt, csv ou json)'
        )

    def handle(self, *args, **options):
        formato = options['formato']
        
        self.stdout.write('Carregando dados...')
        stats = self.obter_estatisticas()
        
        if formato == 'csv':
            self.formato_csv(stats)
        elif formato == 'json':
            self.formato_json(stats)
        else:
            self.formato_texto(stats)

    def obter_estatisticas(self):
        """Obtém estatísticas gerais"""
        total = Pessoa.objects.count()
        ativos = Pessoa.objects.filter(status_pessoa__nome='Ativo').count()
        inativos = total - ativos
        
        # Por sexo
        masculino = Pessoa.objects.filter(status_pessoa__nome='Ativo', genero='M').count()
        feminino = Pessoa.objects.filter(status_pessoa__nome='Ativo', genero='F').count()
        
        # Por faixa etária
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

    def formato_texto(self, stats):
        """Gera relatório em texto"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"RELATÓRIO DE MEMBROS - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        self.stdout.write("="*50 + "\n")
        
        self.stdout.write(f"📊 GERAL")
        self.stdout.write(f"   Total de membros:    {stats['total']}")
        self.stdout.write(self.style.SUCCESS(f"   ✅ Ativos:    {stats['ativos']} ({stats['ativos']/stats['total']*100:.1f}%)"))
        self.stdout.write(self.style.WARNING(f"   ⏸️  Inativos:  {stats['inativos']} ({stats['inativos']/stats['total']*100:.1f}%)"))
        
        self.stdout.write(f"\n👥 POR SEXO (Ativos)")
        self.stdout.write(f"   Masculino: {stats['masculino']}")
        self.stdout.write(f"   Feminino:  {stats['feminino']}")
        
        self.stdout.write(f"\n📆 POR FAIXA ETÁRIA (Ativos)")
        self.stdout.write(f"   Crianças (0-12):   {stats['criancas']}")
        self.stdout.write(f"   Jovens (13-30):    {stats['jovens']}")
        self.stdout.write(f"   Adultos (31-60):   {stats['adultos']}")
        self.stdout.write(f"   Idosos (60+):      {stats['idosos']}")
        
        self.stdout.write("\n" + "="*50 + "\n")

    def formato_csv(self, stats):
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
        
        self.stdout.write(self.style.SUCCESS(f"✅ Relatório salvo: {arquivo}"))

    def formato_json(self, stats):
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
        
        self.stdout.write(self.style.SUCCESS(f"✅ Relatório salvo: {arquivo}"))
