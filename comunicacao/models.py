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


class WhatsAppConfiguracao(models.Model):
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        related_name='whatsapp_configuracoes',
        verbose_name='Ministerio',
    )
    igreja = models.OneToOneField(
        Igreja,
        on_delete=models.CASCADE,
        related_name='whatsapp_configuracao',
        verbose_name='Congregacao/Igreja',
    )
    ativo = models.BooleanField(default=False, verbose_name='Ativo')
    numero_envio = models.CharField(max_length=20, verbose_name='Numero WhatsApp de envio')
    remetente_nome = models.CharField(max_length=120, blank=True, null=True, verbose_name='Nome do remetente')
    session_name = models.CharField(max_length=120, verbose_name='Session WAHA')
    waha_base_url = models.URLField(default='http://localhost:3000', verbose_name='URL base WAHA')
    waha_api_key = models.CharField(max_length=255, blank=True, null=True, verbose_name='API Key WAHA')
    webhook_token = models.CharField(max_length=80, blank=True, null=True, verbose_name='Token webhook')
    auto_aniversariantes = models.BooleanField(default=True, verbose_name='Automacao aniversariantes')
    auto_novos_membros = models.BooleanField(default=True, verbose_name='Automacao novos membros')
    auto_contribuicoes = models.BooleanField(default=False, verbose_name='Automacao agradecimento dizimo')
    auto_lembrete_eventos = models.BooleanField(default=False, verbose_name='Automacao lembrete eventos')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuracao WhatsApp'
        verbose_name_plural = 'Configuracoes WhatsApp'
        ordering = ['igreja__nome_igreja']

    def __str__(self):
        return f"WhatsApp {self.igreja.nome_igreja}"


class WhatsAppMensagemLog(models.Model):
    TIPO_CHOICES = [
        ('manual', 'Manual'),
        ('aniversario', 'Aniversario'),
        ('novo_membro', 'Novo membro'),
        ('dizimo', 'Agradecimento dizimo'),
        ('evento', 'Lembrete evento'),
        ('webhook', 'Recebido webhook'),
        ('outro', 'Outro'),
    ]
    STATUS_CHOICES = [
        ('sucesso', 'Sucesso'),
        ('erro', 'Erro'),
        ('recebido', 'Recebido'),
    ]

    ministerio = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='whatsapp_logs')
    igreja = models.ForeignKey(Igreja, on_delete=models.SET_NULL, null=True, blank=True, related_name='whatsapp_logs')
    membro = models.ForeignKey('secretaria.Pessoa', on_delete=models.SET_NULL, null=True, blank=True, related_name='whatsapp_logs')
    configuracao = models.ForeignKey(
        WhatsAppConfiguracao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='outro')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sucesso')
    telefone_destino = models.CharField(max_length=20)
    chat_id = models.CharField(max_length=64, blank=True, null=True)
    mensagem = models.TextField()
    resposta_waha = models.JSONField(blank=True, null=True)
    erro = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log WhatsApp'
        verbose_name_plural = 'Logs WhatsApp'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.telefone_destino} ({self.get_status_display()})"


