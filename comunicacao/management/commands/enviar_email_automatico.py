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
        neutralizados_demo = 0
        nao_enviados = 0
        falhas = 0

        for automacao in AutomacaoAniversariantes.objects.filter(email_ativo=True).select_related('ministerio'):
            resumo = executar_automacao_aniversario_email(
                ministerio=automacao.ministerio,
                force=options['force'],
            )
            if resumo.get('ignorado'):
                continue
            enviados += resumo['enviados']
            neutralizados_demo += resumo['neutralizados_demo']
            nao_enviados += resumo['nao_enviados']
            falhas += resumo['falhas']

        self.stdout.write(self.style.SUCCESS(f'Enviados externamente: {enviados}'))
        if neutralizados_demo:
            self.stdout.write(self.style.WARNING(f'Neutralizados em Demo: {neutralizados_demo}'))
        if nao_enviados:
            self.stdout.write(self.style.WARNING(f'Não enviados: {nao_enviados}'))
        if falhas:
            self.stdout.write(self.style.WARNING(f'Falhas de envio: {falhas}'))