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


class PermissionRequest(models.Model):
    """Solicitacao de permissao (grupo) por usuario."""

    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovada'),
        ('rejected', 'Rejeitada'),
        ('cancelled', 'Cancelada'),
    ]

    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    usuario_solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitacoes_permissao',
        verbose_name='Usuario Solicitante',
    )
    grupo_solicitado = models.ForeignKey(
        'auth.Group',
        on_delete=models.CASCADE,
        verbose_name='Grupo Solicitado',
    )
    justificativa = models.TextField(verbose_name='Justificativa')
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='media')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', db_index=True)
    data_solicitacao = models.DateTimeField(auto_now_add=True, db_index=True)
    data_resposta = models.DateTimeField(null=True, blank=True)
    usuario_aprovador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitacoes_avaliadas',
    )
    observacao_resposta = models.TextField(blank=True)
    ministerio = models.ForeignKey(Ministerio, on_delete=models.CASCADE, null=True, blank=True)
    igreja_contexto = models.ForeignKey('configuracao.Igreja', on_delete=models.SET_NULL, null=True, blank=True)
    notificacao_enviada = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Solicitacao de Permissao'
        verbose_name_plural = 'Solicitacoes de Permissoes'
        ordering = ['-data_solicitacao']
        indexes = [
            models.Index(fields=['status', '-data_solicitacao']),
            models.Index(fields=['usuario_solicitante', '-data_solicitacao']),
            models.Index(fields=['ministerio', 'status']),
        ]

    def __str__(self):
        return f"{self.usuario_solicitante.username} -> {self.grupo_solicitado.name} ({self.get_status_display()})"

    @property
    def pendente(self):
        return self.status == 'pending'

    @property
    def tempo_espera(self):
        if self.data_resposta:
            return self.data_resposta - self.data_solicitacao
        return timezone.now() - self.data_solicitacao

    def aprovar(self, aprovador, observacao=''):
        self.status = 'approved'
        self.usuario_aprovador = aprovador
        self.data_resposta = timezone.now()
        self.observacao_resposta = observacao
        self.save(update_fields=['status', 'usuario_aprovador', 'data_resposta', 'observacao_resposta'])

        self.usuario_solicitante.groups.add(self.grupo_solicitado)

        from auditoria.models import PermissionChangeLog
        PermissionChangeLog.objects.create(
            usuario_afetado=self.usuario_solicitante,
            grupo=self.grupo_solicitado,
            acao='ADD',
            usuario_executor=aprovador,
            observacao=f'Aprovado via solicitacao #{self.id}: {observacao}',
            ministerio=self.ministerio,
        )
        return True

    def rejeitar(self, rejeitador, observacao=''):
        self.status = 'rejected'
        self.usuario_aprovador = rejeitador
        self.data_resposta = timezone.now()
        self.observacao_resposta = observacao
        self.save(update_fields=['status', 'usuario_aprovador', 'data_resposta', 'observacao_resposta'])
        return True

    def cancelar(self):
        if self.status != 'pending':
            return False
        self.status = 'cancelled'
        self.save(update_fields=['status'])
        return True


class HierarquiaPermissoes(models.Model):
    """Relacionamento hierarquico entre usuario superior e subordinado."""

    NIVEL_CHOICES = [
        ('Admin Ministerio', 'Admin Ministerio'),
        ('Pastor Regional', 'Pastor Regional'),
        ('Pastor Local', 'Pastor Local'),
    ]

    usuario_superior = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vinculos_supervisao',
    )
    usuario_subordinado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vinculos_subordinacao',
    )
    nivel_superior = models.CharField(max_length=50, choices=NIVEL_CHOICES)
    igreja = models.ForeignKey(
        'configuracao.Igreja',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hierarquias_permissoes',
    )
    data_vinculo = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Hierarquia de Permissao'
        verbose_name_plural = 'Hierarquias de Permissoes'
        ordering = ['-data_vinculo']
        unique_together = ('usuario_superior', 'usuario_subordinado', 'nivel_superior')
        indexes = [
            models.Index(fields=['usuario_superior', 'nivel_superior']),
            models.Index(fields=['usuario_subordinado', 'ativo']),
            models.Index(fields=['igreja', 'nivel_superior']),
        ]

    def __str__(self):
        return f"{self.usuario_superior.username} ({self.nivel_superior}) -> {self.usuario_subordinado.username}"
