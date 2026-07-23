from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Executa todas as automacoes diarias de WhatsApp em uma unica rotina.'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando rotina diaria de WhatsApp...')
        call_command('enviar_whatsapp_automatico', tipo='aniversariantes')
        call_command('enviar_whatsapp_automatico', tipo='novos_membros')
        call_command('enviar_whatsapp_automatico', tipo='followup_visitantes')
        call_command('enviar_whatsapp_automatico', tipo='lembrete_eventos')
        call_command('processar_whatsapp_agendados')
        self.stdout.write(self.style.SUCCESS('Rotina diaria de WhatsApp concluida.'))
