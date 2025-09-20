from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from comunicacao.models import NotificacaoEnviada

def is_admin_or_pastor(user):
    return user.is_superuser or user.groups.filter(name__in=["Pastor", "Administrador", "Admin Ministerio", "Lider Igreja"]).exists()

@login_required
@user_passes_test(is_admin_or_pastor)
def notificacoes_enviadas_view(request):
    notificacoes = NotificacaoEnviada.objects.order_by('-data_envio')[:200]
    return render(request, 'core/notificacoes_enviadas.html', {'notificacoes': notificacoes})
