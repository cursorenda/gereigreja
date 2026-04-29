from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from configuracao.models import Ministerio, Igreja


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
