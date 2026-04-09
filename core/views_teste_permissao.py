from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from contas.constants import ADMIN_MINISTERIO, user_tem_grupo
from core.decorators import user_passes_test_or_403

@login_required
def view_livre(request):
    return HttpResponse('Acesso livre OK')

from contas.constants import user_has_permission_level_or_higher
@user_passes_test_or_403(lambda u: u.is_authenticated and user_has_permission_level_or_higher(u, ADMIN_MINISTERIO))
def view_admin_ministerio(request):
    return HttpResponse('Acesso permitido para Admin Ministerio')
