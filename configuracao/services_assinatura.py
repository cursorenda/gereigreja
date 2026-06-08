import logging
from typing import Optional
from datetime import datetime

from configuracao.models import AssinaturaMinisterio, EventoFunil, HistoricoAssinatura, LiberacaoPlanoMinisterio, Ministerio, Plano

logger = logging.getLogger(__name__)

STATUS_ASSINATURA_REGULAR = {'ativa', 'gratuita'}


def _timestamp_to_date(ts):
    if not ts:
        return None
    try:
        return datetime.utcfromtimestamp(int(ts)).date()
    except Exception:
        return None


def _calcular_usos_restantes(max_redemptions, times_redeemed):
    if max_redemptions is None:
        return None
    try:
        restantes = int(max_redemptions) - int(times_redeemed or 0)
        return max(0, restantes)
    except Exception:
        return None


def _upsert_codigo_promocional_local(
    codigo_stripe,
    descricao='',
    ativo=True,
    percentual_desconto=None,
    data_termino=None,
    usos_restantes=None,
    vezes_usado=None,
):
    from configuracao.models import CodigoPromocional

    defaults = {
        'descricao': descricao or '',
        'status': 'ativo' if ativo else 'inativo',
        'percentual_desconto': percentual_desconto,
        'data_termino': data_termino,
        'usos_restantes': usos_restantes,
    }
    if vezes_usado is not None:
        defaults['vezes_usado'] = int(vezes_usado)

    CodigoPromocional.objects.update_or_create(
        codigo_stripe=str(codigo_stripe).strip(),
        defaults=defaults,
    )


def _ministerio_eh_demo(ministerio: Optional[Ministerio]) -> bool:
    """Identifica o ministério de demonstração para liberar limites de teste."""
    if not ministerio:
        return False

    nome = (getattr(ministerio, 'nome_fantasia', '') or '').strip().lower()
    if nome == 'demonstração' or nome == 'demonstracao':
        return True

    administrador = getattr(ministerio, 'administrador_principal', None)
    username = getattr(administrador, 'username', '') or ''
    return username.startswith('admin_demo')


# ---------------------------------------------------------------------------
# HELPER DE FUNIL
# ---------------------------------------------------------------------------
def registrar_evento_funil(
    tipo: str,
    ministerio: Optional[Ministerio] = None,
    plano: Optional[Plano] = None,
    ciclo_pagamento: Optional[str] = None,
    valor=None,
    extra: Optional[dict] = None,
) -> None:
    """Registra um evento de funil de forma silenciosa (nunca lança exceção para o usuário)."""
    try:
        EventoFunil.objects.create(
            tipo=tipo,
            ministerio=ministerio,
            plano=plano,
            ciclo_pagamento=ciclo_pagamento,
            valor=valor,
            extra=extra or {},
        )
    except Exception as exc:
        logger.warning(f"[funil] Falha ao registrar evento '{tipo}': {exc}")



def obter_assinatura_ministerio(ministerio: Ministerio) -> Optional[AssinaturaMinisterio]:
    """Retorna a assinatura do ministerio ou None quando nao existir."""
    return AssinaturaMinisterio.objects.filter(ministerio=ministerio).first()


def obter_ministerio_do_usuario(user) -> Optional[Ministerio]:
    """Resolve o ministerio do usuario via perfil, membro ou administracao principal."""
    perfil = getattr(user, 'perfil', None) or getattr(user, 'perfil_usuario', None)
    ministerio = getattr(perfil, 'ministerio', None) if perfil else None

    if not ministerio:
        membro = getattr(user, 'membro_secretaria', None)
        ministerio = getattr(getattr(membro, 'igreja', None), 'ministerio', None)

    if not ministerio:
        ministerio = Ministerio.objects.filter(administrador_principal=user).first()

    return ministerio


def assinatura_esta_regular(assinatura: Optional[AssinaturaMinisterio], ministerio: Ministerio) -> bool:
    """Regra central de elegibilidade de assinatura para acesso ao sistema."""
    # Liberação BETA individual sempre libera acesso independente do status da assinatura
    from configuracao.models import LiberacaoPlanoMinisterio
    if LiberacaoPlanoMinisterio.objects.filter(
        ministerio=ministerio, ativo=True, acesso_beta=True, pode_visualizar=True
    ).exists():
        return True

    if assinatura is None:
        return ministerio.verificar_elegibilidade_plano_gratuito()

    if assinatura.trial_ativo and not is_trial_ativo(assinatura):
        return False

    if is_trial_ativo(assinatura):
        return True

    if assinatura.status in STATUS_ASSINATURA_REGULAR:
        return True

    if assinatura.is_periodo_cortesia_valido():
        return True

    # Grace period por inadimplência: acesso mantido enquanto dentro do prazo
    if assinatura_em_graca_inadimplencia(assinatura):
        return True

    if assinatura.status == 'vencida' and ministerio.verificar_elegibilidade_plano_gratuito():
        return True

    return False


def assinatura_em_graca_inadimplencia(assinatura: Optional[AssinaturaMinisterio]) -> bool:
    """Verifica se a assinatura está em período de graça por inadimplência (não expirado)."""
    if not assinatura or assinatura.status != 'pendente_pagamento':
        return False
    
    if not assinatura.data_fim_graca_inadimplencia:
        return False
    
    from django.utils import timezone
    return timezone.now() < assinatura.data_fim_graca_inadimplencia


def dias_restantes_graca(assinatura: Optional[AssinaturaMinisterio]) -> Optional[int]:
    """Retorna quantos dias restam do período de graça, ou None se não está em graça."""
    if not assinatura_em_graca_inadimplencia(assinatura):
        return None
    
    from django.utils import timezone
    delta = assinatura.data_fim_graca_inadimplencia - timezone.now()
    return max(0, delta.days)


def validar_codigo_promocional(codigo: str) -> tuple[bool, str]:
    """Valida um código promocional e retorna (é_válido, mensagem_erro).
    
    Retorna:
        (True, "") se válido
        (False, "motivo") caso contrário
    """
    if not codigo or not codigo.strip():
        return (False, "Cupom vazio.")
    
    codigo_limpo = codigo.strip()

    # 1) Tenta validar pelo cadastro interno (quando existir)
    try:
        from configuracao.models import CodigoPromocional
        cupom = CodigoPromocional.objects.get(codigo_stripe=codigo_limpo)

        if not cupom.is_valido():
            return (False, "Este cupom não é mais válido.")

        return (True, "")
    except CodigoPromocional.DoesNotExist:
        pass

    # 2) Fallback: valida direto no Stripe para não bloquear cupons válidos
    # que ainda não foram cadastrados localmente.
    try:
        import stripe
        from django.conf import settings

        stripe.api_key = settings.STRIPE_SECRET_KEY

        # 2.1 Promotion code por ID
        if codigo_limpo.startswith('promo_'):
            promo = stripe.PromotionCode.retrieve(codigo_limpo)
            if promo and getattr(promo, 'active', False):
                coupon_id = promo.coupon.id if hasattr(promo.coupon, 'id') else promo.coupon
                coupon = stripe.Coupon.retrieve(coupon_id)
                _upsert_codigo_promocional_local(
                    codigo_stripe=promo.id,
                    descricao=getattr(promo, 'code', '') or getattr(coupon, 'name', '') or 'Promotion Code Stripe',
                    ativo=bool(getattr(promo, 'active', False)),
                    percentual_desconto=getattr(coupon, 'percent_off', None),
                    data_termino=_timestamp_to_date(getattr(coupon, 'redeem_by', None)),
                    usos_restantes=_calcular_usos_restantes(getattr(promo, 'max_redemptions', None), getattr(promo, 'times_redeemed', 0)),
                    vezes_usado=getattr(promo, 'times_redeemed', 0),
                )
                return (True, "")

        # 2.2 Promotion code por código legível
        promotion_codes = stripe.PromotionCode.list(code=codigo_limpo, active=True, limit=1)
        if getattr(promotion_codes, 'data', None):
            promo = promotion_codes.data[0]
            coupon_id = promo.coupon.id if hasattr(promo.coupon, 'id') else promo.coupon
            coupon = stripe.Coupon.retrieve(coupon_id)
            _upsert_codigo_promocional_local(
                codigo_stripe=promo.id,
                descricao=getattr(promo, 'code', '') or getattr(coupon, 'name', '') or 'Promotion Code Stripe',
                ativo=bool(getattr(promo, 'active', False)),
                percentual_desconto=getattr(coupon, 'percent_off', None),
                data_termino=_timestamp_to_date(getattr(coupon, 'redeem_by', None)),
                usos_restantes=_calcular_usos_restantes(getattr(promo, 'max_redemptions', None), getattr(promo, 'times_redeemed', 0)),
                vezes_usado=getattr(promo, 'times_redeemed', 0),
            )
            return (True, "")

        # 2.3 Coupon por ID
        try:
            coupon = stripe.Coupon.retrieve(codigo_limpo)
            if coupon and getattr(coupon, 'valid', False):
                _upsert_codigo_promocional_local(
                    codigo_stripe=coupon.id,
                    descricao=getattr(coupon, 'name', '') or 'Cupom Stripe',
                    ativo=bool(getattr(coupon, 'valid', False)),
                    percentual_desconto=getattr(coupon, 'percent_off', None),
                    data_termino=_timestamp_to_date(getattr(coupon, 'redeem_by', None)),
                    usos_restantes=_calcular_usos_restantes(getattr(coupon, 'max_redemptions', None), getattr(coupon, 'times_redeemed', 0)),
                    vezes_usado=getattr(coupon, 'times_redeemed', 0),
                )
                return (True, "")
        except Exception:
            pass

        # 2.4 Coupon por nome (fallback para painel Stripe)
        coupons = stripe.Coupon.list(limit=100)
        for coupon in coupons.auto_paging_iter():
            if (getattr(coupon, 'name', '') or '').strip().lower() == codigo_limpo.lower():
                if getattr(coupon, 'valid', False):
                    _upsert_codigo_promocional_local(
                        codigo_stripe=coupon.id,
                        descricao=getattr(coupon, 'name', '') or 'Cupom Stripe',
                        ativo=bool(getattr(coupon, 'valid', False)),
                        percentual_desconto=getattr(coupon, 'percent_off', None),
                        data_termino=_timestamp_to_date(getattr(coupon, 'redeem_by', None)),
                        usos_restantes=_calcular_usos_restantes(getattr(coupon, 'max_redemptions', None), getattr(coupon, 'times_redeemed', 0)),
                        vezes_usado=getattr(coupon, 'times_redeemed', 0),
                    )
                    return (True, "")
                return (False, "Este cupom existe no Stripe, mas não está mais válido.")

    except Exception as exc:
        logger.warning(f"Falha ao validar cupom diretamente no Stripe '{codigo_limpo}': {exc}")

    return (False, "Cupom não reconhecido. Verifique o código.")


def is_trial_ativo(assinatura: Optional[AssinaturaMinisterio]) -> bool:
    """Verifica se o trial está ativo e não expirou."""
    if not assinatura or not assinatura.trial_ativo:
        return False

    if not assinatura.data_inicio_trial:
        return False

    from django.utils import timezone
    dias_totais = assinatura.dias_trial_totais or 14
    data_fim_trial = assinatura.data_inicio_trial + timezone.timedelta(days=dias_totais)
    return timezone.now() < data_fim_trial


def dias_restantes_trial(assinatura: Optional[AssinaturaMinisterio]) -> Optional[int]:
    """Retorna quantos dias restam do trial, ou None se não está em trial."""
    if not is_trial_ativo(assinatura):
        return None

    from django.utils import timezone
    dias_totais = assinatura.dias_trial_totais or 14
    data_fim_trial = assinatura.data_inicio_trial + timezone.timedelta(days=dias_totais)
    delta = data_fim_trial - timezone.now()
    return max(0, delta.days)


def iniciar_trial(ministerio: Ministerio) -> AssinaturaMinisterio:
    """Inicia um período de trial de 14 dias para o ministério."""
    from django.utils import timezone

    assinatura = obter_assinatura_ministerio(ministerio)
    if assinatura is None:
        assinatura = AssinaturaMinisterio.objects.create(
            ministerio=ministerio,
            status='gratuita',
            data_inicio=timezone.now(),
            trial_ativo=True,
            data_inicio_trial=timezone.now(),
            dias_trial_totais=14,
        )
    else:
        assinatura.trial_ativo = True
        assinatura.data_inicio_trial = timezone.now()
        assinatura.dias_trial_totais = 14
        assinatura.status = 'gratuita'
        if not assinatura.data_inicio:
            assinatura.data_inicio = timezone.now()
        assinatura.save(update_fields=['trial_ativo', 'data_inicio_trial', 'dias_trial_totais', 'status', 'data_inicio', 'data_atualizacao'])

    # Registra trial no histórico
    trial_fim = timezone.now() + timezone.timedelta(days=14)
    HistoricoAssinatura.objects.create(
        ministerio=ministerio,
        plano=assinatura.plano,
        tipo='trial',
        valor=0.00,
        status='a_vencer',
        data_inicio=assinatura.data_inicio_trial,
        data_fim=trial_fim,
        observacao='Período de teste grátis — 14 dias',
    )

    return assinatura


def ministerio_pode_usar_modulo(ministerio: Ministerio, modulo: str) -> bool:
    """Valida acesso a modulos por plano contratado.

    O status da assinatura (vencida, gratuita etc.) nao bloqueia modulos —
    isso e responsabilidade do middleware/decorator de acesso ao sistema.
    Aqui apenas verificamos se o plano permite o modulo solicitado.
    """
    modulo = (modulo or '').lower().strip()
    plano = obter_plano_efetivo_ministerio(ministerio)
    if not plano:
        return True

    modulo_para_campo = {
        'secretaria': 'permite_modulo_secretaria',
        'agenda': 'permite_modulo_agenda',
        'eventos': 'permite_modulo_eventos',
        'escola_biblica': 'permite_modulo_escola_biblica',
        'financeiro': 'permite_modulo_financeiro',
        'comunicacao': 'permite_modulo_comunicacao',
        'comunicacao_massa': 'permite_modulo_comunicacao',
    }

    campo = modulo_para_campo.get(modulo)
    if campo:
        return bool(getattr(plano, campo, True))

    return True


def usuario_pode_usar_modulo(user, modulo: str) -> bool:
    """Valida modulo por usuario autenticado com fallbacks de resolucao de ministerio."""
    if not getattr(user, 'is_authenticated', False):
        return False

    if getattr(user, 'is_superuser', False):
        return True

    ministerio = obter_ministerio_do_usuario(user)
    if not ministerio:
        return False

    # No modo demonstracao, todos os modulos devem ficar disponiveis para
    # que os perfis possam ser explorados sem bloqueio de plano.
    if _ministerio_eh_demo(ministerio):
        return True

    return ministerio_pode_usar_modulo(ministerio, modulo)


def obter_plano_efetivo_ministerio(ministerio: Ministerio) -> Optional[Plano]:
    """Retorna o plano aplicavel ao ministerio.

    Prioridade:
    1) liberacao ativa por ministerio (pilot/beta)
    2) plano da assinatura
    3) plano pioneiro como fallback
    """
    liberacao_ativa = (
        LiberacaoPlanoMinisterio.objects
        .filter(
            ministerio=ministerio,
            ativo=True,
            pode_visualizar=True,
        )
        .select_related('plano')
        .order_by('-data_atualizacao', '-id')
        .first()
    )
    if liberacao_ativa and liberacao_ativa.plano and liberacao_ativa.plano.ativo:
        return liberacao_ativa.plano

    assinatura = obter_assinatura_ministerio(ministerio)
    if assinatura and assinatura.plano:
        return assinatura.plano

    return Plano.objects.filter(codigo_plano='pioneiro', ativo=True).first()


def obter_liberacao_plano_ministerio(ministerio: Optional[Ministerio], plano: Plano) -> Optional[LiberacaoPlanoMinisterio]:
    """Retorna a liberação específica do plano para o ministério, quando existir."""
    if not ministerio:
        return None

    return LiberacaoPlanoMinisterio.objects.filter(
        ministerio=ministerio,
        plano=plano,
        ativo=True,
    ).first()


def plano_esta_visivel_publicamente(plano: Plano) -> bool:
    """Define se o plano deve aparecer para o público geral."""
    return bool(plano.ativo and plano.is_visible and plano.liberado_publicamente)


def plano_pode_ser_contratado_publicamente(plano: Plano) -> bool:
    """Define se o plano pode ser contratado por qualquer ministério."""
    return bool(plano_esta_visivel_publicamente(plano) and plano.contratacao_publica_liberada)


def ministerio_pode_visualizar_plano(ministerio: Optional[Ministerio], plano: Plano) -> bool:
    """Valida visibilidade do plano para um ministério específico, considerando allowlist piloto."""
    if plano_esta_visivel_publicamente(plano):
        return True

    liberacao = obter_liberacao_plano_ministerio(ministerio, plano)
    return bool(liberacao and liberacao.pode_visualizar)


def ministerio_pode_contratar_plano(ministerio: Optional[Ministerio], plano: Plano) -> bool:
    """Valida contratação do plano para um ministério específico, considerando rollout e piloto."""
    if plano_pode_ser_contratado_publicamente(plano):
        return True

    liberacao = obter_liberacao_plano_ministerio(ministerio, plano)
    return bool(liberacao and liberacao.pode_contratar)


def listar_planos_publicos():
    """Lista planos exibidos para o público geral na landing page."""
    return Plano.objects.filter(
        ativo=True,
        is_visible=True,
        liberado_publicamente=True,
    ).order_by('ordem_liberacao', 'preco_mensal')


def listar_planos_landing_page():
    """Lista todos os planos ativos e visíveis para a landing page de marketing.
    Não depende do flag liberado_publicamente — a landing sempre exibe todos os planos."""
    return Plano.objects.filter(
        ativo=True,
        is_visible=True,
    ).order_by('ordem_liberacao', 'preco_mensal')


def listar_planos_para_ministerio(ministerio: Optional[Ministerio]):
    """Lista planos visíveis para um ministério, incluindo exceções piloto."""
    planos = Plano.objects.filter(ativo=True).order_by('ordem_liberacao', 'preco_mensal')
    return [plano for plano in planos if ministerio_pode_visualizar_plano(ministerio, plano)]


def contar_pessoas_ativas(ministerio: Ministerio) -> int:
    """Conta pessoas ativas do ministério para enforcement do plano."""
    if _ministerio_eh_demo(ministerio):
        return 0

    from secretaria.models import Membro

    return Membro.objects.filter(
        igreja__ministerio=ministerio,
        status_pessoa__nome__iexact='Ativo',
    ).count()


def obter_limite_pessoas_ativas(ministerio: Ministerio) -> Optional[int]:
    """Retorna o limite de pessoas ativas do plano efetivo; None significa sem limite conhecido."""
    if _ministerio_eh_demo(ministerio):
        return 0

    plano = obter_plano_efetivo_ministerio(ministerio)
    if not plano:
        return None
    return plano.limite_membros


def ministerio_pode_adicionar_pessoa_ativa(ministerio: Ministerio, quantidade: int = 1) -> bool:
    """Valida se o ministério ainda pode ativar mais pessoas conforme o plano."""
    if _ministerio_eh_demo(ministerio):
        return True

    assinatura = obter_assinatura_ministerio(ministerio)
    if not assinatura_esta_regular(assinatura, ministerio):
        return False

    limite = obter_limite_pessoas_ativas(ministerio)
    if limite is None or limite == 0:
        return True

    total_ativos = contar_pessoas_ativas(ministerio)
    return (total_ativos + quantidade) <= limite


def ministerio_pode_criar_igreja(ministerio: Ministerio) -> bool:
    """Valida limite de igrejas conforme plano efetivo e status da assinatura."""
    assinatura = obter_assinatura_ministerio(ministerio)
    if not assinatura_esta_regular(assinatura, ministerio):
        return False

    plano = obter_plano_efetivo_ministerio(ministerio)
    if not plano:
        return True

    limite = plano.limite_igrejas
    if not limite or limite == 0:
        return True

    total_igrejas = ministerio.igrejas.count()
    return total_igrejas < limite
