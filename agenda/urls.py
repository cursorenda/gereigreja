from django.urls import path

from .views import agenda_view, agenda_eventos_json, criar_evento, detalhe_evento, editar_evento, excluir_evento

urlpatterns = [
    path('', agenda_view, name='agenda'),
    path('novo/', criar_evento, name='criar_evento'),
    path('evento/<int:pk>/', detalhe_evento, name='detalhe_evento'),
    path('evento/<int:pk>/editar/', editar_evento, name='editar_evento'),
    path('evento/<int:pk>/excluir/', excluir_evento, name='excluir_evento'),
    path('api/eventos/', agenda_eventos_json, name='agenda_eventos_json'),
]
