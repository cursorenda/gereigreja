from django.core.management.base import BaseCommand
from secretaria.models import GrupoCasa, Membro

class Command(BaseCommand):
    help = 'Lista todas as pessoas (inclusive inativas/ocultas) vinculadas a um GrupoCasa pelo ID.'

    def add_arguments(self, parser):
        parser.add_argument('grupocasa_id', type=int, help='ID do GrupoCasa a inspecionar')

    def handle(self, *args, **options):
        grupocasa_id = options['grupocasa_id']
        try:
            grupo = GrupoCasa.objects.get(pk=grupocasa_id)
        except GrupoCasa.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'GrupoCasa com id={grupocasa_id} não encontrado.'))
            return

        pessoas = grupo.pessoas.all()
        total = pessoas.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nenhuma pessoa vinculada a este GrupoCasa.'))
            return

        self.stdout.write(f'Pessoas vinculadas ao GrupoCasa id={grupocasa_id} ({grupo}):')
        for p in pessoas:
            pessoa_id = getattr(p, 'pk', None) or getattr(p, 'id', None) or '?'
            nome = getattr(p, 'nome', '?')
            status = getattr(p, 'status_pessoa', '?')
            ativo = getattr(p, 'ativo', '?')
            self.stdout.write(f'- ID: {pessoa_id} | Nome: {nome} | Status: {status} | Ativo: {ativo}')
        self.stdout.write(self.style.WARNING(f'Total: {total} pessoa(s) encontradas.'))