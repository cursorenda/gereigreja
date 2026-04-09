def modo_auditoria_ativo(request):
    """
    Helper para checar se o modo auditoria está ativo na sessão.
    """
    return bool(request.session.get('modo_auditoria', False))
