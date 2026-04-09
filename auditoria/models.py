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
