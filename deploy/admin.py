"""Admin para deploy historico."""
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.http import JsonResponse

from core.admin_mixins import DateHierarchyMixin

from .models import DeployHistorico
from .views import (
    executar_deploy, 
    obter_mudancas_git, 
    obter_commits_desde_ultimo_deploy,
    obter_versao_atual,
    verificar_branch_correta,
    verificar_migrations_pendentes,
    verificar_sincronizacao_remote,
    obter_estatisticas_codigo
)
import subprocess


@admin.register(DeployHistorico)
class DeployHistoricoAdmin(DateHierarchyMixin, admin.ModelAdmin):
    list_display = ['versao', 'tipo_versao', 'usuario', 'data_deploy', 'status', 'tag_criada']
    list_filter = ['status', 'tipo_versao', 'data_deploy']
    search_fields = ['versao', 'descricao', 'commit_hash']
    readonly_fields = ['versao', 'usuario', 'data_deploy', 'status', 'log_execucao', 
                       'erro_detalhes', 'commit_hash', 'tag_criada', 'arquivos_modificados']
    date_hierarchy = 'data_deploy'  # Override mixin default
    
    fieldsets = (
        ('Informações da Versão', {
            'fields': ('versao', 'tipo_versao', 'descricao')
        }),
        ('Arquivos Modificados', {
            'fields': ('arquivos_modificados',),
            'classes': ('collapse',)
        }),
        ('Execução', {
            'fields': ('usuario', 'data_deploy', 'status', 'log_execucao', 'erro_detalhes')
        }),
        ('Git', {
            'fields': ('commit_hash', 'tag_criada')
        }),
    )
    
    def has_add_permission(self, request):
        # Não permitir adicionar manualmente - só via botão customizado
        return False
    
    def has_change_permission(self, request, obj=None):
        # Permitir visualização (necessário para aparecer no admin)
        return True
    
    def has_delete_permission(self, request, obj=None):
        # Superusuários podem deletar histórico antigo
        return request.user.is_superuser
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('nova-versao/', self.admin_site.admin_view(self.nova_versao_view), name='deploy_nova_versao'),
            path('obter-mudancas/', self.admin_site.admin_view(self.obter_mudancas_ajax), name='deploy_obter_mudancas'),
        ]
        return custom_urls + urls
    
    def nova_versao_view(self, request):
        """View para criar nova versão com formulário customizado"""
        
        # Apenas superusuários podem acessar
        if not request.user.is_superuser:
            messages.error(request, "Apenas superusuários podem realizar deploys.")
            return redirect('admin:deploy_deployhistorico_changelist')
        
        if request.method == 'POST':
            # Executar o deploy
            tipo_versao = request.POST.get('tipo_versao')
            descricao = request.POST.get('descricao')
            
            resultado = executar_deploy(
                tipo_versao=tipo_versao,
                descricao=descricao,
                usuario=request.user
            )
            
            if resultado['sucesso']:
                messages.success(request, f"✅ Deploy da versão {resultado['versao']} realizado com sucesso!")
                return redirect('admin:deploy_deployhistorico_changelist')
            else:
                messages.error(request, f"❌ Erro no deploy: {resultado['erro']}")
                return redirect('admin:deploy_nova_versao')
        
        # GET - Mostrar formulário
        # Obter mudanças automáticas do Git
        mudancas_git = obter_mudancas_git()
        commits_automaticos = obter_commits_desde_ultimo_deploy()
        
        # Executar validações pré-deploy
        versao_atual = obter_versao_atual()
        validacao_branch = verificar_branch_correta()
        validacao_migrations = verificar_migrations_pendentes()
        validacao_remote = verificar_sincronizacao_remote()
        estatisticas = obter_estatisticas_codigo()
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Nova Versão - Deploy Automatizado',
            'versao_atual': versao_atual,
            'validacao_branch': validacao_branch,
            'validacao_migrations': validacao_migrations,
            'validacao_remote': validacao_remote,
            'estatisticas': estatisticas,
            'mudancas_git': mudancas_git,
            'commits_automaticos': commits_automaticos,
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/deploy/nova_versao.html', context)
    
    def obter_mudancas_ajax(self, request):
        """AJAX endpoint para atualizar mudanças do Git"""
        if not request.user.is_superuser:
            return JsonResponse({'erro': 'Sem permissão'}, status=403)
        
        mudancas = obter_mudancas_git()
        return JsonResponse(mudancas)
    
    def changelist_view(self, request, extra_context=None):
        """Adicionar botão para nova versão no topo da lista"""
        extra_context = extra_context or {}
        extra_context['mostrar_botao_nova_versao'] = request.user.is_superuser
        return super().changelist_view(request, extra_context=extra_context)
