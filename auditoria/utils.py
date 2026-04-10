from django.core.management import call_command
from io import StringIO


def rodar_auditoria_permissoes():
    output = StringIO()
    call_command('auditar_permissoes', stdout=output)
    return output.getvalue()


def modo_auditoria_ativo(request):
    return bool(request.session.get('modo_auditoria', False))