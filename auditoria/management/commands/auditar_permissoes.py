from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from contas.constants import GRUPOS_TODOS

class Command(BaseCommand):
    help = 'Audita usuários e grupos do sistema GereIgreja.'

    def handle(self, *args, **options):
        self.stdout.write('--- Usuários sem grupo ---')
        for user in User.objects.all():
            if not user.groups.exists():
                self.stdout.write(f'Usuário sem grupo: {user.username}')
        self.stdout.write('--- Grupos não padronizados ---')
        grupos_db = set(Group.objects.values_list('name', flat=True))
        grupos_padrao = set(GRUPOS_TODOS)
        for grupo in grupos_db - grupos_padrao:
            self.stdout.write(f'Grupo no banco não padronizado: {grupo}')
        self.stdout.write('--- Auditoria concluída ---')
