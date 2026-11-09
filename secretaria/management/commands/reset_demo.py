from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import F, Q

from configuracao.models import Igreja
from eventos.models import Evento
from financeiro.models import (
    ContaBancaria,
    ContaPagar,
    ContaPagarAutorizacaoEvento,
    Despesas,
    FechamentoCaixa,
    ImportacaoExtratoOFX,
    Receitas,
    RecorrenciaContaPagar,
    TransferenciaCaixa,
)

class Command(BaseCommand):
    help = (
        "Limpa os dados operacionais dos ministérios marcados como demo, "
        "preservando Ministério, Igrejas, usuários, pessoas, configurações "
        "estruturais e histórico de auditoria."
    )

    def handle(self, *args, **options):
        with transaction.atomic():
            demo_churches = Igreja.objects.filter(ministerio__is_demo=True)

            cross_tenant_transfers = TransferenciaCaixa.objects.filter(
                Q(
                    caixa_origem__igreja__ministerio__is_demo=True,
                    caixa_destino__igreja__ministerio__is_demo=False,
                )
                | Q(
                    caixa_origem__igreja__ministerio__is_demo=False,
                    caixa_destino__igreja__ministerio__is_demo=True,
                )
            )
            if cross_tenant_transfers.exists():
                raise CommandError(
                    "Foram encontradas transferências financeiras cross-tenant; "
                    "reset demo abortado sem mutações."
                )

            demo_events = Evento.objects.filter(igreja__in=demo_churches)
            if any(
                model.objects.filter(evento__in=demo_events)
                .exclude(igreja__in=demo_churches)
                .exists()
                for model in (Receitas, Despesas)
            ):
                raise CommandError(
                    "Foram encontradas referências financeiras fora do escopo demo; "
                    "reset demo abortado sem mutações."
                )

            demo_events.delete()
            ImportacaoExtratoOFX.objects.filter(igreja__in=demo_churches).delete()
            FechamentoCaixa.objects.filter(igreja__in=demo_churches).delete()
            TransferenciaCaixa.objects.filter(
                caixa_origem__igreja__in=demo_churches
            ).delete()
            ContaPagarAutorizacaoEvento.objects.filter(
                conta_pagar__igreja__in=demo_churches
            ).delete()
            ContaPagar.objects.filter(igreja__in=demo_churches).delete()
            RecorrenciaContaPagar.objects.filter(igreja__in=demo_churches).delete()
            Receitas.objects.filter(igreja__in=demo_churches).delete()
            Despesas.objects.filter(igreja__in=demo_churches).delete()
            ContaBancaria.objects.filter(igreja__in=demo_churches).update(
                saldo_atual=F("saldo_inicial")
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Dados operacionais dos ambientes demo resetados com sucesso."
            )
        )
