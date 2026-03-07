from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from comunicacao.models import NotificacaoEnviada
from contas.constants import ADMIN_MINISTERIO, PASTOR_REGIONAL
from core.decorators import user_passes_test_or_403  # Importar decorator que lança 403

def is_admin_or_pastor(user):
    return user.is_superuser or user.groups.filter(name__in=["Pastor", "Administrador", ADMIN_MINISTERIO, PASTOR_REGIONAL]).exists()

@login_required
@user_passes_test_or_403(is_admin_or_pastor)
def notificacoes_enviadas_view(request):
    notificacoes = NotificacaoEnviada.objects.order_by('-data_envio')[:200]
    return render(request, 'core/notificacoes_enviadas.html', {'notificacoes': notificacoes})
