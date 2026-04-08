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
    """
    Modelo para solicitações de permissões (grupos) dos usuários.
    Permite que usuários solicitem acesso a determinados grupos/permissões
    e administradores aprovem ou rejeitem essas solicitações.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovada'),
        ('rejected', 'Rejeitada'),
        ('cancelled', 'Cancelada'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    usuario_solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitacoes_permissao',
        verbose_name='Usuário Solicitante',
        help_text='Usuário que está solicitando a permissão'
    )
    
    grupo_solicitado = models.ForeignKey(
        'auth.Group',
        on_delete=models.CASCADE,
        verbose_name='Grupo/Permissão Solicitada',
        help_text='Grupo de permissão que está sendo solicitado'
    )
    
    justificativa = models.TextField(
        verbose_name='Justificativa',
        help_text='Explique por que você precisa desta permissão'
    )
    
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADE_CHOICES,
        default='media',
        verbose_name='Prioridade',
        help_text='Nível de urgência da solicitação'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status',
        db_index=True
    )
    
    data_solicitacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data da Solicitação',
        db_index=True
    )
    
    data_resposta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data da Resposta',
        help_text='Data em que a solicitação foi aprovada ou rejeitada'
    )
    
    usuario_aprovador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitacoes_avaliadas',
        verbose_name='Aprovador/Rejeitador',
        help_text='Usuário que aprovou ou rejeitou a solicitação'
    )
    
    observacao_resposta = models.TextField(
        blank=True,
        verbose_name='Observação da Resposta',
        help_text='Comentários do aprovador sobre a decisão'
    )
    
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Ministério',
        help_text='Ministério ao qual a solicitação pertence'
    )
    
    igreja_contexto = models.ForeignKey(
        'configuracao.Igreja',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Igreja de Contexto',
        help_text='Igreja relacionada à solicitação (se aplicável)'
    )
    
    notificacao_enviada = models.BooleanField(
        default=False,
        verbose_name='Notificação Enviada',
        help_text='Indica se o solicitante foi notificado da resposta'
    )
    
    class Meta:
        verbose_name = 'Solicitação de Permissão'
        verbose_name_plural = 'Solicitações de Permissões'
        ordering = ['-data_solicitacao']
        indexes = [
            models.Index(fields=['status', '-data_solicitacao']),
            models.Index(fields=['usuario_solicitante', '-data_solicitacao']),
            models.Index(fields=['ministerio', 'status']),
        ]
    
    def __str__(self):
        return f"{self.usuario_solicitante.username} → {self.grupo_solicitado.name} ({self.get_status_display()})"
    
    @property
    def pendente(self):
        """Verifica se a solicitação está pendente"""
        return self.status == 'pending'
    
    @property
    def tempo_espera(self):
        """Retorna o tempo de espera desde a solicitação"""
        if self.data_resposta:
            return self.data_resposta - self.data_solicitacao
        return timezone.now() - self.data_solicitacao
    
    def aprovar(self, aprovador, observacao=''):
        """Aprova a solicitação e adiciona o usuário ao grupo"""
        self.status = 'approved'
        self.usuario_aprovador = aprovador
        self.data_resposta = timezone.now()
        self.observacao_resposta = observacao
        self.save()
        
        # Adiciona o usuário ao grupo
        self.usuario_solicitante.groups.add(self.grupo_solicitado)
        
        # Registra no log de auditoria
        from auditoria.models import PermissionChangeLog
        PermissionChangeLog.objects.create(
            usuario_afetado=self.usuario_solicitante,
            grupo=self.grupo_solicitado,
            acao='ADD',
            usuario_executor=aprovador,
            observacao=f'Aprovado via solicitação #{self.id}: {observacao}',
            ministerio=self.ministerio
        )
        
        return True
    
    def rejeitar(self, rejeitador, observacao=''):
        """Rejeita a solicitação"""
        self.status = 'rejected'
        self.usuario_aprovador = rejeitador
        self.data_resposta = timezone.now()
        self.observacao_resposta = observacao
        self.save()
        
        return True
    
    def cancelar(self):
        """Cancela a solicitação (pelo próprio solicitante)"""
        if self.status == 'pending':
            self.status = 'cancelled'
            self.save()
            return True
        return False


# ===================================
# MODELO DE HIERARQUIA DE PERMISSÕES
# ===================================

class HierarquiaPermissoes(models.Model):
    """
    Rastreia a relação de subordinação entre usuários para controle hierárquico de permissões.
    Permite que Admin, Pastor Regional e Pastor Local gerenciem permissões de seus subordinados.
    
    Exemplo:
    - Admin Ministério: usuario_superior = Admin, usuario_subordinado = Pastor Regional
    - Pastor Regional: usuario_superior = Pastor Regional, usuario_subordinado = Pastor Local
    - Pastor Local: usuario_superior = Pastor Local, usuario_subordinado = Secretário/Tesoureiro
    """
    
    NIVEL_CHOICES = [
        ('Admin Ministerio', 'Admin Ministério'),
        ('Pastor Regional', 'Pastor Regional'),
        ('Pastor Local', 'Pastor Local'),
    ]
    
    usuario_superior = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vinculos_supervisao',
        verbose_name='Usuário Superior (Gerenciador)',
        help_text='Usuário que gerencia permissões'
    )
    
    usuario_subordinado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vinculos_subordinacao',
        verbose_name='Usuário Subordinado',
        help_text='Usuário cuja permissão será gerenciada'
    )
    
    nivel_superior = models.CharField(
        max_length=50,
        choices=NIVEL_CHOICES,
        verbose_name='Nível do Superior',
        help_text='Nível hierárquico que autoriza o gerenciamento'
    )
    
    igreja = models.ForeignKey(
        'configuracao.Igreja',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hierarquias_permissoes',
        verbose_name='Igreja (Contexto)',
        help_text='Igreja para a qual a subordinação é válida (especialmente para Pastores Locais)'
    )
    
    data_vinculo = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data do Vínculo'
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Desativar sem deletar o registro'
    )
    
    class Meta:
        verbose_name = 'Hierarquia de Permissões'
        verbose_name_plural = 'Hierarquias de Permissões'
        ordering = ['-data_vinculo']
        unique_together = ('usuario_superior', 'usuario_subordinado', 'nivel_superior')
        indexes = [
            models.Index(fields=['usuario_superior', 'nivel_superior']),
            models.Index(fields=['usuario_subordinado', 'ativo']),
            models.Index(fields=['igreja', 'nivel_superior']),
        ]
    
    def __str__(self):
        return f"{self.usuario_superior.username} ({self.nivel_superior}) → {self.usuario_subordinado.username}"
