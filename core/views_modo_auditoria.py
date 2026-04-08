from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages

@login_required
def alternar_modo_auditoria(request):
    if not request.user.is_superuser:
        messages.error(request, "Apenas superusuários podem alternar o modo auditoria.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    flag = request.session.get('modo_auditoria', False)
    request.session['modo_auditoria'] = not flag
    request.session.modified = True
    if not flag:
        messages.info(request, "Modo Auditoria ativado: navegação somente leitura.")
    else:
        messages.info(request, "Modo Auditoria desativado: permissões normais restauradas.")
    return redirect(request.META.get('HTTP_REFERER', '/'))
