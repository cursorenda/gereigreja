from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views # Importar as views de autenticação
from django.views.generic import TemplateView # Importar TemplateView
from django.conf import settings
from django.conf.urls.static import static
from secretaria import views as secretaria_views


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('secretaria.urls')), # REMOVER ESTA LINHA DUPLICADA
    path('financeiro/', include(('financeiro.urls', 'financeiro'), namespace='financeiro')),
    path('eventos/', include(('eventos.urls', 'eventos'), namespace='eventos')),
    path('comunicacao/', include(('comunicacao.urls', 'comunicacao'), namespace='comunicacao')),
    path('configuracao/', include('configuracao.urls')),

    path('accounts/', include('django.contrib.auth.urls')), # Inclui as URLs padrão de autenticação do Django, incluindo password_reset
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'), #Exemplo usando a view padrão do Django
    path('contas/', include('contas.urls', namespace='contas')),
    # Novas URLs para Política de Privacidade e Termos e Condições
    path('politica-privacidade/', TemplateView.as_view(template_name='core/politica_privacidade.html'), name='politica_privacidade'),
    path('termos-condicoes/', TemplateView.as_view(template_name='core/termos_condicoes.html'), name='termos_condicoes'),
    path('', include(('secretaria.urls', 'secretaria'), namespace='secretaria')), # Adiciona namespace

]

if settings.DEBUG:
    # A linha abaixo já deve existir para MEDIA_ROOT
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
