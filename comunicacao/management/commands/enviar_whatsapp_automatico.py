from django.core.management.base import BaseCommand
from configuracao.models import Ministerio

from comunicacao.models import AutomacaoAniversariantes
from comunicacao.services import (
    executar_automacao_aniversario_whatsapp,
    executar_automacao_followup_visitantes_whatsapp,
    executar_automacao_lembrete_eventos_whatsapp,
    executar_automacao_novos_membros_whatsapp,
)
from comunicacao.models import WhatsAppConfiguracao


class Command(BaseCommand):
    help = 'Envia mensagens automaticas de WhatsApp (aniversariantes, novos membros, follow-up de visitantes e lembrete de eventos).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            default='aniversariantes',
            choices=['aniversariantes', 'novos_membros', 'followup_visitantes', 'lembrete_eventos'],
            help='Tipo de automacao a executar.',
        )
        parser.add_argument(
            '--dias-novos',
            type=int,
            default=7,
            help='Janela de dias para considerar novos membros na automacao de boas-vindas.',
        )
        parser.add_argument(
            '--dias-followup',
            type=int,
            default=1,
            help='Dias apos a primeira visita para enviar follow-up ao visitante.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Executa novamente mesmo se a automacao ja tiver rodado hoje.',
        )

    def handle(self, *args, **options):
        tipo = options['tipo']
        if tipo == 'aniversariantes':
            self.enviar_aniversariantes(force=options['force'])
        elif tipo == 'novos_membros':
            self.enviar_novos_membros(force=options['force'], dias_novos=options['dias_novos'])
        elif tipo == 'followup_visitantes':
            self.enviar_followup_visitantes(force=options['force'], dias_followup=options['dias_followup'])
        elif tipo == 'lembrete_eventos':
            self.enviar_lembrete_eventos(force=options['force'])

    def enviar_aniversariantes(self, force=False):
        enviados = 0
        falhas = 0

        for automacao in AutomacaoAniversariantes.objects.filter(whatsapp_ativo=True).select_related('ministerio'):
            resumo = executar_automacao_aniversario_whatsapp(
                ministerio=automacao.ministerio,
                force=force,
            )
            if resumo.get('ignorado'):
                continue
            enviados += resumo['enviados']
            falhas += resumo['falhas']

        self.stdout.write(self.style.SUCCESS(f'Envios com sucesso: {enviados}'))
        if falhas:
            self.stdout.write(self.style.WARNING(f'Falhas de envio: {falhas}'))

    def enviar_lembrete_eventos(self, force=False):
        enviados = 0
        falhas = 0
        ignorados = 0
        eventos_processados = 0

        ministerios_ids = (
            WhatsAppConfiguracao.objects.filter(ativo=True, auto_lembrete_eventos=True)
            .values_list('ministerio_id', flat=True)
            .distinct()
        )

        for ministerio in Ministerio.objects.filter(pk__in=ministerios_ids):
            resumo = executar_automacao_lembrete_eventos_whatsapp(
                ministerio=ministerio,
                force=force,
            )
            enviados += resumo['enviados']
            falhas += resumo['falhas']
            ignorados += resumo['ignorados']
            eventos_processados += resumo['eventos_processados']

        self.stdout.write(self.style.SUCCESS(f'Eventos processados: {eventos_processados}'))
        self.stdout.write(self.style.SUCCESS(f'Envios com sucesso: {enviados}'))
        if ignorados:
            self.stdout.write(self.style.WARNING(f'Ignorados (duplicados no dia): {ignorados}'))
        if falhas:
            self.stdout.write(self.style.WARNING(f'Falhas de envio: {falhas}'))

    def enviar_followup_visitantes(self, force=False, dias_followup=1):
        enviados = 0
        falhas = 0
        ignorados = 0

        ministerios_ids = (
            WhatsAppConfiguracao.objects.filter(ativo=True, auto_novos_membros=True)
            .values_list('ministerio_id', flat=True)
            .distinct()
        )

        for ministerio in Ministerio.objects.filter(pk__in=ministerios_ids):
            resumo = executar_automacao_followup_visitantes_whatsapp(
                ministerio=ministerio,
                dias_apos=dias_followup,
                force=force,
            )
            enviados += resumo['enviados']
            falhas += resumo['falhas']
            ignorados += resumo['ignorados']

        self.stdout.write(self.style.SUCCESS(f'Envios com sucesso: {enviados}'))
        if ignorados:
            self.stdout.write(self.style.WARNING(f'Ignorados (duplicados no dia): {ignorados}'))
        if falhas:
            self.stdout.write(self.style.WARNING(f'Falhas de envio: {falhas}'))

    def enviar_novos_membros(self, force=False, dias_novos=7):
        enviados = 0
        falhas = 0
        ignorados = 0

        ministerios_ids = (
            WhatsAppConfiguracao.objects.filter(ativo=True, auto_novos_membros=True)
            .values_list('ministerio_id', flat=True)
            .distinct()
        )

        for ministerio in Ministerio.objects.filter(pk__in=ministerios_ids):
            resumo = executar_automacao_novos_membros_whatsapp(
                ministerio=ministerio,
                dias=dias_novos,
                force=force,
            )
            enviados += resumo['enviados']
            falhas += resumo['falhas']
            ignorados += resumo['ignorados']

        self.stdout.write(self.style.SUCCESS(f'Envios com sucesso: {enviados}'))
        if ignorados:
            self.stdout.write(self.style.WARNING(f'Ignorados (ja tinham boas-vindas): {ignorados}'))
        if falhas:
            self.stdout.write(self.style.WARNING(f'Falhas de envio: {falhas}'))
