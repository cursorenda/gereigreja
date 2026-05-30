from types import SimpleNamespace

from django.core.management.base import BaseCommand

from configuracao.models import ConfiguracaoSistema, Igreja
from escola_biblica.views import auto_sync_ebd_periodos_e_licoes


class Command(BaseCommand):
    help = 'Sincroniza automaticamente os calendarios e licoes da EBD para os ministerios configurados.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ministerio-id',
            type=int,
            dest='ministerio_id',
            help='Sincroniza apenas o ministerio informado.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='Forca a sincronizacao mesmo se ela ja tiver sido executada no dia.',
        )

    def handle(self, *args, **options):
        ministerio_id = options.get('ministerio_id')
        force = options.get('force', True)

        configs = ConfiguracaoSistema.objects.select_related('ministerio').all().order_by('ministerio__nome_fantasia')
        if ministerio_id:
            configs = configs.filter(ministerio_id=ministerio_id)

        total_configs = configs.count()
        if total_configs == 0:
            self.stdout.write(self.style.WARNING('Nenhuma configuracao EBD encontrada para sincronizar.'))
            return

        self.stdout.write(f'Iniciando sincronizacao EBD para {total_configs} configuracao(oes)...')
        total_processadas = 0

        for config in configs:
            request = self._build_fake_request(config.ministerio)
            auto_sync_ebd_periodos_e_licoes(request, force=force)
            total_processadas += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sincronizado ministerio {config.ministerio_id} ({config.ministerio.nome_fantasia})."
                )
            )

        self.stdout.write(self.style.SUCCESS(f'Sincronizacao EBD concluida para {total_processadas} configuracao(oes).'))

    def _build_fake_request(self, ministerio):
        user = SimpleNamespace(
            is_authenticated=True,
            is_superuser=True,
            pk=getattr(ministerio, 'pk', None),
            perfil=SimpleNamespace(ministerio=ministerio),
            perfil_usuario=SimpleNamespace(ministerio=ministerio),
        )
        return SimpleNamespace(
            user=user,
            session={},
            igrejas_permitidas=Igreja.objects.filter(ministerio=ministerio),
            igreja_ativa=None,
        )
