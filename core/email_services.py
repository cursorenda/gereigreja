"""Dispatch de e-mail com validação de tenant e resultado explícito."""
from dataclasses import dataclass
from enum import Enum
import logging

from django.conf import settings
from django.core.mail import send_mail


logger = logging.getLogger(__name__)


class StatusEnvioEmail(Enum):
    ENVIADO = 'enviado'
    NEUTRALIZADO_DEMO = 'neutralizado_demo'
    NAO_ENVIADO = 'nao_enviado'


@dataclass(frozen=True)
class ResultadoEnvioEmail:
    status: StatusEnvioEmail
    backend_chamado: bool
    resultado_backend: int | None


def _resolver_e_validar_contextos(*, ministerio=None, membro=None, igreja=None):
    """Resolve o Ministério e bloqueia contextos tenant ausentes ou conflitantes."""
    contextos_resolvidos = []

    if ministerio is not None:
        if getattr(ministerio, 'pk', None) is None:
            raise ValueError(
                'Ministerio fornecido nao possui identidade persistida valida (pk nulo).'
            )
        contextos_resolvidos.append(('ministerio', ministerio))

    if membro is not None:
        try:
            igreja_do_membro = membro.igreja
        except AttributeError as exc:
            raise ValueError(
                'Membro fornecido nao possui relacionamento com Igreja.'
            ) from exc
        if igreja_do_membro is None:
            raise ValueError('Membro fornecido nao esta vinculado a nenhuma Igreja.')

        try:
            ministerio_do_membro = igreja_do_membro.ministerio
        except AttributeError as exc:
            raise ValueError(
                'Igreja do membro nao possui relacionamento com Ministerio.'
            ) from exc
        if (
            ministerio_do_membro is None
            or getattr(ministerio_do_membro, 'pk', None) is None
        ):
            raise ValueError(
                'Nao foi possivel derivar Ministerio a partir do membro fornecido.'
            )
        contextos_resolvidos.append(('membro', ministerio_do_membro))

    if igreja is not None:
        try:
            ministerio_da_igreja = igreja.ministerio
        except AttributeError as exc:
            raise ValueError(
                'Igreja fornecida nao possui relacionamento com Ministerio.'
            ) from exc
        if (
            ministerio_da_igreja is None
            or getattr(ministerio_da_igreja, 'pk', None) is None
        ):
            raise ValueError(
                'Nao foi possivel derivar Ministerio a partir da igreja fornecida.'
            )
        contextos_resolvidos.append(('igreja', ministerio_da_igreja))

    if not contextos_resolvidos:
        raise ValueError(
            'Contexto de tenant ausente: informe ministerio, membro ou igreja.'
        )

    origem_referencia, ministerio_efetivo = contextos_resolvidos[0]
    for origem, contexto_ministerio in contextos_resolvidos[1:]:
        if contexto_ministerio.pk != ministerio_efetivo.pk:
            raise ValueError(
                f"Contextos conflitantes: origem '{origem_referencia}' aponta para "
                f"ministerio={ministerio_efetivo.pk}, mas origem '{origem}' aponta "
                f"para ministerio={contexto_ministerio.pk}. Possivel cross-tenant leak."
            )

    return ministerio_efetivo


def enviar_email_seguro(
    assunto,
    mensagem,
    destinatarios,
    *,
    ministerio=None,
    membro=None,
    igreja=None,
    html_message=None,
    from_email=None,
    fail_silently=False,
):
    """Executa ou neutraliza o dispatch externo conforme o tenant resolvido."""
    ministerio_efetivo = _resolver_e_validar_contextos(
        ministerio=ministerio,
        membro=membro,
        igreja=igreja,
    )

    if ministerio_efetivo.is_demo:
        logger.info(
            'E-mail neutralizado no tenant demo: ministerio=%s',
            ministerio_efetivo.pk,
        )
        return ResultadoEnvioEmail(
            status=StatusEnvioEmail.NEUTRALIZADO_DEMO,
            backend_chamado=False,
            resultado_backend=None,
        )

    resultado_backend = send_mail(
        assunto,
        mensagem,
        from_email or settings.DEFAULT_FROM_EMAIL,
        destinatarios,
        html_message=html_message,
        fail_silently=fail_silently,
    )
    status = (
        StatusEnvioEmail.ENVIADO
        if resultado_backend > 0
        else StatusEnvioEmail.NAO_ENVIADO
    )
    return ResultadoEnvioEmail(
        status=status,
        backend_chamado=True,
        resultado_backend=resultado_backend,
    )