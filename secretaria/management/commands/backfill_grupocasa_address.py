from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db import models
from secretaria.models import GrupoCasa, Pessoa


class Command(BaseCommand):
    help = 'Preview / backfill bairro/cidade/estado em GrupoCasa a partir dos moradores (Pessoa).'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Aplicar as alterações (commit).')
        parser.add_argument('--igreja', type=int, help='Filtrar por ID da igreja (opcional).')

    def handle(self, *args, **options):
        apply_changes = options.get('apply')
        igreja_id = options.get('igreja')

        qs = GrupoCasa.objects.annotate(num_pessoas=Count('pessoas'))
        if igreja_id:
            qs = qs.filter(igreja_id=igreja_id)

        # Filtrar grupos que têm moradores mas faltam endereço
        candidates = qs.filter(num_pessoas__gt=0).filter(
            (models.Q(bairro__isnull=True) | models.Q(bairro='')) |
            (models.Q(cidade__isnull=True) | models.Q(cidade='')) |
            (models.Q(estado__isnull=True) | models.Q(estado=''))
        )

        total = candidates.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nenhum GrupoCasa com moradores e endereço incompleto encontrado.'))
            return

        self.stdout.write(self.style.WARNING(f'Encontrados {total} GrupoCasa(s) com moradores e endereço incompleto.'))

        for g in candidates.order_by('igreja_id', 'rua', 'numero'):
            # buscar primeiro morador com dados
            p = Pessoa.objects.filter(grupo_casa=g).first()
            bairro = getattr(p, 'bairro_distrito', '') if p else ''
            cidade = getattr(p, 'cidade', '') if p else ''
            estado = getattr(p, 'estado', '') if p else ''
            self.stdout.write(f"{g.pk} - {g.nome or g.rua} | atual: bairro='{g.bairro}' cidade='{g.cidade}' estado='{g.estado}' -> sugestao: bairro='{bairro}' cidade='{cidade}' estado='{estado}'")
            if apply_changes and p:
                changed = False
                if not g.bairro and bairro:
                    g.bairro = bairro
                    changed = True
                if not g.cidade and cidade:
                    g.cidade = cidade
                    changed = True
                if not g.estado and estado:
                    g.estado = estado
                    changed = True
                if changed:
                    g.save()
                    self.stdout.write(self.style.SUCCESS(f'  -> Atualizado {g.pk}'))

        if not apply_changes:
            self.stdout.write('Rode com --apply para aplicar as sugestões acima.')
