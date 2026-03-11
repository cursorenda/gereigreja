from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, time
import holidays
from agenda.models import AgendaEvento
from configuracao.models import Igreja


class Command(BaseCommand):
    help = 'Importa feriados nacionais brasileiros para a agenda'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ano',
            type=int,
            default=datetime.now().year,
            help='Ano para importar feriados (padrão: ano atual)'
        )
        parser.add_argument(
            '--estado',
            type=str,
            default=None,
            help='Sigla do estado para feriados estaduais (ex: SP, RJ, MG)'
        )
        parser.add_argument(
            '--igreja-id',
            type=int,
            default=None,
            help='ID da igreja para associar os feriados'
        )

    def handle(self, *args, **options):
        ano = options['ano']
        estado = options['estado']
        igreja_id = options['igreja_id']

        self.stdout.write(f'Importando feriados brasileiros de {ano}...')

        # Buscar igreja
        igreja = None
        if igreja_id:
            try:
                igreja = Igreja.objects.get(id=igreja_id)
                self.stdout.write(f'Igreja encontrada: {igreja.nome_igreja}')
            except Igreja.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Igreja com ID {igreja_id} não encontrada'))
                return
        else:
            # Se não especificou igreja, pegar a primeira disponível
            igreja = Igreja.objects.first()
            if not igreja:
                self.stdout.write(self.style.ERROR('Nenhuma igreja cadastrada no sistema'))
                return
            self.stdout.write(f'Usando igreja padrão: {igreja.nome_igreja}')

        # Obter feriados brasileiros
        if estado:
            br_holidays = holidays.Brazil(state=estado.upper(), years=ano)
            self.stdout.write(f'Buscando feriados nacionais e do estado {estado.upper()}')
        else:
            br_holidays = holidays.Brazil(years=ano)
            self.stdout.write('Buscando apenas feriados nacionais')

        eventos_criados = 0
        eventos_existentes = 0

        for data, nome in sorted(br_holidays.items()):
            # Verificar se já existe evento de feriado nesta data para esta igreja
            if AgendaEvento.objects.filter(
                igreja=igreja,
                tipo='feriado',
                data_inicio__date=data
            ).exists():
                eventos_existentes += 1
                self.stdout.write(f'  ⏭️  {data.strftime("%d/%m/%Y")} - {nome} (já existe)')
                continue

            # Criar evento de feriado
            data_inicio = timezone.make_aware(datetime.combine(data, time(0, 0)))
            data_fim = timezone.make_aware(datetime.combine(data, time(23, 59)))

            evento = AgendaEvento.objects.create(
                titulo=nome,
                tipo='feriado',
                data_inicio=data_inicio,
                data_fim=data_fim,
                igreja=igreja,
                descricao=f'Feriado nacional importado automaticamente'
            )
            eventos_criados += 1
            self.stdout.write(self.style.SUCCESS(f'  ✅ {data.strftime("%d/%m/%Y")} - {nome}'))

        self.stdout.write()
        self.stdout.write(self.style.SUCCESS(f'✨ Importação concluída!'))
        self.stdout.write(f'   📅 Eventos criados: {eventos_criados}')
        self.stdout.write(f'   ⏭️  Eventos já existentes: {eventos_existentes}')
        self.stdout.write(f'   📊 Total de feriados: {eventos_criados + eventos_existentes}')
