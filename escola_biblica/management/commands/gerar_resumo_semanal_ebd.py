from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from comunicacao.models import Aviso
from configuracao.models import ConfiguracaoSistema, Ministerio
from escola_biblica.utils import (
    build_resumo_semanal_ebd,
    formatar_resumo_semanal_ebd,
    get_faixa_semana_anterior,
)


class Command(BaseCommand):
    help = 'Gera resumo semanal operacional da EBD para secretaria/lideranca.'

    def add_arguments(self, parser):
        parser.add_argument('--ministerio-id', type=int, dest='ministerio_id')
        parser.add_argument('--inicio', type=str, dest='inicio')
        parser.add_argument('--fim', type=str, dest='fim')
        parser.add_argument(
            '--publicar-aviso',
            action='store_true',
            dest='publicar_aviso',
            help='Publica o resumo como Aviso no modulo de comunicacao.',
        )

    def handle(self, *args, **options):
        inicio_raw = options.get('inicio')
        fim_raw = options.get('fim')
        ministerio_id = options.get('ministerio_id')
        publicar_aviso = options.get('publicar_aviso', False)

        if inicio_raw or fim_raw:
            data_inicio = parse_date(inicio_raw) if inicio_raw else None
            data_fim = parse_date(fim_raw) if fim_raw else None
            if not data_inicio or not data_fim:
                self.stderr.write(self.style.ERROR('Datas inválidas. Use formato YYYY-MM-DD.'))
                return
            if data_inicio > data_fim:
                self.stderr.write(self.style.ERROR('Data inicial não pode ser maior que data final.'))
                return
        else:
            data_inicio, data_fim = get_faixa_semana_anterior()

        ministerios = Ministerio.objects.all().order_by('nome_fantasia')
        if ministerio_id:
            ministerios = ministerios.filter(pk=ministerio_id)

        if not ministerios.exists():
            self.stdout.write(self.style.WARNING('Nenhum ministério encontrado para geração do resumo EBD.'))
            return

        for ministerio in ministerios:
            # Mantem alinhamento com ministerios que possuem configuracao EBD ativa no sistema.
            if not ConfiguracaoSistema.objects.filter(ministerio=ministerio).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f'Ministério {ministerio.nome_fantasia} sem configuração EBD. Resumo não gerado.'
                    )
                )
                continue

            resumo = build_resumo_semanal_ebd(ministerio, data_inicio, data_fim)
            titulo = (
                f"Resumo semanal EBD - {data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m')}"
            )
            conteudo = formatar_resumo_semanal_ebd(resumo)

            self.stdout.write(self.style.SUCCESS(f'[{ministerio.nome_fantasia}] {titulo}'))
            self.stdout.write(conteudo)
            self.stdout.write('')

            if publicar_aviso:
                Aviso.objects.create(
                    ministerio=ministerio,
                    titulo=titulo,
                    conteudo=conteudo,
                    publicado=True,
                )
                self.stdout.write(self.style.SUCCESS('Aviso publicado para liderança/secretaria.'))
