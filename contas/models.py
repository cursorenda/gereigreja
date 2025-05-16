# c:\Gereigreja\contas\models.py
from django.db import models
from django.conf import settings # Para referenciar User
from django.utils import timezone
import uuid # Para gerar tokens únicos

# Importar modelos de outros apps
from configuracao.models import Organizacao

class Convite(models.Model):
    """ Modelo para armazenar convites enviados para novos usuários se juntarem a uma organização. """
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('aceito', 'Aceito'),
        ('expirado', 'Expirado'),
        ('cancelado', 'Cancelado'), # Opcional: Se o admin puder cancelar
    )

    email_convidado = models.EmailField(
        max_length=254,
        verbose_name="E-mail do Convidado"
    )
    remetente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # Se o remetente for excluído, o convite também é
        related_name='convites_enviados',
        verbose_name="Enviado por"
    )
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.CASCADE, # Se a organização for excluída, os convites também são
        related_name='convites_recebidos',
        verbose_name="Organização"
    )
    token = models.UUIDField(
        default=uuid.uuid4, # Gera um UUID único automaticamente
        editable=False, # Não pode ser editado
        unique=True, # Garante que cada token seja único
        verbose_name="Token Único"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name="Status"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_aceite = models.DateTimeField(
        null=True, blank=True, # Preenchido quando o convite for aceito
        verbose_name="Data de Aceite"
    )
    # Opcional: Adicionar data de expiração
    # data_expiracao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Expiração")

    def __str__(self):
        return f"Convite para {self.email_convidado} ({self.organizacao.nome_fantasia}) - {self.get_status_display()}"

    class Meta:
        verbose_name = "Convite"
        verbose_name_plural = "Convites"
        ordering = ['-data_criacao'] # Ordenar por mais recente

    def is_valido(self):
        """ Verifica se o convite está pendente e (opcionalmente) não expirado. """
        # Adicionar lógica de expiração aqui se usar data_expiracao
        # expirado = self.data_expiracao and self.data_expiracao < timezone.now()
        # return self.status == 'pendente' and not expirado
        return self.status == 'pendente'

