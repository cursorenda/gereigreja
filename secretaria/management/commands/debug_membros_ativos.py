from django.core.management.base import BaseCommand
from secretaria.models import Membro

class Command(BaseCommand):
    help = 'Mostra o total de membros ativos do tipo "Membro" e lista seus nomes/ids.'

    def handle(self, *args, **options):
        qs = Membro.objects.filter(status_pessoa__considerar_ativo_relatorios=True, tipo_pessoa__nome__iexact="Membro")
        total = qs.count()
        self.stdout.write(self.style.SUCCESS(f"Total de membros ativos do tipo 'Membro': {total}"))
        for m in qs:
            self.stdout.write(f"ID: {m.chave} | Nome: {m.nome} | Status: {m.status_pessoa} | Tipo: {m.tipo_pessoa}")
