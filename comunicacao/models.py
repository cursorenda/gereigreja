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


class WhatsAppConfiguracaoGlobal(models.Model):
    """
    Configuracao WAHA no nivel do ministerio.
    O admin configura uma vez: URL do servidor WAHA e API Key.
    Cada congregacao herda esses dados e so precisa informar seu numero e escanear QR.
    """
    ministerio = models.OneToOneField(
        Ministerio,
        on_delete=models.CASCADE,
        related_name='whatsapp_config_global',
        verbose_name='Ministerio',
    )
    waha_base_url = models.URLField(default='http://localhost:3000', verbose_name='URL base WAHA (servidor)')
    waha_api_key = models.CharField(max_length=255, blank=True, null=True, verbose_name='API Key WAHA')
    ativo = models.BooleanField(default=False, verbose_name='Integracao WhatsApp ativa')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuracao Global WhatsApp'
        verbose_name_plural = 'Configuracoes Globais WhatsApp'

    def __str__(self):
        return f"Config Global WhatsApp - {self.ministerio.nome_fantasia}"


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
    # session_name: se vazio, e gerado automaticamente a partir do slug da igreja
    session_name = models.CharField(max_length=120, blank=True, null=True, verbose_name='Session WAHA (auto se vazio)')
    # URL e Key opcionais: se vazios, herda da configuracao global do ministerio
    waha_base_url = models.URLField(blank=True, null=True, verbose_name='URL base WAHA (deixe vazio para herdar do ministerio)')
    waha_api_key = models.CharField(max_length=255, blank=True, null=True, verbose_name='API Key WAHA (deixe vazio para herdar do ministerio)')
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

    def get_session_name(self):
        """Retorna session_name ou gera automaticamente a partir do slug da igreja."""
        if self.session_name:
            return self.session_name
        import re
        slug = re.sub(r'[^a-z0-9]', '-', self.igreja.nome_igreja.lower())
        slug = re.sub(r'-+', '-', slug).strip('-')
        return f"igreja-{slug}"[:60]

    @property
    def waha_url_efetiva(self):
        """URL do servidor WAHA: override local -> override global -> settings (plataforma)."""
        if self.waha_base_url:
            return self.waha_base_url
        try:
            global_url = self.ministerio.whatsapp_config_global.waha_base_url
            # Ignora o valor padrao local para permitir uso da URL real via ambiente.
            if global_url and global_url.rstrip('/') not in ('http://localhost:3000', 'http://127.0.0.1:3000'):
                return global_url
        except Exception:
            pass
        return getattr(settings, 'WAHA_BASE_URL', 'http://localhost:3000')

    @property
    def waha_key_efetiva(self):
        """API Key WAHA: override local -> override global -> settings (plataforma)."""
        if self.waha_api_key:
            return self.waha_api_key
        try:
            global_key = self.ministerio.whatsapp_config_global.waha_api_key
            if global_key:
                return global_key
        except Exception:
            pass
        key = getattr(settings, 'WAHA_API_KEY', '')
        return key if key else None


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


