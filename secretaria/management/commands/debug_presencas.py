from django.core.management.base import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
    help = 'Debug helper: show recent PresencaVisitanteEvento and ParticipacaoEvento records. Use --membro to filter by membro.chave or --limit to change number of rows.'

    def add_arguments(self, parser):
        parser.add_argument('--membro', type=int, help='membro.chave or pk to filter')
        parser.add_argument('--limit', type=int, default=20, help='number of records to show per model')

    def handle(self, *args, **options):
        membro = options.get('membro')
        limit = options.get('limit') or 20

        try:
            from secretaria.models import PresencaVisitanteEvento, Membro
            from eventos.models import ParticipacaoEvento
        except Exception as e:
            self.stderr.write(f'Erro importando modelos: {e}')
            return

        self.stdout.write(self.style.MIGRATE_HEADING(f'[{timezone.now().isoformat()}] Debug presenças (limit={limit})'))

        if membro:
            try:
                m = Membro.objects.filter(chave=membro).first() or Membro.objects.filter(pk=membro).first()
            except Exception:
                m = None
            if not m:
                self.stdout.write(self.style.WARNING(f'Membro {membro} não encontrado. Mostrando registros sem filtro de membro.'))
                membro = None
            else:
                self.stdout.write(self.style.SUCCESS(f'Filtrando por membro: {m.nome} (pk={m.pk} chave={getattr(m, "chave", None)})'))

        q_pres = PresencaVisitanteEvento.objects.all().select_related('membro', 'evento').order_by('-data_registro')
        q_part = ParticipacaoEvento.objects.all().select_related('membro', 'evento', 'sessao').order_by('-criado_em')

        if membro:
            q_pres = q_pres.filter(membro__chave=membro) | q_pres.filter(membro__pk=membro)
            q_part = q_part.filter(membro__chave=membro) | q_part.filter(membro__pk=membro)

        presencas = list(q_pres[:limit])
        participacoes = list(q_part[:limit])

        self.stdout.write(self.style.NOTICE('\nÚltimas presenças:'))
        if not presencas:
            self.stdout.write('  (nenhuma encontrada)')
        for p in presencas:
            self.stdout.write(f'  Presenca pk={p.pk} membro={getattr(p.membro, "nome", "(sem membro)")} (chave={getattr(p.membro, "chave", None)}) evento_id={getattr(p.evento, "pk", None)} data={p.data_registro} responsavel={getattr(p.responsavel_registro, "username", getattr(p.responsavel_registro, "pk", None))}')

        self.stdout.write(self.style.NOTICE('\nÚltimas participações:'))
        if not participacoes:
            self.stdout.write('  (nenhuma encontrada)')
        for pt in participacoes:
            self.stdout.write(f'  Participacao pk={pt.pk} membro={getattr(pt.membro, "nome", "(sem membro)")} (chave={getattr(pt.membro, "chave", None)}) evento_id={getattr(pt.evento, "pk", None)} sessao_id={getattr(pt.sessao, "pk", None)} status={pt.status} criado_em={pt.criado_em}')

        self.stdout.write('\nDone.')
