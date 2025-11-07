from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count
from secretaria.models import GrupoCasa


class Command(BaseCommand):
    help = (
        'Localiza grupos (GrupoCasa) com 0 moradores e opcionalmente os exclui. '
        'Por padrão faz um preview (lista). Use --confirm para executar. '
        'Use --force para também remover grupos que têm visitas associadas.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', help='Excluir os grupos listados (commit).')
        parser.add_argument('--force', action='store_true', help='Forçar exclusão mesmo se o grupo tiver visitas (cuidado).')
        parser.add_argument('--igreja', type=int, help='Filtrar por ID da igreja (opcional).')

    def handle(self, *args, **options):
        confirm = options.get('confirm')
        force = options.get('force')
        igreja_id = options.get('igreja')

        qs = GrupoCasa.objects.all()
        if igreja_id:
            qs = qs.filter(igreja_id=igreja_id)

        qs = qs.annotate(num_pessoas=Count('pessoas'), num_visitas=Count('visitas'))
        empty_qs = qs.filter(num_pessoas=0).order_by('igreja_id','rua','numero')

        total = empty_qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nenhum GrupoCasa com 0 moradores encontrado.'))
            return

        self.stdout.write(self.style.WARNING(f'Foram encontrados {total} GrupoCasa(s) com 0 moradores.'))
        self.stdout.write('Lista (id) - Igreja - Nome/Endereço - visitas')
        to_delete = []
        for g in empty_qs:
            label = f"{g.pk} - {getattr(g.igreja, 'id', g.igreja_id)} - {g.nome or (g.rua or '') + ' ' + (g.numero or '')} - visitas:{g.num_visitas}"
            self.stdout.write(label)
            # collect candidates; actual deletion will consider visitas and --force
            to_delete.append((g, g.num_visitas))

        if not confirm:
            self.stdout.write('Rode este comando com --confirm para realmente excluir os grupos listados.')
            return

        # confirm == True => proceed
        deleted = []
        skipped = []
        errors = []
        with transaction.atomic():
            for g, num_visitas in to_delete:
                if num_visitas > 0 and not force:
                    skipped.append((g.pk, num_visitas))
                    continue
                try:
                    g.delete()
                    deleted.append(g.pk)
                except Exception as e:
                    errors.append((g.pk, str(e)))

        self.stdout.write(self.style.SUCCESS(f'Deletados: {len(deleted)}'))
        if skipped:
            self.stdout.write(self.style.WARNING(f'Skipped {len(skipped)} grupos que tinham visitas (use --force para forçar):'))
            for pk, nv in skipped:
                self.stdout.write(f' - {pk} (visitas: {nv})')
        if errors:
            self.stdout.write(self.style.ERROR(f'Erros ao excluir {len(errors)} grupos:'))
            for pk, msg in errors:
                self.stdout.write(f' - {pk}: {msg}')

        self.stdout.write(self.style.SUCCESS('Operação finalizada.'))
