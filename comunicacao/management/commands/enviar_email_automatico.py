from django.core.management.base import BaseCommand

from comunicacao.models import AutomacaoAniversariantes
from comunicacao.services import executar_automacao_aniversario_email


class Command(BaseCommand):
    help = 'Envia e-mails automaticos da Comunicacao (aniversariantes).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            default='aniversariantes',
            choices=['aniversariantes'],
            help='Tipo de automacao a executar.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Executa novamente mesmo se a automacao ja tiver rodado hoje.',
        )

    def handle(self, *args, **options):
        enviados = 0
        falhas = 0

        for automacao in AutomacaoAniversariantes.objects.filter(email_ativo=True).select_related('ministerio'):
            resumo = executar_automacao_aniversario_email(
                ministerio=automacao.ministerio,
                force=options['force'],
            )
            if resumo.get('ignorado'):
                continue
            enviados += resumo['enviados']
            falhas += resumo['falhas']

        self.stdout.write(self.style.SUCCESS(f'Envios com sucesso: {enviados}'))
        if falhas:
            self.stdout.write(self.style.WARNING(f'Falhas de envio: {falhas}'))