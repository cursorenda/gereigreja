# c:\Gereigreja\contas\models.py
from django.db import models
from django.conf import settings # Para referenciar User
from django.utils import timezone
import uuid # Para gerar tokens únicos

# Importar modelos de outros apps
from configuracao.models import Ministerio

class Convite(models.Model):
    """ Modelo para armazenar convites enviados para novos usuários se juntarem a uma ministério. """
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
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE, # Se a ministério for excluída, os convites também são
        related_name='convites_recebidos',
        verbose_name="Ministério"
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
        return f"Convite para {self.email_convidado} ({self.ministerio.nome_fantasia}) - {self.get_status_display()}"

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


class NotaUsuario(models.Model):
    """ Modelo para armazenar anotações pessoais de cada usuário no dashboard. """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nota_pessoal',
        verbose_name="Usuário"
    )
    conteudo = models.TextField(
        blank=True,
        default='',
        verbose_name="Conteúdo da Nota",
        help_text="Anotações pessoais do usuário (privadas)"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    def __str__(self):
        return f"Nota de {self.usuario.get_full_name() or self.usuario.username}"

    class Meta:
        verbose_name = "Nota do Usuário"
        verbose_name_plural = "Notas dos Usuários"
        ordering = ['-atualizado_em']


class ConsentimentoLGPD(models.Model):
    """
    Modelo para registrar consentimentos de termos de uso e política de privacidade (LGPD).
    
    Armazena quando e como o usuário aceitou os termos, incluindo IP e versão dos documentos.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consentimentos_lgpd',
        verbose_name="Usuário"
    )
    aceite_termos = models.BooleanField(
        default=False,
        verbose_name="Aceitou Termos de Uso"
    )
    aceite_privacidade = models.BooleanField(
        default=False,
        verbose_name="Aceitou Política de Privacidade"
    )
    data_consentimento = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data/Hora do Consentimento"
    )
    ip_consentimento = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP do Consentimento",
        help_text="Endereço IP de onde o consentimento foi dado"
    )
    versao_termos = models.CharField(
        max_length=20,
        default='1.0',
        verbose_name="Versão dos Termos",
        help_text="Versão dos termos aceitos (ex: 1.0, 1.1)"
    )
    versao_privacidade = models.CharField(
        max_length=20,
        default='1.0',
        verbose_name="Versão da Política",
        help_text="Versão da política de privacidade aceita"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent",
        help_text="Informações do navegador/dispositivo"
    )

    def __str__(self):
        return f"Consentimento de {self.usuario.username} em {self.data_consentimento.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Consentimento LGPD"
        verbose_name_plural = "Consentimentos LGPD"
        ordering = ['-data_consentimento']
