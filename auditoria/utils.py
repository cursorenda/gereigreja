def rodar_auditoria_permissoes():
    # Lógica simplificada: pode importar e rodar o comando existente
    from django.core.management import call_command
    from io import StringIO
    import sys
    out = StringIO()
    call_command('auditar_permissoes', stdout=out)
    return out.getvalue()

def modo_auditoria_ativo(request):
    """
    Helper para checar se o modo auditoria está ativo na sessão.
    """
    return bool(request.session.get('modo_auditoria', False))
