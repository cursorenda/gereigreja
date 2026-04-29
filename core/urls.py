from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views # Importar as views de autenticação
from django.views.generic import TemplateView, RedirectView # Importar TemplateView e RedirectView
from django.conf import settings
from django.conf.urls.static import static

# Importar a view da landing page

from contas.views import LandingPageView

from core.views import notificacoes_enviadas_view
from core.backup_views import backup_urls
from core.views_painel_permissoes import painel_permissoes_view
from core.views_teste_permissao import view_livre, view_admin_ministerio
from painel_testes.admin import painel_pytest_view
from configuracao.admin_dashboard import dashboard_desenvolvedor, executar_comando
from configuracao.admin_metrics import metricas_produto
from django.contrib.admin.views.decorators import staff_member_required
from auditoria.admin_site import auditoria_admin_site


urlpatterns = [
    # Redirecionar /admin/deploy/ para o histórico de deploys (DEVE VIR ANTES DO admin/)
    path('admin/deploy/', RedirectView.as_view(pattern_name='admin:deploy_deployhistorico_changelist', permanent=False)),
    # Dashboard do Desenvolvedor (ANTES do admin.site.urls)
    path('admin/dashboard-dev/', staff_member_required(dashboard_desenvolvedor), name='admin_dashboard_desenvolvedor'),
    path('admin/executar-comando/', staff_member_required(executar_comando), name='admin_executar_comando'),
    # Métricas de Produto/Uso (ANTES do admin.site.urls)
    path('admin/api/metricas-produto/', staff_member_required(metricas_produto), name='admin_metricas_produto'),
    # Painel de testes de permissoes/hierarquias
    path('admin/painel-permissoes/', staff_member_required(painel_permissoes_view), name='admin_painel_permissoes'),
    # Painel de testes unitários (pytest)
    path('admin/painel-testes/pytest/', admin.site.admin_view(painel_pytest_view), name='admin_painel_pytest'),
    path('admin-auditoria/', auditoria_admin_site.urls),
    # Rotas de teste de permissao
    path('teste-permissao/livre/', view_livre, name='teste_permissao_livre'),
    path('teste-permissao/admin-ministerio/', view_admin_ministerio, name='teste_permissao_admin_ministerio'),
    path('admin/', admin.site.urls),
    path('financeiro/', include(('financeiro.urls', 'financeiro'), namespace='financeiro')),
    path('eventos/', include(('eventos.urls', 'eventos'), namespace='eventos')),
    path('comunicacao/', include(('comunicacao.urls', 'comunicacao'), namespace='comunicacao')),
    path('notificacoes/', include(('notificacoes.urls', 'notificacoes'), namespace='notificacoes')),
    path('configuracao/', include('configuracao.urls')),
    path('suporte/', include('suporte.urls', namespace='suporte')),

    path('accounts/', include('django.contrib.auth.urls')), # Inclui as URLs padrão de autenticação do Django, incluindo password_reset
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'), #Exemplo usando a view padrão do Django
    path('contas/', include('contas.urls', namespace='contas')),
    # Novas URLs para Política de Privacidade e Termos e Condições
    path('politica-privacidade/', TemplateView.as_view(template_name='core/politica_privacidade.html'), name='politica_privacidade'),
    path('termos-condicoes/', TemplateView.as_view(template_name='core/termos_condicoes.html'), name='termos_condicoes'),

    # A URL raiz '/' agora aponta para a página de vendas.
    path('', LandingPageView.as_view(), name='landing_page'),
    # O sistema interno (secretaria, etc.) agora começa com '/secretaria/'
    path('secretaria/', include(('secretaria.urls', 'secretaria'), namespace='secretaria')),
    path('agenda/', include(('agenda.urls', 'agenda'), namespace='agenda')),

    # Página de acompanhamento de notificações enviadas
    path('notificacoes-enviadas/', notificacoes_enviadas_view, name='notificacoes_enviadas'),

    # Escola Bíblica Dominical
    path('escola_biblica/', include(('escola_biblica.urls', 'escola_biblica'), namespace='escola_biblica')),
    path('auditoria/', include(('auditoria.urls', 'auditoria'), namespace='auditoria')),
    # URLs de backup
    *backup_urls,
]


if settings.DEBUG:
    # A linha abaixo já deve existir para MEDIA_ROOT
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
    # Em produção, o servidor web (nginx, apache, etc.) é que serve os arquivos de mídia
    # Em desenvolvimento, o Django pode servir, mas não é eficiente
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
