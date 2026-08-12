from django.core.management.base import BaseCommand

from financeiro.services import DepartamentoFinanceiroService


class Command(BaseCommand):
    help = 'Gera ou sincroniza departamentos financeiros padrao por igreja.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--igreja-id',
            action='append',
            type=int,
            dest='igreja_ids',
            help='ID da igreja a processar. Pode repetir o argumento para varias igrejas.',
        )

    def handle(self, *args, **options):
        igreja_ids = options.get('igreja_ids') or None

        resumo = DepartamentoFinanceiroService.sincronizar_departamentos_padrao(igreja_ids=igreja_ids)

        self.stdout.write(
            self.style.SUCCESS(
                'Sincronizacao concluida: '
                f"igrejas={resumo['igrejas_processadas']}, "
                f"departamentos_criados={resumo['departamentos_criados']}, "
                f"departamentos_atualizados={resumo['departamentos_atualizados']}, "
                f"politicas_criadas={resumo['politicas_criadas']}"
            )
        )
