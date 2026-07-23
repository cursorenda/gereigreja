from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Executa as automacoes diarias de Comunicacao para aniversariantes.'

    def handle(self, *args, **options):
        call_command('enviar_whatsapp_automatico', tipo='aniversariantes')
        call_command('enviar_email_automatico', tipo='aniversariantes')
        call_command('processar_whatsapp_agendados')
        self.stdout.write(self.style.SUCCESS('Automacoes diarias de Comunicacao executadas.'))