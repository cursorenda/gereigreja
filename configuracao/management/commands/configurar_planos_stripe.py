"""
Management command: configurar_planos_stripe

Cria ou atualiza produtos e preços no Stripe para os 4 planos do Gereigreja,
depois salva os IDs no banco. Idempotente: usa metadata para evitar duplicatas.

Uso:
    python manage.py configurar_planos_stripe              # modo test (padrão)
    python manage.py configurar_planos_stripe --live       # modo live (produção)

Em modo test, requer STRIPE_SECRET_KEY começando com sk_test_.
Em modo live,  requer STRIPE_SECRET_KEY começando com sk_live_.
"""

import stripe
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from configuracao.models import Plano


# ---------------------------------------------------------------------------
# Definição canônica dos planos. Ajuste os preços aqui se necessário.
# ---------------------------------------------------------------------------
PLANOS_CONFIG = [
    {
        "codigo": "crescimento",
        "nome_display": "Crescimento",
        "preco_mensal":    Decimal("29.00"),
        "preco_de_mensal": Decimal("39.00"),
        "preco_anual":     Decimal("290.00"),
        "preco_de_anual":  Decimal("390.00"),
        "descricao": "Até 250 membros, 1 igreja, módulo Financeiro incluso.",
    },
    {
        "codigo": "ministerio",
        "nome_display": "Ministério",
        "preco_mensal":    Decimal("59.00"),
        "preco_de_mensal": Decimal("79.00"),
        "preco_anual":     Decimal("590.00"),
        "preco_de_anual":  Decimal("790.00"),
        "descricao": "Até 500 membros, 3 igrejas, Comunicação + Eventos inclusos.",
    },
    {
        "codigo": "rede",
        "nome_display": "Rede",
        "preco_mensal":    Decimal("99.00"),
        "preco_de_mensal": Decimal("129.00"),
        "preco_anual":     Decimal("990.00"),
        "preco_de_anual":  Decimal("1290.00"),
        "descricao": "Membros e igrejas ilimitados, todos os módulos + suporte prioritário.",
    },
]

# Moeda utilizada (Stripe espera lowercase ISO 4217)
MOEDA = "brl"


def _reais_para_centavos(valor: Decimal) -> int:
    """Converte Decimal em reais para inteiro de centavos."""
    return int(round(valor * 100))


class Command(BaseCommand):
    help = "Cria/atualiza produtos e preços no Stripe e sincroniza os IDs no banco."

    def add_arguments(self, parser):
        parser.add_argument(
            "--live",
            action="store_true",
            default=False,
            help="Usa a chave de produção (sk_live_...). Sem a flag usa modo test.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Imprime o que seria feito sem chamar a API do Stripe nem salvar no banco.",
        )

    def handle(self, *args, **options):
        is_live = options["live"]
        dry_run = options["dry_run"]

        api_key = settings.STRIPE_SECRET_KEY
        if not api_key:
            raise CommandError(
                "STRIPE_SECRET_KEY não está definida nas configurações/env vars."
            )

        # Validação de modo
        if is_live and not api_key.startswith("sk_live_"):
            raise CommandError(
                "Você passou --live mas STRIPE_SECRET_KEY não começa com 'sk_live_'. Abortando."
            )
        if not is_live and not api_key.startswith("sk_test_"):
            self.stdout.write(
                self.style.WARNING(
                    "Atenção: --live não foi passado mas a chave não começa com 'sk_test_'. "
                    "Continuando mesmo assim (pode ser uma chave restrita)."
                )
            )

        stripe.api_key = api_key
        modo = "LIVE" if is_live else "TEST"
        self.stdout.write(self.style.HTTP_INFO(f"[Stripe {modo}] Iniciando configuração de planos...\n"))

        for cfg in PLANOS_CONFIG:
            self._processar_plano(cfg, dry_run)

        self.stdout.write(self.style.SUCCESS("\nConcluído! Verifique os IDs no Django Admin > Planos de Assinatura."))

    # ------------------------------------------------------------------

    def _processar_plano(self, cfg: dict, dry_run: bool):
        codigo = cfg["codigo"]
        self.stdout.write(f"── Plano: {cfg['nome_display']} ({codigo})")

        try:
            plano_obj = Plano.objects.get(codigo_plano=codigo)
        except Plano.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f"   AVISO: Plano '{codigo}' não encontrado no banco. Crie-o primeiro via admin."
                )
            )
            return

        # ── Produto ──────────────────────────────────────────────────
        product_id = plano_obj.stripe_product_id
        if product_id:
            self.stdout.write(f"   Produto existente no banco: {product_id} — validando no Stripe.")
            if not dry_run:
                try:
                    stripe.Product.modify(
                        product_id,
                        name=cfg['nome_display'],
                        description=cfg["descricao"],
                    )
                except stripe.error.InvalidRequestError:
                    self.stdout.write(
                        self.style.WARNING(
                            f"   Produto {product_id} não existe neste ambiente Stripe. Tentando localizar por metadata..."
                        )
                    )
                    product_id = None
                    plano_obj.stripe_product_id = None
        else:
            # Verifica se já existe produto com metadata gereigreja_plano=codigo no Stripe
            # para evitar duplicatas em re-runs
            existing = None
            if not dry_run:
                results = stripe.Product.search(
                    query=f'metadata["gereigreja_plano"]:"{codigo}"',
                    limit=1,
                )
                if results.data:
                    existing = results.data[0]

        if not product_id and not dry_run:
            # Tenta localizar de novo por metadata (caso o product_id antigo seja inválido)
            results = stripe.Product.search(
                query=f'metadata["gereigreja_plano"]:"{codigo}"',
                limit=1,
            )
            if results.data:
                existing = results.data[0]
            else:
                existing = None

            if existing:
                product_id = existing.id
                self.stdout.write(f"   Produto já existe no Stripe (via metadata): {product_id} — reutilizando.")
                plano_obj.stripe_product_id = product_id
            else:
                self.stdout.write("   Criando produto no Stripe...")
                product = stripe.Product.create(
                    name=cfg['nome_display'],
                    description=cfg["descricao"],
                    metadata={"gereigreja_plano": codigo},
                )
                product_id = product.id
                plano_obj.stripe_product_id = product_id
                self.stdout.write(f"   Produto criado: {product_id}")
        elif not product_id and dry_run:
            self.stdout.write("   [dry-run] Criaria produto.")

        # ── Preço Mensal ─────────────────────────────────────────────
        price_id_mensal = plano_obj.stripe_price_id_mensal
        price_id_mensal = self._garantir_preco(
            price_id_mensal,
            product_id=product_id,
            unit_amount=_reais_para_centavos(cfg["preco_mensal"]),
            interval="month",
            nickname=f"{cfg['nome_display']} Mensal",
            metadata_key=f"{codigo}_mensal",
            dry_run=dry_run,
        )
        if price_id_mensal and price_id_mensal != plano_obj.stripe_price_id_mensal:
            plano_obj.stripe_price_id_mensal = price_id_mensal

        # ── Preço Anual ───────────────────────────────────────────────
        price_id_anual = plano_obj.stripe_price_id_anual
        price_id_anual = self._garantir_preco(
            price_id_anual,
            product_id=product_id,
            unit_amount=_reais_para_centavos(cfg["preco_anual"]),
            interval="year",
            nickname=f"{cfg['nome_display']} Anual",
            metadata_key=f"{codigo}_anual",
            dry_run=dry_run,
        )
        if price_id_anual and price_id_anual != plano_obj.stripe_price_id_anual:
            plano_obj.stripe_price_id_anual = price_id_anual

        # ── Preços "de" (apenas banco, não cria no Stripe) ───────────
        plano_obj.preco_mensal    = cfg["preco_mensal"]
        plano_obj.preco_de_mensal = cfg["preco_de_mensal"]
        plano_obj.preco_anual     = cfg["preco_anual"]
        plano_obj.preco_de_anual  = cfg["preco_de_anual"]

        if not dry_run:
            plano_obj.save()
            self.stdout.write(self.style.SUCCESS(f"   Banco atualizado para '{codigo}'."))
        else:
            self.stdout.write(f"   [dry-run] Salvaria: mensal={cfg['preco_mensal']}, anual={cfg['preco_anual']}")

    # ------------------------------------------------------------------

    def _garantir_preco(
        self,
        price_id_existente,
        product_id,
        unit_amount: int,
        interval: str,
        nickname: str,
        metadata_key: str,
        dry_run: bool,
    ) -> str:
        """Retorna o price_id a usar: o existente (já ok) ou cria um novo."""
        if price_id_existente:
            self.stdout.write(f"   Preço {interval} existente: {price_id_existente} — validando no Stripe.")
            if dry_run:
                return price_id_existente

            try:
                price = stripe.Price.retrieve(price_id_existente)
                product_ok = str(getattr(price, 'product', '')) == str(product_id)
                unit_ok = int(getattr(price, 'unit_amount', -1) or -1) == int(unit_amount)
                recurring = getattr(price, 'recurring', None) or {}
                interval_ok = (recurring.get('interval') == interval)
                if getattr(price, 'active', False) and product_ok and unit_ok and interval_ok:
                    return price_id_existente

                self.stdout.write(
                    self.style.WARNING(
                        f"   Preço {price_id_existente} incompatível (active/product/amount/interval). Criando novo."
                    )
                )
            except stripe.error.InvalidRequestError:
                self.stdout.write(
                    self.style.WARNING(
                        f"   Preço {price_id_existente} não existe neste ambiente Stripe. Criando novo."
                    )
                )
            except Exception as exc:
                self.stdout.write(
                    self.style.WARNING(
                        f"   Falha ao validar preço {price_id_existente}: {exc}. Criando novo."
                    )
                )

        self.stdout.write(f"   Criando preço {interval} ({unit_amount/100:.2f} {MOEDA.upper()})...")
        if dry_run:
            self.stdout.write(f"   [dry-run] Criaria price {interval}.")
            return price_id_existente

        if not product_id:
            self.stdout.write(
                self.style.WARNING(f"   AVISO: product_id vazio, não é possível criar preço {interval}.")
            )
            return price_id_existente

        price = stripe.Price.create(
            product=product_id,
            unit_amount=unit_amount,
            currency=MOEDA,
            recurring={"interval": interval},
            nickname=nickname,
            metadata={"gereigreja_price": metadata_key},
        )
        self.stdout.write(f"   Preço {interval} criado: {price.id}")
        return price.id
