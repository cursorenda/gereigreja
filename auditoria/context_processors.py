def modo_auditoria_flag(request):
    return {'modo_auditoria_ativo': bool(request.session.get('modo_auditoria', False))}