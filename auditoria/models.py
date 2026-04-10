from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone


class PermissionChangeLog(models.Model):
    ACAO_CHOICES = [
        ('ADD', 'Adicionado ao Grupo'),
        ('REMOVE', 'Removido do Grupo'),
        ('EDIT', 'Permissoes Editadas'),
        ('CREATE', 'Grupo Criado'),
        ('DELETE', 'Grupo Deletado'),
    ]

    usuario_afetado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='logs_permissao_afetado',
        verbose_name='Usuario Afetado',
    )
    grupo = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Grupo',
    )
    acao = models.CharField(
        max_length=10,
        choices=ACAO_CHOICES,
        verbose_name='Acao',
    )
    usuario_executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_permissao_executor',
        verbose_name='Executado Por',
    )
    data_hora = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name='Data/Hora',
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP',
    )
    observacao = models.TextField(
        blank=True,
        verbose_name='Observacao',
    )
    ministerio = models.ForeignKey(
        'configuracao.Ministerio',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Ministerio',
    )

    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Log de Alteracao de Permissao'
        verbose_name_plural = 'Logs de Alteracoes de Permissoes'
        indexes = [
            models.Index(fields=['-data_hora', 'usuario_afetado']),
            models.Index(fields=['ministerio', '-data_hora']),
        ]

    def __str__(self):
        grupo = self.grupo.name if self.grupo else 'sem grupo'
        data_hora = self.data_hora.strftime('%d/%m/%Y %H:%M')
        return f'{self.acao}: {self.usuario_afetado} - {grupo} ({data_hora})'


class AccessDeniedLog(models.Model):
    TIPO_CHOICES = [
        ('VIEW', 'Acesso a View'),
        ('OBJECT', 'Acesso a Objeto'),
        ('ACTION', 'Execucao de Acao'),
        ('API', 'Acesso a API'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='logs_acesso_negado',
        verbose_name='Usuario',
    )
    tipo_acesso = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de Acesso',
    )
    recurso = models.CharField(
        max_length=255,
        verbose_name='Recurso',
    )
    permissao_requerida = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Permissao Requerida',
    )
    igreja_tentada = models.ForeignKey(
        'configuracao.Igreja',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Igreja',
    )
    data_hora = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name='Data/Hora',
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP',
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='User Agent',
    )
    url_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='URL',
    )
    metodo_http = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Metodo HTTP',
    )
    ministerio = models.ForeignKey(
        'configuracao.Ministerio',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Ministerio',
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
        data_hora = self.data_hora.strftime('%d/%m/%Y %H:%M')
        return f'Acesso Negado: {self.usuario} - {self.recurso} ({data_hora})'


class AuditSession(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessoes_auditoria',
        verbose_name='Usuario',
    )
    login_data_hora = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name='Login',
    )
    logout_data_hora = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Logout',
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP',
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='User Agent',
    )
    ministerio = models.ForeignKey(
        'configuracao.Ministerio',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Ministerio',
    )
    igreja_ativa = models.ForeignKey(
        'configuracao.Igreja',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Igreja Ativa',
    )
    paginas_visitadas = models.IntegerField(
        default=0,
        verbose_name='Paginas Visitadas',
    )

    class Meta:
        ordering = ['-login_data_hora']
        verbose_name = 'Sessao de Auditoria'
        verbose_name_plural = 'Sessoes de Auditoria'
        indexes = [
            models.Index(fields=['-login_data_hora', 'usuario']),
            models.Index(fields=['ministerio', '-login_data_hora']),
        ]

    def __str__(self):
        login = self.login_data_hora.strftime('%d/%m/%Y %H:%M')
        return f'Sessao: {self.usuario} - {login}'

    @property
    def duracao(self):
        if self.logout_data_hora:
            return self.logout_data_hora - self.login_data_hora
        return timezone.now() - self.login_data_hora

    @property
    def ativa(self):
        return self.logout_data_hora is None
