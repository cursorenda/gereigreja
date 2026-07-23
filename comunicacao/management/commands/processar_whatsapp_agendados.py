from django.core.management.base import BaseCommand

from comunicacao.models import WhatsAppMensagemAgendada
from comunicacao.services import processar_whatsapp_agendados


class Command(BaseCommand):
    help = 'Processa mensagens WhatsApp agendadas e envia as que ja venceram.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Tenta reenviar mensagens mesmo se houver inconsistencias leves de estado.',
        )

    def handle(self, *args, **options):
        pendentes = WhatsAppMensagemAgendada.objects.filter(status='pendente').count()
        resumo = processar_whatsapp_agendados(force=options['force'])

        self.stdout.write(self.style.SUCCESS(f'Mensagens pendentes encontradas: {pendentes}'))
        self.stdout.write(self.style.SUCCESS(f'Envios com sucesso: {resumo["enviados"]}'))
        if resumo['ignorados']:
            self.stdout.write(self.style.WARNING(f'Ignorados: {resumo["ignorados"]}'))
        if resumo['falhas']:
            self.stdout.write(self.style.WARNING(f'Falhas de envio: {resumo["falhas"]}'))