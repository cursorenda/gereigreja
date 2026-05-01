from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.demo_login_view, name='demo_login'),
    path('dashboard/', views.demo_dashboard_view, name='demo_dashboard'),
    path('trocar-perfil/', views.demo_trocar_perfil_view, name='demo_trocar_perfil'),
    path('resetar/', views.demo_reset_view, name='demo_reset'),
]
