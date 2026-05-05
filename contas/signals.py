from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def registrar_primeiro_login_funil(sender, request, user, **kwargs):
    """Registra primeiro_login no funil na primeira autenticação de um ministério."""
    try:
        from configuracao.models import EventoFunil
        from configuracao.services_assinatura import obter_ministerio_do_usuario, registrar_evento_funil

        ministerio = obter_ministerio_do_usuario(user)
        if not ministerio:
            return

        ja_registrado = EventoFunil.objects.filter(
            tipo='primeiro_login',
            ministerio=ministerio,
        ).exists()

        if not ja_registrado:
            registrar_evento_funil(
                'primeiro_login',
                ministerio=ministerio,
                extra={'user_id': user.id, 'origem': 'auth_login'},
            )
    except Exception:
        # Tracking nunca deve quebrar o fluxo de autenticação.
        return
