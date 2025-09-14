
from django.core.management.base import BaseCommand
from datetime import datetime
from secretaria.models import Membro, TimelineEvent, StatusHistorico
from django.db import transaction
from django.utils import timezone

class Command(BaseCommand):
    help = 'Importa eventos históricos dos membros para TimelineEvent.'

    def handle(self, *args, **options):
        total = 0
        with transaction.atomic():

            # Data de entrada dos membros
            for membro in Membro.objects.exclude(data_entrada=None):
                # Converter para datetime com timezone se necessário
                data_entrada = membro.data_entrada
                if data_entrada and not hasattr(data_entrada, 'tzinfo'):
                    data_entrada = timezone.make_aware(
                        datetime.combine(data_entrada, datetime.min.time()), timezone.get_current_timezone()
                    )
                if not TimelineEvent.objects.filter(membro=membro, tipo_evento='entrada', data=data_entrada).exists():
                    TimelineEvent.objects.create(
                        membro=membro,
                        data=data_entrada,
                        tipo_evento='entrada',
                        descricao='Entrada do membro no sistema.'
                    )
                    total += 1

            # Históricos de status
            for hist in StatusHistorico.objects.select_related('membro').all():
                data_transicao = hist.data_transicao
                if data_transicao and timezone.is_naive(data_transicao):
                    data_transicao = timezone.make_aware(data_transicao, timezone.get_current_timezone())
                if not TimelineEvent.objects.filter(membro=hist.membro, tipo_evento='mudanca_status', data=data_transicao).exists():
                    TimelineEvent.objects.create(
                        membro=hist.membro,
                        data=data_transicao,
                        tipo_evento='mudanca_status',
                        descricao=f"Mudança de status: {hist.status_pessoa_anterior} → {hist.status_pessoa_novo}"
                    )
                    total += 1

            # (Opcional) Adicione aqui lógica para históricos de tipo, se houver modelo equivalente

        self.stdout.write(self.style.SUCCESS(f'Importação concluída. {total} eventos criados.'))
