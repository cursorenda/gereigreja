from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps

from contas.constants import ADMIN_MINISTERIO

class Command(BaseCommand):
    help = f'Atribui todas as permissões de todos os models ao grupo {ADMIN_MINISTERIO}.'

    def handle(self, *args, **options):
        group_name = ADMIN_MINISTERIO
        group, created = Group.objects.get_or_create(name=group_name)
        all_permissions = Permission.objects.all()
        group.permissions.set(all_permissions)
        group.save()
        self.stdout.write(self.style.SUCCESS(f'Todas as permissões atribuídas ao grupo {group_name}.'))
