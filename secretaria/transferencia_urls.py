from django.urls import path

from . import transferencia_views


urlpatterns = [
    path('transferencias/solicitar/', transferencia_views.solicitar_transferencia, name='solicitar_transferencia'),
    path('transferencias/', transferencia_views.lista_transferencias, name='lista_transferencias'),
    path('transferencias/<int:pk>/aprovar/', transferencia_views.aprovar_transferencia, name='aprovar_transferencia'),
    path('transferencias/<int:pk>/recusar/', transferencia_views.recusar_transferencia, name='recusar_transferencia'),
    path('transferencias/<int:pk>/cancelar/', transferencia_views.cancelar_transferencia, name='cancelar_transferencia'),
]
