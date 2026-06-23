from django.conf import settings


def user_is_dev_finance(user):
    if not user or not user.is_authenticated or not user.is_superuser:
        return False

    configured = getattr(settings, 'DEV_FINANCEIRO_USERNAMES', []) or []
    configured = [u.strip() for u in configured if str(u).strip()]
    if not configured:
        # Fallback seguro para ambiente sem configuracao: apenas superuser.
        return True

    return user.username in configured
