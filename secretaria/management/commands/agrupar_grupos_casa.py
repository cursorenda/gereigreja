from django.core.management.base import BaseCommand, CommandError
from secretaria.models import Pessoa, GrupoCasa
from django.db import transaction
import unicodedata
import re
import csv


def normalize_text(s: str) -> str:
    if not s:
        return ''
    s = s.strip().lower()
    # remove accents
    s = unicodedata.normalize('NFKD', s)
    s = ''.join([c for c in s if not unicodedata.combining(c)])
    # normalize spaces and punctuation
    s = re.sub(r"\s+", ' ', s)
    s = re.sub(r"[^0-9a-z ]", ' ', s)
    s = re.sub(r"\s+", ' ', s)
    return s.strip()


class Command(BaseCommand):
    help = 'Agrupa pessoas em Grupos/Casas com base no endereço. Use --preview para gerar relatório e --apply para aplicar.'

    def add_arguments(self, parser):
        parser.add_argument('--preview', action='store_true', help='Gerar CSV de pré-visualização sem aplicar alterações')
        parser.add_argument('--apply', action='store_true', help='Aplicar alterações (criar Grupos/Casas e associar pessoas)')
        parser.add_argument('--output', type=str, default='grupos_casa_report.csv', help='Arquivo CSV de saída (preview e apply)')

    def handle(self, *args, **options):
        preview = options['preview']
        apply_changes = options['apply']
        output = options['output']

        if not preview and not apply_changes:
            raise CommandError('Use --preview para gerar relatório ou --apply para aplicar as alterações (requer confirmação).')

        persons = Pessoa.objects.select_related('igreja').all()
        groups = {}

        for p in persons:
            key = (
                p.igreja_id or 0,
                normalize_text(p.cep or ''),
                normalize_text(p.rua or ''),
                normalize_text(p.numero_casa or ''),
                normalize_text(p.complemento or '')
            )
            groups.setdefault(key, []).append(p)

        # Prepare CSV
        with open(output, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['igreja_id','cep','rua','numero','complemento','qtd_pessoas','pessoas_ids','pessoas_nomes'])

            summary = []
            for key, plist in groups.items():
                igreja_id, cep, rua, numero, complemento = key
                ids = [str(p.pk) for p in plist]
                nomes = [p.nome for p in plist]
                writer.writerow([igreja_id, cep, rua, numero, complemento, len(plist), ';'.join(ids), ';'.join(nomes)])
                summary.append((key, plist))

        self.stdout.write(self.style.SUCCESS(f'Relatório gerado em {output} com {len(groups)} grupos detectados.'))

        if apply_changes:
            # Pedir confirmação interativa
            self.stdout.write('Vai aplicar as alterações: criar Grupos/Casas e associar pessoas.')
            confirm = input('Confirma aplicar as alterações? Digite "sim" para confirmar: ')
            if confirm.lower() != 'sim':
                self.stdout.write(self.style.WARNING('Aplicação cancelada pelo usuário.'))
                return

            created = 0
            updated = 0
            with transaction.atomic():
                for key, plist in summary:
                    igreja_id, cep, rua, numero, complemento = key
                    # criar ou get GrupoCasa
                    house, created_flag = GrupoCasa.objects.get_or_create(
                        igreja_id=igreja_id if igreja_id else None,
                        rua=rua or None,
                        numero=numero or None,
                        complemento=complemento or None,
                        cep=cep or None,
                        defaults={'nome': None}
                    )
                    if created_flag:
                        created += 1
                    # associar pessoas
                    for p in plist:
                        if p.grupo_casa_id != house.id:
                            p.grupo_casa = house
                            p.save()
                            updated += 1
            self.stdout.write(self.style.SUCCESS(f'Aplicação concluída: {created} grupos/casas criados, {updated} pessoas atualizadas.'))
        else:
            self.stdout.write(self.style.NOTICE('Execução em modo preview — nenhuma alteração foi aplicada.'))
