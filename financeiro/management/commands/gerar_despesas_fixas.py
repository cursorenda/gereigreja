from django.core.management.base import BaseCommand, CommandError

from financeiro.services import RecorrenciaContaPagarService


class Command(BaseCommand):
    help = 'Gera contas a pagar a partir das recorrencias de despesas fixas.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--competencia',
            type=str,
            help='Competencia no formato AAAA-MM. Exemplo: 2026-05',
        )
        parser.add_argument(
            '--ministerio-id',
            type=int,
            help='Filtra a geracao por Ministerio (opcional).',
        )
        parser.add_argument(
            '--igreja-id',
            type=int,
            help='Filtra a geracao por Igreja (opcional).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa simulacao sem gravar no banco.',
        )

    def handle(self, *args, **options):
        service = RecorrenciaContaPagarService()

        try:
            resultado = service.gerar_competencia(
                competencia=options.get('competencia'),
                ministerio_id=options.get('ministerio_id'),
                igreja_id=options.get('igreja_id'),
                dry_run=options.get('dry_run', False),
            )
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.NOTICE(f"Competencia: {resultado['competencia']}"))
        self.stdout.write(self.style.NOTICE(f"Dry run: {'sim' if resultado['dry_run'] else 'nao'}"))
        self.stdout.write(self.style.SUCCESS(f"Recorrencias avaliadas: {resultado['total_avaliadas']}"))
        self.stdout.write(self.style.SUCCESS(f"Contas geradas: {resultado['total_geradas']}"))
        self.stdout.write(self.style.WARNING(f"Ja existentes: {resultado['total_existentes']}"))
        self.stdout.write(self.style.WARNING(f"Ignoradas por janela/condicao: {resultado['total_ignoradas']}"))

        if resultado['total_erros']:
            self.stdout.write(self.style.ERROR(f"Erros: {resultado['total_erros']}"))
            for erro in resultado['erros']:
                self.stdout.write(self.style.ERROR(f" - {erro}"))
