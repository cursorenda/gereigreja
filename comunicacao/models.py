from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from configuracao.models import Ministerio, Igreja

# Crie seus modelos aqui.

class Aviso(models.Model):
    """
    Modelo para representar um aviso ou anúncio.
    """
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        related_name='avisos_comunicacao',
        verbose_name="Ministério"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título do Aviso")
    conteudo = models.TextField(verbose_name="Conteúdo do Aviso")
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='avisos_criados',
        verbose_name="Autor"
    )
    igrejas_destino = models.ManyToManyField(
        Igreja,
        blank=True, # Pode ser um aviso para toda a ministério
        related_name='avisos_recebidos',
        verbose_name="Igrejas de Destino",
        help_text="Selecione as igrejas específicas para este aviso. Deixe em branco se for para toda a ministério."
    )
    data_publicacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Publicação")
    data_expiracao = models.DateField(null=True, blank=True, verbose_name="Data de Expiração (Opcional)", help_text="O aviso não será mais exibido após esta data.")
    publicado = models.BooleanField(default=True, verbose_name="Publicado")

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"
        ordering = ['-data_publicacao']


class Notificacao(models.Model):
    """
    Modelo para representar uma notificação para um usuário específico.
    """
    TIPO_CHOICES = [
        ('info', 'Informação'),
        ('aviso', 'Novo Aviso'),
        ('financeiro', 'Financeiro'),
        ('membro', 'Membro'),
        ('alerta', 'Alerta'),
        ('sucesso', 'Sucesso'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificacoes',
        verbose_name="Usuário Destino"
    )
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        related_name='notificacoes_ministerio',
        verbose_name="Ministério"
    )
    message = models.TextField(verbose_name="Mensagem")
    notification_type = models.CharField(max_length=20, choices=TIPO_CHOICES, default='info', verbose_name="Tipo")
    is_read = models.BooleanField(default=False, verbose_name="Lida?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criada Em")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="URL de Destino", help_text="Link para a página relacionada à notificação.")

    # Campos para GenericForeignKey (opcional, para vincular a qualquer modelo)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-created_at']


# --- Notificações Enviadas por E-mail/Sistema ---
class NotificacaoEnviada(models.Model):
    TIPO_CHOICES = [
        ('evento', 'Evento'),
        ('aniversario', 'Aniversário'),
        ('outro', 'Outro'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    destinatario = models.EmailField()
    data_envio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.titulo} ({self.destinatario})"
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.titulo} ({self.destinatario})"