from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from notificacoes.models import NotificacaoEnviada
from contas.constants import ADMIN_MINISTERIO, PASTOR_REGIONAL
from core.decorators import user_passes_test_or_403  # Importar decorator que lança 403

def is_admin_or_pastor(user):
    from contas.constants import user_has_permission_level_or_higher, PASTOR_LOCAL
    return user_has_permission_level_or_higher(user, PASTOR_LOCAL)

@login_required
@user_passes_test_or_403(is_admin_or_pastor)
def notificacoes_enviadas_view(request):
    notificacoes = NotificacaoEnviada.objects.order_by('-data_envio')[:200]
    return render(request, 'core/notificacoes_enviadas.html', {'notificacoes': notificacoes})
