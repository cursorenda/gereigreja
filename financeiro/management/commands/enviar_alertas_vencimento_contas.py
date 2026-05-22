from django.core.management.base import BaseCommand, CommandError

from financeiro.services import AlertaVencimentoContaPagarService


class Command(BaseCommand):
    help = 'Envia alertas de contas a pagar (D-7, D-3, D-1 e vencidas).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias-alerta',
            nargs='*',
            type=int,
            default=[7, 3, 1],
            help='Dias para alerta de vencimento. Exemplo: --dias-alerta 7 3 1',
        )
        parser.add_argument(
            '--sem-vencidas',
            action='store_true',
            help='Nao envia alertas de contas vencidas.',
        )
        parser.add_argument(
            '--ministerio-id',
            type=int,
            help='Filtra envio por Ministerio (opcional).',
        )
        parser.add_argument(
            '--igreja-id',
            type=int,
            help='Filtra envio por Igreja (opcional).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa simulacao sem gravar notificacoes.',
        )

    def handle(self, *args, **options):
        dias_alerta = options.get('dias_alerta') or [7, 3, 1]
        if any(dia < 0 for dia in dias_alerta):
            raise CommandError('Os dias de alerta devem ser inteiros nao negativos.')

        service = AlertaVencimentoContaPagarService()
        resultado = service.enviar_alertas(
            dias_alerta=tuple(dias_alerta),
            incluir_vencidas=not options.get('sem_vencidas', False),
            ministerio_id=options.get('ministerio_id'),
            igreja_id=options.get('igreja_id'),
            dry_run=options.get('dry_run', False),
        )

        self.stdout.write(self.style.NOTICE(f"Dry run: {'sim' if resultado['dry_run'] else 'nao'}"))
        self.stdout.write(self.style.NOTICE(f"Dias de alerta: {', '.join(str(d) for d in resultado['dias_alerta'])}"))
        self.stdout.write(self.style.NOTICE(f"Incluir vencidas: {'sim' if resultado['incluir_vencidas'] else 'nao'}"))
        self.stdout.write(self.style.SUCCESS(f"Contas avaliadas: {resultado['total_contas_avaliadas']}"))
        self.stdout.write(self.style.SUCCESS(f"Notificacoes criadas: {resultado['total_notificacoes_criadas']}"))
        self.stdout.write(self.style.WARNING(f"Notificacoes ja existentes: {resultado['total_notificacoes_existentes']}"))
        self.stdout.write(self.style.WARNING(f"Contas fora da regra de alerta: {resultado['total_contas_fora_regra']}"))
        self.stdout.write(self.style.WARNING(f"Contas sem destinatario: {resultado['total_contas_sem_destinatario']}"))

        if resultado['total_erros']:
            self.stdout.write(self.style.ERROR(f"Erros: {resultado['total_erros']}"))
            for erro in resultado['erros']:
                self.stdout.write(self.style.ERROR(f" - {erro}"))
