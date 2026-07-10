from django.urls import path

from .views import HinoCatalogoView, HinoDetalheView

app_name = 'hinario'

urlpatterns = [
    path('', HinoCatalogoView.as_view(), name='lista'),
    path('hino/<str:colecao>/<int:numero>/', HinoDetalheView.as_view(), name='detalhe'),
]
