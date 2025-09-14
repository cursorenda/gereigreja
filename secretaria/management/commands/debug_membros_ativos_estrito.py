from django.core.management.base import BaseCommand
from secretaria.models import Membro

class Command(BaseCommand):
    help = 'Mostra o total de membros com status "Ativo" e tipo "Membro".'

    def handle(self, *args, **options):
        qs = Membro.objects.filter(status_pessoa__nome__iexact="Ativo", tipo_pessoa__nome__iexact="Membro")
        total = qs.count()
        self.stdout.write(self.style.SUCCESS(f"Total de membros com status 'Ativo' e tipo 'Membro': {total}"))
        for m in qs:
            self.stdout.write(f"ID: {m.chave} | Nome: {m.nome} | Status: {m.status_pessoa} | Tipo: {m.tipo_pessoa}")
