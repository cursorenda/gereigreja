from datetime import date

from django.core.management.base import BaseCommand

from comunicacao.models import WhatsAppConfiguracao
from comunicacao.services_whatsapp import send_whatsapp_text, WhatsAppSendError
from secretaria.models import Pessoa
from eventos.models import Evento


class Command(BaseCommand):
    help = 'Envia mensagens automaticas de WhatsApp (MVP: aniversariantes).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            default='aniversariantes',
            choices=['aniversariantes', 'lembrete_eventos'],
            help='Tipo de automacao a executar.',
        )

    def handle(self, *args, **options):
        tipo = options['tipo']
        if tipo == 'aniversariantes':
            self.enviar_aniversariantes()
        elif tipo == 'lembrete_eventos':
            self.enviar_lembrete_eventos()

    def enviar_aniversariantes(self):
        hoje = date.today()
        enviados = 0
        falhas = 0

        configs = WhatsAppConfiguracao.objects.filter(ativo=True, auto_aniversariantes=True).select_related('igreja', 'ministerio')

        for config in configs:
            pessoas = Pessoa.objects.filter(
                igreja=config.igreja,
                nascimento__month=hoje.month,
                nascimento__day=hoje.day,
            ).exclude(celular__isnull=True).exclude(celular='')

            for pessoa in pessoas:
                texto = f'Feliz aniversario, {pessoa.nome}! Que Deus abencoe sua vida de forma abundante.'
                try:
                    send_whatsapp_text(
                        config,
                        pessoa.celular,
                        texto,
                        tipo='aniversario',
                        ministerio=config.ministerio,
                        igreja=config.igreja,
                        membro=pessoa,
                    )
                    enviados += 1
                except WhatsAppSendError:
                    falhas += 1

        self.stdout.write(self.style.SUCCESS(f'Envios com sucesso: {enviados}'))
        if falhas:
            self.stdout.write(self.style.WARNING(f'Falhas de envio: {falhas}'))

    def enviar_lembrete_eventos(self):
        hoje = date.today()
        enviados = 0
        falhas = 0

        configs = WhatsAppConfiguracao.objects.filter(ativo=True, auto_lembrete_eventos=True).select_related('igreja', 'ministerio')

        for config in configs:
            eventos = Evento.objects.filter(igreja=config.igreja, data_inicio__date=hoje).order_by('data_inicio')
            if not eventos.exists():
                continue

            pessoas = Pessoa.objects.filter(igreja=config.igreja).exclude(celular__isnull=True).exclude(celular='')
            for pessoa in pessoas:
                for evento in eventos:
                    texto = (
                        f"Lembrete: hoje teremos '{evento.titulo}' as "
                        f"{evento.data_inicio.strftime('%H:%M')} na {config.igreja.nome_igreja}."
                    )
                    try:
                        send_whatsapp_text(
                            config,
                            pessoa.celular,
                            texto,
                            tipo='evento',
                            ministerio=config.ministerio,
                            igreja=config.igreja,
                            membro=pessoa,
                        )
                        enviados += 1
                    except WhatsAppSendError:
                        falhas += 1

        self.stdout.write(self.style.SUCCESS(f'Envios com sucesso: {enviados}'))
        if falhas:
            self.stdout.write(self.style.WARNING(f'Falhas de envio: {falhas}'))
