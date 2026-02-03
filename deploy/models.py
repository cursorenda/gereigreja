from django.db import models
from django.contrib.auth.models import User


class DeployHistorico(models.Model):
    """Histórico de deploys realizados"""
    
    TIPO_VERSAO_CHOICES = [
        ('patch', 'Patch (1.0.X) - Correções de bugs, pequenos ajustes'),
        ('minor', 'Minor (1.X.0) - Novas funcionalidades, melhorias'),
        ('major', 'Major (X.0.0) - Mudanças significativas, breaking changes'),
    ]
    
    STATUS_CHOICES = [
        ('sucesso', 'Sucesso'),
        ('erro', 'Erro'),
        ('em_andamento', 'Em andamento'),
    ]
    
    versao = models.CharField(max_length=20, verbose_name="Versão")
    tipo_versao = models.CharField(max_length=10, choices=TIPO_VERSAO_CHOICES, verbose_name="Tipo de Versão")
    descricao = models.TextField(verbose_name="Descrição das Mudanças")
    arquivos_modificados = models.TextField(blank=True, verbose_name="Arquivos Modificados (Auto)")
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuário")
    data_deploy = models.DateTimeField(auto_now_add=True, verbose_name="Data do Deploy")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='em_andamento', verbose_name="Status")
    log_execucao = models.TextField(blank=True, verbose_name="Log de Execução")
    erro_detalhes = models.TextField(blank=True, verbose_name="Detalhes do Erro")
    
    commit_hash = models.CharField(max_length=40, blank=True, verbose_name="Hash do Commit")
    tag_criada = models.CharField(max_length=20, blank=True, verbose_name="Tag Criada")
    
    class Meta:
        verbose_name = "Deploy"
        verbose_name_plural = "Histórico de Deploys"
        ordering = ['-data_deploy']
    
    def __str__(self):
        return f"{self.versao} - {self.data_deploy.strftime('%d/%m/%Y %H:%M')}"
