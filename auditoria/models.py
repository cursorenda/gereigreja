"""
Modelos de Auditoria - Sistema de Logs de Permissões e Acesso
"""
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from configuracao.models import Ministerio, Igreja


class PermissionChangeLog(models.Model):
    """
    Registra todas as mudanças de permissões (grupos) dos usuários.
    Permite rastrear quem alterou, quando e qual foi a mudança.
    """
    ACAO_CHOICES = [
        ('ADD', 'Adicionado ao Grupo'),
        ('REMOVE', 'Removido do Grupo'),
        ('EDIT', 'Permissões Editadas'),
        ('CREATE', 'Grupo Criado'),
        ('DELETE', 'Grupo Deletado'),
    ]
    
    usuario_afetado = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='logs_permissao_afetado',
        verbose_name='Usuário Afetado',
        help_text='Usuário que teve suas permissões alteradas'
    )
    
    grupo = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Grupo',
        help_text='Grupo de permissão envolvido na alteração'
    )
    
    acao = models.CharField(
        max_length=10,
        choices=ACAO_CHOICES,
        verbose_name='Ação',
        help_text='Tipo de alteração realizada'
    )
    
    usuario_executor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_permissao_executor',
        verbose_name='Executado Por',
        help_text='Usuário que realizou a alteração'
    )
    
    data_hora = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data/Hora',
        db_index=True,
        help_text='Momento em que a alteração foi realizada'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP',
        help_text='Endereço IP de origem da alteração'
    )
    
    observacao = models.TextField(
        blank=True,
        verbose_name='Observação',
        help_text='Informações adicionais sobre a alteração'
    )
    
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Ministério',
        help_text='Ministério ao qual o log pertence'
    )
    
    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Log de Alteração de Permissão'
        verbose_name_plural = 'Logs de Alterações de Permissões'
        indexes = [
            models.Index(fields=['-data_hora', 'usuario_afetado']),
            models.Index(fields=['ministerio', '-data_hora']),
        ]
    
    def __str__(self):
        return f"{self.get_acao_display()}: {self.usuario_afetado.username} - {self.grupo} ({self.data_hora.strftime('%d/%m/%Y %H:%M')})"
    
    @property
    def nivel_hierarquia(self):
        """Retorna o nível hierárquico do grupo (se existir)"""
        if self.grupo:
            from contas.constants import get_user_permission_level, HIERARQUIA_GRUPOS
            try:
                return HIERARQUIA_GRUPOS.index(self.grupo.name)
            except ValueError:
                return None
        return None


class AccessDeniedLog(models.Model):
    """
    Registra tentativas de acesso negado.
    Útil para identificar problemas de permissão e tentativas de acesso não autorizado.
    """
    TIPO_CHOICES = [
        ('VIEW', 'Acesso a View'),
        ('OBJECT', 'Acesso a Objeto'),
        ('ACTION', 'Execução de Ação'),
        ('API', 'Acesso a API'),
    ]
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='logs_acesso_negado',
        verbose_name='Usuário',
        help_text='Usuário que tentou acessar'
    )
    
    tipo_acesso = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de Acesso',
        help_text='Tipo de recurso que foi tentado acessar'
    )
    
    recurso = models.CharField(
        max_length=255,
        verbose_name='Recurso',
        help_text='Nome ou identificador do recurso (view, model, action)'
    )
    
    permissao_requerida = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Permissão Requerida',
        help_text='Permissão ou grupo necessário para o acesso'
    )
    
    igreja_tentada = models.ForeignKey(
        Igreja,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Igreja',
        help_text='Igreja que foi tentada acessar (se aplicável)'
    )
    
    data_hora = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data/Hora',
        db_index=True,
        help_text='Momento da tentativa de acesso'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP',
        help_text='Endereço IP de origem'
    )
    
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='User Agent',
        help_text='Informações do navegador/cliente'
    )
    
    url_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='URL',
        help_text='URL completa que foi tentada acessar'
    )
    
    metodo_http = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Método HTTP',
        help_text='GET, POST, PUT, DELETE, etc.'
    )
    
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Ministério',
        help_text='Ministério ao qual o log pertence'
    )
    
    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Log de Acesso Negado'
        verbose_name_plural = 'Logs de Acessos Negados'
        indexes = [
            models.Index(fields=['-data_hora', 'usuario']),
            models.Index(fields=['ministerio', '-data_hora']),
            models.Index(fields=['tipo_acesso', '-data_hora']),
        ]
    
    def __str__(self):
        return f"Acesso Negado: {self.usuario.username} - {self.recurso} ({self.data_hora.strftime('%d/%m/%Y %H:%M')})"
    
    @property
    def grupos_usuario(self):
        """Retorna os grupos do usuário no momento do log"""
        return ', '.join(self.usuario.groups.values_list('name', flat=True))


class AuditSession(models.Model):
    """
    Registra sessões de auditoria/navegação dos usuários.
    Permite rastrear tempo de uso e padrões de navegação.
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessoes_auditoria',
        verbose_name='Usuário'
    )
    
    login_data_hora = models.DateTimeField(
        default=timezone.now,
        verbose_name='Login',
        db_index=True
    )
    
    logout_data_hora = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Logout'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP'
    )
    
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='User Agent'
    )
    
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Ministério'
    )
    
    igreja_ativa = models.ForeignKey(
        Igreja,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Igreja Ativa',
        help_text='Igreja selecionada durante a sessão'
    )
    
    paginas_visitadas = models.IntegerField(
        default=0,
        verbose_name='Páginas Visitadas',
        help_text='Contador de páginas acessadas na sessão'
    )
    
    class Meta:
        ordering = ['-login_data_hora']
        verbose_name = 'Sessão de Auditoria'
        verbose_name_plural = 'Sessões de Auditoria'
        indexes = [
            models.Index(fields=['-login_data_hora', 'usuario']),
            models.Index(fields=['ministerio', '-login_data_hora']),
        ]
    
    def __str__(self):
        return f"Sessão: {self.usuario.username} - {self.login_data_hora.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def duracao(self):
        """Retorna a duração da sessão"""
        if self.logout_data_hora:
            return self.logout_data_hora - self.login_data_hora
        return timezone.now() - self.login_data_hora
    
    @property
    def ativa(self):
        """Verifica se a sessão ainda está ativa"""
        return self.logout_data_hora is None
