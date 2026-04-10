from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from contas.constants import GRUPOS_TODOS


class Command(BaseCommand):
    help = 'Audita usuarios e grupos do sistema GereIgreja.'

    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write('--- Usuarios sem grupo ---')
        for user in User.objects.all():
            if not user.groups.exists():
                self.stdout.write(f'Usuario sem grupo: {user.username}')

        self.stdout.write('--- Grupos nao padronizados ---')
        grupos_db = set(Group.objects.values_list('name', flat=True))
        grupos_padrao = set(GRUPOS_TODOS)
        for grupo in grupos_db - grupos_padrao:
            self.stdout.write(f'Grupo no banco nao padronizado: {grupo}')

        self.stdout.write('--- Auditoria concluida ---')