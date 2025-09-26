from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
	path('novo/', views.criar_evento_profissional, name='criar_evento'),
	path('lista/', views.lista_eventos, name='lista_eventos'),
	path('detalhe/<int:pk>/', views.detalhe_evento_profissional, name='detalhe_evento'),
	path('editar/<int:pk>/', views.editar_evento_profissional, name='editar_evento'),
	path('excluir/<int:pk>/', views.excluir_evento_profissional, name='excluir_evento'),
	path('presenca/<int:pk>/', views.marcar_presenca_evento, name='marcar_presenca'),
	path('exportar_participantes_excel/<int:pk>/', views.exportar_participantes_excel, name='exportar_participantes_excel'),
]
