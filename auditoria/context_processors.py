def modo_auditoria_flag(request):
    """
    Adiciona o flag de modo auditoria ao contexto global.
    """
    return {'modo_auditoria_ativo': bool(request.session.get('modo_auditoria', False))}
