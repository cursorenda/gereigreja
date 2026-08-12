from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
# Importa o modelo de onboarding para registro no app
from .models_onboarding import OnboardingStatus
# --- Configurações Globais do Sistema (Notificações, etc) ---
class ConfiguracaoSistema(models.Model):
    DIAS_SEMANA = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    ebd_dia_semana = models.IntegerField(
        choices=DIAS_SEMANA,
        default=6,
        verbose_name='Dia padrão da EBD',
        help_text='Selecione o dia padrão da semana em que ocorre a Escola Bíblica Dominical.'
    )
    ministerio = models.OneToOneField('Ministerio', on_delete=models.CASCADE, related_name='configuracao', verbose_name='Ministério')
    notificar_eventos = models.BooleanField(default=True, verbose_name='Enviar notificações de eventos?')
    notificar_aniversarios = models.BooleanField(default=True, verbose_name='Enviar notificações de aniversários?')
    # Notificações de pré-cadastro
    notificar_pre_cadastro_secretario_pastor = models.BooleanField(
        default=True,
        verbose_name='Notificar Secretário/Pastor Local sobre auto-cadastro?',
        help_text='Se marcado, Secretários e Pastores Locais receberão notificação de novos auto-cadastros.'
    )
    notificar_pre_cadastro_admin = models.BooleanField(
        default=False,
        verbose_name='Notificar Admin Ministério sobre auto-cadastro?',
        help_text='Se marcado, o Admin Ministério também receberá notificação de novos auto-cadastros.'
    )
    EBD_PERIODO_CHOICES = [
        ('trimestre', 'Trimestre'),
        ('quadrimestre', 'Quadrimestre'),
        ('semestre', 'Semestre'),
        ('ano', 'Ano'),
    ]
    ebd_periodo = models.CharField(
        max_length=20,
        choices=EBD_PERIODO_CHOICES,
        default='trimestre',
        verbose_name='Período da Escola Bíblica',
        help_text='Selecione o período utilizado para a EBD (trimestre, quadrimestre, semestre, ano).'
    )
    ebd_horario = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Horário padrão da EBD',
        help_text='Horário padrão sugerido para as lições da Escola Bíblica Dominical.'
    )
    # Recursos devocionais no portal do membro
    url_biblia_online = models.URLField(
        blank=True,
        default='https://www.bibliaonline.com.br/',
        verbose_name='URL — Bíblia Online',
        help_text='Link externo para a Bíblia Online exibida no portal do membro.'
    )
    url_harpa_crista = models.URLField(
        blank=True,
        default='https://www.harpacrista.com.br/',
        verbose_name='URL — Harpa Cristã',
        help_text='Link externo para a Harpa Cristã exibida no portal do membro.'
    )
    # Adicione outros tipos de notificação conforme necessário
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração do Sistema'
        verbose_name_plural = 'Configurações do Sistema'

    def __str__(self):
        return f'Configuração de {self.ministerio.nome_fantasia}'

# c:\Gereigreja\configuracao\models.py
from django.db import models
from django.conf import settings # Necessário para referenciar o User model padrão do Django
from django.utils import timezone # Importar timezone se usar default=timezone.now
import uuid # Para nomes de arquivo únicos
import os   # Para manipulação de caminhos
import unicodedata
from datetime import timedelta # Para calcular data_fim da assinatura
from django.apps import apps # Para import tardio e evitar circularidade


def _default_avatar_url() -> str:
    """URL absoluta (relativa ao host) do avatar padrão estático do sistema."""
    return f"{settings.STATIC_URL}img/default_avatar.png"


def _default_ministerio_url() -> str:
    """URL da imagem padrão de Ministério."""
    return f"{settings.STATIC_URL}img/default_ministerio.png"


def _default_igreja_url() -> str:
    """URL da imagem padrão de Igreja."""
    return f"{settings.STATIC_URL}img/default_igreja.png"


def _get_galeria_imagem_ativa_url(tipo: str, fallback_url: str) -> str:
    """Busca a imagem ativa da galeria por tipo e cai para static se não existir."""
    try:
        SistemaImagem = apps.get_model('painel_desenvolvedor', 'SistemaImagem')
        imagem = SistemaImagem.objects.filter(
            tipo=tipo,
            variacao='original',
            ativo=True,
        ).order_by('-data_upload').first()
        if imagem and imagem.imagem:
            return imagem.imagem.url
    except Exception:
        pass
    return fallback_url

# Histórico de mensalidades e cortesias
class HistoricoAssinatura(models.Model):
    TIPOS = [
        ('mensalidade', 'Mensalidade'),
        ('cortesia', 'Cortesia'),
        ('trial', 'Teste Grátis'),
    ]
    STATUS = [
        ('paga', 'Paga'),
        ('expirada', 'Expirada'),
        ('a_vencer', 'A Vencer'),
        ('vencida', 'Vencida'),
    ]
    ministerio = models.ForeignKey('Ministerio', on_delete=models.CASCADE, related_name='historicos_assinatura')
    plano = models.ForeignKey('Plano', on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField(null=True, blank=True)
    data_registro = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-data_inicio']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.get_status_display()} ({self.data_inicio:%d/%m/%Y})"


# --- Função para upload_to do logo do Ministério ---
def get_ministerio_logo_upload_path(instance, filename):
    """Gera um caminho de upload único para os logos dos Ministérios."""
    ext = os.path.splitext(filename)[1]
    unique_filename = f"ministerio_logo_{uuid.uuid4().hex}{ext}"
    return os.path.join('logos_ministerios', unique_filename)

# --- DEFINIÇÃO DE ESTADO_CHOICES ---
ESTADO_CHOICES = [
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
    ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
    ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), # noqa
    ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
]
# --- FIM ESTADO_CHOICES ---


class ModeloCartaRecomendacao(models.Model):
    TIPO_PADRAO = 'padrao'
    TIPO_EXCLUSIVO = 'exclusivo'
    TIPO_CHOICES = [
        (TIPO_PADRAO, 'Padrao'),
        (TIPO_EXCLUSIVO, 'Exclusivo'),
    ]

    codigo = models.CharField(
        max_length=60,
        unique=True,
        verbose_name='Codigo tecnico',
        help_text='Identificador unico do modelo (ex: padrao, vales_classico).'
    )
    nome = models.CharField(max_length=120, verbose_name='Nome do modelo')
    template_include = models.CharField(
        max_length=255,
        verbose_name='Template include',
        help_text='Caminho do include Django (ex: secretaria/documentos/modelos/_carta_recomendacao_padrao.html).'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_PADRAO)
    ministerio = models.ForeignKey(
        'Ministerio',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='modelos_carta_exclusivos',
        verbose_name='Ministerio dono (quando exclusivo)'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    ordem = models.PositiveIntegerField(default=100, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Modelo de Carta de Recomendacao'
        verbose_name_plural = 'Modelos de Carta de Recomendacao'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.codigo})"

    def clean(self):
        super().clean()

        if self.tipo == self.TIPO_EXCLUSIVO and not self.ministerio_id:
            raise ValidationError({
                'ministerio': 'Modelos exclusivos devem estar vinculados a um ministerio.'
            })

        if self.tipo == self.TIPO_PADRAO and self.ministerio_id:
            raise ValidationError({
                'ministerio': 'Modelos padrao nao podem estar vinculados a um ministerio especifico.'
            })


# --- Modelo para o Ministério ---
class Ministerio(models.Model):
    def verificar_elegibilidade_plano_gratuito(self):
        """
        Retorna True se o ministério está dentro dos limites do plano gratuito (busca o limite do plano pioneiro cadastrado).
        Usa apenas membros com status 'Ativo' — mesma métrica do enforcement do plano.
        """
        from secretaria.models import Membro
        total_membros = Membro.objects.filter(
            igreja__ministerio=self,
            status_pessoa__nome__iexact='Ativo',
        ).count()
        try:
            plano_pioneiro = Plano.objects.get(codigo_plano='pioneiro')
            limite = plano_pioneiro.limite_membros
        except Plano.DoesNotExist:
            limite = 50 # fallback seguro
        return limite == 0 or total_membros <= limite
    nome_fantasia = models.CharField(
        max_length=150,
        verbose_name="Nome Fantasia"
    )
    razao_social = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Razão Social"
    )
    administrador_principal = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ministerios_administrados',
        verbose_name="Administrador Principal"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    ativo = models.BooleanField(
        default=False,
        verbose_name="Ativo (Aprovado pelo Desenvolvedor)",
        help_text="Ministérios inativos podem ter acesso limitado até serem aprovados."
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    cnpj = models.CharField(max_length=18, unique=True, null=True, blank=True, verbose_name="CNPJ")
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    rua = models.CharField(max_length=150, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(
        max_length=2,
        choices=ESTADO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Estado (Sede)"
    )
    logo = models.ImageField(
        upload_to=get_ministerio_logo_upload_path, # Função para gerar o caminho
        null=True,
        blank=True,
        verbose_name="Logo do Ministério"
    )
    logo_png = models.ImageField(
        upload_to=get_ministerio_logo_upload_path,
        null=True,
        blank=True,
        verbose_name='Logo PNG (principal)',
        help_text='Use este arquivo PNG para materiais de marketing e documentos visuais.'
    )
    logo_pequeno = models.ImageField(
        upload_to=get_ministerio_logo_upload_path,
        null=True,
        blank=True,
        verbose_name='Logo pequeno',
        help_text='Versão reduzida para cartões, avatares e selos.'
    )
    logo_grande = models.ImageField(
        upload_to=get_ministerio_logo_upload_path,
        null=True,
        blank=True,
        verbose_name='Logo grande',
        help_text='Versão em alta para banners, capas e peças grandes.'
    )
    logo_marketing_extra_1 = models.ImageField(
        upload_to=get_ministerio_logo_upload_path,
        null=True,
        blank=True,
        verbose_name='Logo extra 1',
        help_text='Versão opcional para campanhas específicas.'
    )
    logo_marketing_extra_2 = models.ImageField(
        upload_to=get_ministerio_logo_upload_path,
        null=True,
        blank=True,
        verbose_name='Logo extra 2',
        help_text='Versão opcional adicional para marketing.'
    )
    modelo_carta_recomendacao = models.CharField(
        max_length=40,
        default='padrao',
        blank=True,
        verbose_name='Modelo da Carta de Recomendacao',
        help_text='Codigo do modelo selecionado para carta de recomendacao.'
    )
    carteirinha_permitir_secretaria_local = models.BooleanField(
        default=False,
        verbose_name='Permitir emissao da carteirinha pelas igrejas locais',
        help_text='Se desmarcado, somente a secretaria ministerial/presidencia pode gerar e imprimir carteirinhas.'
    )

    # --- CAMPO PARA INTEGRAÇÃO COM GATEWAY DE PAGAMENTO ---
    stripe_customer_id = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="ID do Cliente no Stripe",
        help_text="ID do cliente no Stripe, usado para gerenciar assinaturas."
    )

    def __str__(self):
        return self.nome_fantasia

    @property
    def logo_url(self) -> str:
        """Retorna a URL da logo do ministério com fallback padrão."""
        try:
            if self.logo:
                return self.logo.url
        except Exception:
            pass
        return _get_galeria_imagem_ativa_url(
            'padrao_ministerio',
            _default_ministerio_url(),
        )


    class Meta:
        verbose_name = "Ministério"
        verbose_name_plural = "Ministérios"
        ordering = ['nome_fantasia']

# --- Modelo para o Perfil do Usuário ---
class PerfilUsuario(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        related_name='perfis_usuarios'
    )
    igrejas_permitidas = models.ManyToManyField(
        'Igreja',
        blank=True,
        related_name='usuarios_permitidos',
        verbose_name="Igrejas Permitidas",
        help_text="Selecione as igrejas específicas que este usuário pode gerenciar (deixe em branco para acesso baseado apenas no papel/ministerio)."
    )
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True, verbose_name="Foto do Perfil")
    telefone_contato = models.CharField(
        max_length=20,
        blank=True, null=True,
        verbose_name="Telefone de Contato"
    )
    whatsapp_contato = models.CharField(
        max_length=20,
        blank=True, null=True,
        verbose_name="WhatsApp"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    def __str__(self):
        user_display = self.user.get_full_name() or self.user.username
        return f"Perfil de {user_display} ({self.ministerio.nome_fantasia})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

# --- Funções para upload_to dos logos da Igreja ---

def logo1_upload_to_path(instance, filename):
    """ Gera um caminho de upload único para o logo 1 da igreja. """
    ext = os.path.splitext(filename)[1]
    # Cria um nome de arquivo único que não depende do PK do objeto.
    # Opcional: pode-se incluir instance.pk se ele existir para organizar em pastas.
    # Ex: f'igreja_{instance.pk or "novo"}/logo1_{uuid.uuid4().hex}{ext}'
    unique_filename = f"igreja_logo1_{uuid.uuid4().hex}{ext}"
    return os.path.join('logos_igrejas', unique_filename)

def logo2_upload_to_path(instance, filename):
    """ Gera um caminho de upload único para o logo 2 da igreja. """
    ext = os.path.splitext(filename)[1]
    unique_filename = f"igreja_logo2_{uuid.uuid4().hex}{ext}"
    return os.path.join('logos_igrejas', unique_filename)


# --- Modelo para cada Igreja (Sede, Regional, Congregação) ---
class Igreja(models.Model):
    # --- Relacionamentos ---
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        related_name='igrejas'
    )
    igreja_superior = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='igrejas_subordinadas',
        verbose_name="Igreja Superior (Sede/Regional)",
        help_text="Selecione a Sede ou Regional à qual esta igreja está vinculada (se aplicável)."
    )

    # --- Identificação e Tipo ---
    nome_igreja = models.CharField(max_length=255, verbose_name="Nome da Igreja")
    TIPO_IGREJA_CHOICES = [
        ('sede', 'Sede'),
        ('regional', 'Regional'),
        ('congregacao', 'Congregação'),
        ('independente', 'Independente'), # Adicionado para clareza
    ]
    tipo_igreja = models.CharField(
        max_length=20,
        choices=TIPO_IGREJA_CHOICES,
        default='congregacao',
        verbose_name="Tipo de Igreja"
    )
    data_fundacao = models.DateField(blank=True, null=True, verbose_name="Data de Fundação")

    # --- Endereço ---
    cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP")
    rua = models.CharField(max_length=255, blank=True, null=True, verbose_name="Rua")
    numero_casa = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    bairro_distrito = models.CharField(max_length=255, blank=True, null=True, verbose_name="Bairro/Distrito")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(
        max_length=2,
        choices=ESTADO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Estado"
    )
    pais = models.CharField(max_length=50, blank=True, null=True, default="Brasil", verbose_name="País")

    # --- Contato e Documentos ---
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="E-mail")
    cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name="CNPJ")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name="Celular")
    site = models.URLField(blank=True, null=True, verbose_name="Site")

    # --- Responsáveis ---
    pastor_local = models.CharField(max_length=255, blank=True, null=True, verbose_name="Pastor Local / Responsável")
    pastor_regional = models.CharField(max_length=255, blank=True, null=True, verbose_name="Pastor Regional")

    # --- Outras Configurações ---
    moeda = models.CharField(max_length=3, default="BRL", verbose_name="Moeda")
    ebd_periodo = models.CharField(
        max_length=20,
        choices=ConfiguracaoSistema.EBD_PERIODO_CHOICES,
        blank=True,
        null=True,
        verbose_name='Período da EBD (Igreja)',
        help_text='Opcional. Se preenchido, substitui o período EBD herdado do ministério para esta igreja.'
    )
    ebd_dia_semana = models.IntegerField(
        choices=ConfiguracaoSistema.DIAS_SEMANA,
        blank=True,
        null=True,
        verbose_name='Dia da EBD (Igreja)',
        help_text='Opcional. Se preenchido, substitui o dia EBD herdado do ministério para esta igreja.'
    )
    ebd_horario = models.TimeField(
        blank=True,
        null=True,
        verbose_name='Horário da EBD (Igreja)',
        help_text='Opcional. Se preenchido, substitui o horário EBD herdado do ministério para esta igreja.'
    )
    ebd_pontos_presente = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Pontos por Presença',
        help_text='Opcional. Pontos atribuídos quando o aluno está presente na chamada.'
    )
    ebd_pontos_biblia = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Pontos por Bíblia',
        help_text='Opcional. Pontos atribuídos quando o aluno marca Bíblia na chamada.'
    )
    ebd_pontos_revista = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Pontos por Revista',
        help_text='Opcional. Pontos atribuídos quando o aluno marca Revista na chamada.'
    )
    ebd_pontos_oferta = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Pontos por Oferta',
        help_text='Opcional. Pontos atribuídos quando o aluno marca Oferta na chamada.'
    )
    ebd_pontos_visitante = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Pontos por Visitante',
        help_text='Opcional. Pontos atribuídos quando o aluno marca Visitante na chamada.'
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    logo1 = models.ImageField(upload_to=logo1_upload_to_path, blank=True, null=True, verbose_name="Logo 1")
    logo2 = models.ImageField(upload_to=logo2_upload_to_path, blank=True, null=True, verbose_name="Logo 2")
    
    conta_padrao_receitas = models.ForeignKey(
        'financeiro.ContaBancaria',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='igreja_como_padrao_receita',
        verbose_name="Conta/Caixa Padrão para Receitas",
        help_text="Conta/Caixa que será pré-selecionada ao registrar novas receitas para esta igreja."
    )
    conta_padrao_despesas = models.ForeignKey(
        'financeiro.ContaBancaria',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='igreja_como_padrao_despesa',
        verbose_name="Conta/Caixa Padrão para Despesas",
        help_text="Conta/Caixa que será pré-selecionada ao registrar novas despesas para esta igreja."
    )
    conta_padrao_eventos = models.ForeignKey(
        'financeiro.ContaBancaria',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='igreja_como_padrao_evento',
        verbose_name="Conta/Caixa Padrão para Eventos",
        help_text="Conta/Caixa usada automaticamente nas entradas e saídas de eventos desta igreja."
    )
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
 
    def __str__(self):
        min_nome = self.ministerio.nome_fantasia if self.ministerio else "Sem Ministério"
        return f"{self.nome_igreja} ({self.get_tipo_igreja_display()}) - [{min_nome}]"

    @property
    def logo1_url(self) -> str:
        """Retorna a URL do logo1 da igreja com fallback padrão."""
        try:
            if self.logo1:
                return self.logo1.url
        except Exception:
            pass
        return _get_galeria_imagem_ativa_url(
            'padrao_igreja',
            _default_igreja_url(),
        )

    @property
    def logo2_url(self) -> str:
        """Retorna a URL do logo2 da igreja com fallback padrão."""
        try:
            if self.logo2:
                return self.logo2.url
        except Exception:
            pass
        return _get_galeria_imagem_ativa_url(
            'padrao_igreja',
            _default_igreja_url(),
        )

    def get_descendants(self, include_self=False):
        """
        Retorna um QuerySet de todas as igrejas descendentes (subordinadas diretas e indiretas).
        """
        ids = set()
        if include_self:
            ids.add(self.pk)

        children = self.igrejas_subordinadas.all()
        
        for child in children:
            ids.add(child.pk)
            # Adiciona descendentes recursivamente
            child_descendants = child.get_descendants(include_self=False)
            ids.update(child_descendants.values_list('pk', flat=True))
        
        return Igreja.objects.filter(pk__in=ids).distinct()

    class Meta:
        verbose_name = "Igreja"
        verbose_name_plural = "Igrejas"
        ordering = ['ministerio', 'nome_igreja']
        unique_together = ('ministerio', 'nome_igreja')


class Departamento(models.Model):
    """Entidade organizacional de departamento por igreja, independente do modulo financeiro."""

    TIPO_PADRAO = 'PADRAO'
    TIPO_PERSONALIZADO = 'PERSONALIZADO'

    TIPO_CHOICES = [
        (TIPO_PADRAO, 'Padrao do Sistema'),
        (TIPO_PERSONALIZADO, 'Personalizado'),
    ]

    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.CASCADE,
        related_name='departamentos',
        verbose_name='Igreja',
    )
    codigo_interno = models.CharField(max_length=40, verbose_name='Codigo Interno')
    nome_exibicao = models.CharField(max_length=120, verbose_name='Nome de Exibicao')
    tipo_departamento = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default=TIPO_PERSONALIZADO,
        verbose_name='Tipo de Departamento',
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    ordem_exibicao = models.PositiveIntegerField(default=100, verbose_name='Ordem de Exibicao')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['igreja__ministerio__nome_fantasia', 'igreja__nome_igreja', 'ordem_exibicao', 'nome_exibicao']
        unique_together = ('igreja', 'codigo_interno')

    def __str__(self):
        return f"{self.nome_exibicao} ({self.igreja.nome_igreja})"

    def save(self, *args, **kwargs):
        self.codigo_interno = (self.codigo_interno or '').strip().upper().replace(' ', '_')
        super().save(*args, **kwargs)


class ProgramacaoPadraoIgreja(models.Model):
    """Programacoes recorrentes da igreja para gerar agenda automaticamente."""

    TIPO_EVENTO_CHOICES = [
        ('culto', 'Culto'),
        ('estudo', 'Estudo'),
        ('reuniao', 'Reunião'),
        ('escola_dominical', 'Escola Dominical'),
        ('outro', 'Outro'),
    ]

    FREQUENCIA_CHOICES = [
        ('semanal', 'Semanal'),
        ('mensal_por_ocorrencia', 'Mensal por ocorrência'),
        ('anual_por_ocorrencia', 'Anual por ocorrência'),
    ]

    OCORRENCIA_MENSAL_CHOICES = [
        (1, '1ª ocorrência do mês'),
        (2, '2ª ocorrência do mês'),
        (3, '3ª ocorrência do mês'),
        (4, '4ª ocorrência do mês'),
        (-1, 'Última ocorrência do mês'),
    ]

    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.CASCADE,
        related_name='programacoes_padrao',
        verbose_name='Igreja',
    )
    nome = models.CharField(max_length=120, verbose_name='Nome da programação')
    tipo_evento = models.CharField(
        max_length=20,
        choices=TIPO_EVENTO_CHOICES,
        default='culto',
        verbose_name='Tipo de evento',
    )
    frequencia = models.CharField(
        max_length=30,
        choices=FREQUENCIA_CHOICES,
        default='semanal',
        verbose_name='Frequência',
    )
    dia_semana = models.IntegerField(
        choices=ConfiguracaoSistema.DIAS_SEMANA,
        verbose_name='Dia da semana',
    )
    ocorrencia_mensal = models.IntegerField(
        choices=OCORRENCIA_MENSAL_CHOICES,
        blank=True,
        null=True,
        verbose_name='Ocorrência mensal',
        help_text='Usado quando frequência é mensal por ocorrência (ex: 1º domingo, 2º domingo, último domingo).',
    )
    intervalo_semanas = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        verbose_name='Intervalo em semanas',
        help_text='Use 1 para semanal, 2 para quinzenal, etc. Válido para frequência semanal.',
    )
    mes_ano = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name='Mês do ano',
        help_text='Usado em recorrência anual por ocorrência (1=Jan ... 12=Dez).',
    )
    hora_inicio = models.TimeField(verbose_name='Hora de início')
    hora_termino = models.TimeField(
        blank=True,
        null=True,
        verbose_name='Hora de término',
        help_text='Preferencial para configurar o fim do culto/reunião. A duração será calculada automaticamente.',
    )
    duracao_minutos = models.PositiveIntegerField(
        default=90,
        validators=[MinValueValidator(30), MaxValueValidator(360)],
        verbose_name='Duração (minutos)',
    )
    local = models.CharField(max_length=200, blank=True, null=True, verbose_name='Local')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    datas_excecao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Datas de exceção',
        help_text='Uma data por linha (YYYY-MM-DD ou DD/MM/YYYY) para pular ocorrências específicas.',
    )
    ordem = models.PositiveSmallIntegerField(default=0, verbose_name='Ordem')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Programação Padrão da Igreja'
        verbose_name_plural = 'Programações Padrão das Igrejas'
        ordering = ['ordem', 'dia_semana', 'hora_inicio', 'nome']
        unique_together = ('igreja', 'nome', 'dia_semana', 'hora_inicio')

    def __str__(self):
        return f"{self.nome} ({self.get_dia_semana_display()} {self.hora_inicio:%H:%M})"

    def clean(self):
        super().clean()
        if self.frequencia in ('mensal_por_ocorrencia', 'anual_por_ocorrencia') and self.ocorrencia_mensal is None:
            raise ValidationError({'ocorrencia_mensal': 'Informe a ocorrência mensal para frequência mensal.'})

        if self.frequencia == 'anual_por_ocorrencia' and self.mes_ano is None:
            raise ValidationError({'mes_ano': 'Informe o mês do ano para frequência anual por ocorrência.'})

        if self.frequencia == 'semanal':
            self.ocorrencia_mensal = None
            self.mes_ano = None

        if self.frequencia == 'mensal_por_ocorrencia':
            self.mes_ano = None

        if self.hora_termino:
            dt_inicio = datetime.combine(datetime.today().date(), self.hora_inicio)
            dt_fim = datetime.combine(datetime.today().date(), self.hora_termino)
            if dt_fim <= dt_inicio:
                raise ValidationError({'hora_termino': 'A hora de término deve ser maior que a hora de início.'})
            self.duracao_minutos = int((dt_fim - dt_inicio).total_seconds() // 60)
        elif not self.duracao_minutos:
            self.duracao_minutos = 90

        if self.datas_excecao:
            for linha in self.datas_excecao.splitlines():
                valor = (linha or '').strip()
                if not valor:
                    continue
                data = parse_date(valor)
                if data is None and '/' in valor:
                    partes = valor.split('/')
                    if len(partes) == 3:
                        data = parse_date(f"{partes[2]}-{partes[1]}-{partes[0]}")
                if data is None:
                    raise ValidationError({'datas_excecao': f'Data inválida nas exceções: {valor}'})

    def get_datas_excecao_set(self):
        """Retorna conjunto de datas de exceção normalizadas."""
        resultado = set()
        if not self.datas_excecao:
            return resultado

        for linha in self.datas_excecao.splitlines():
            valor = (linha or '').strip()
            if not valor:
                continue
            data = parse_date(valor)
            if data is None and '/' in valor:
                partes = valor.split('/')
                if len(partes) == 3:
                    data = parse_date(f"{partes[2]}-{partes[1]}-{partes[0]}")
            if data is not None:
                resultado.add(data)
        return resultado

    @property
    def hora_termino_calculada(self):
        if self.hora_termino:
            return self.hora_termino
        dt_inicio = datetime.combine(datetime.today().date(), self.hora_inicio)
        dt_fim = dt_inicio + timedelta(minutes=self.duracao_minutos or 90)
        return dt_fim.time()

# --- NOVOS MODELOS PARA PLANOS E ASSINATURAS ---

class Plano(models.Model):
    MODULOS_CONFIGURAVEIS = [
        ('permite_modulo_secretaria', 'Módulo Secretaria', 'Secretaria completa'),
        ('permite_modulo_agenda', 'Módulo Agenda', 'Agenda inteligente'),
        ('permite_modulo_eventos', 'Módulo Eventos', 'Gestão de eventos'),
        ('permite_modulo_escola_biblica', 'Módulo Escola Bíblica', 'Escola bíblica'),
        ('permite_modulo_financeiro', 'Módulo Financeiro', 'Módulo financeiro'),
        ('permite_modulo_comunicacao', 'Módulo de Comunicação', 'Comunicação em massa'),
    ]
    SUPORTES_CONFIGURAVEIS = [
        ('permite_suporte_tickets', 'Suporte via tickets', 'Suporte via tickets'),
        ('suporte_prioritario', 'Suporte Prioritário', 'Suporte prioritário'),
    ]

    NOME_PLANO_CHOICES = [
        ('pioneiro', 'Pioneiro'),
        ('crescimento', 'Crescimento'),
        ('ministerio', 'Ministério'),
        ('rede', 'Rede'),
    ]
    nome = models.CharField(max_length=50, choices=NOME_PLANO_CHOICES, unique=True, verbose_name="Nome do Plano")
    codigo_plano = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Identificador único para o sistema (ex: 'pioneiro', 'crescimento', 'ministerio').")    
    # Preços
    preco_mensal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Mensal (R$)")
    preco_anual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Anual (R$)")
    # Preço "de" — usado na landing para exibir o risco de preço cheio
    preco_de_mensal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, verbose_name="Preço DE Mensal (R$)", help_text="Preço cheio para exibição como riscado na landing page. 0 = não exibir risco.")
    preco_de_anual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, verbose_name="Preço DE Anual (R$)", help_text="Preço cheio para exibição como riscado na landing page. 0 = não exibir risco.")

    # Limites e Features
    limite_membros = models.PositiveIntegerField(default=50, help_text="Número máximo de pessoas ativas (consideradas para relatórios). 0 para ilimitado.", verbose_name="Limite de Pessoas Ativas")
    limite_igrejas = models.PositiveIntegerField(default=1, help_text="Número máximo de igrejas/congregações. 0 para ilimitado.")
    permite_modulo_secretaria = models.BooleanField(default=True, verbose_name="Permite Módulo Secretaria?")
    permite_modulo_agenda = models.BooleanField(default=True, verbose_name="Permite Módulo Agenda?")
    permite_modulo_eventos = models.BooleanField(default=True, verbose_name="Permite Módulo Eventos?")
    permite_modulo_escola_biblica = models.BooleanField(default=True, verbose_name="Permite Módulo Escola Bíblica?")
    permite_modulo_financeiro = models.BooleanField(default=True, verbose_name="Permite Módulo Financeiro?")
    permite_modulo_comunicacao = models.BooleanField(default=False, verbose_name="Permite Módulo de Comunicação?")
    permite_suporte_tickets = models.BooleanField(default=True, verbose_name="Permite Suporte via Tickets?")
    suporte_prioritario = models.BooleanField(default=False, verbose_name="Suporte Prioritário?")
    

    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Plano Ativo no Sistema?")
    is_visible = models.BooleanField(default=True, help_text="Marque para exibir este plano nas páginas de preço/venda.")
    liberado_publicamente = models.BooleanField(
        default=False,
        verbose_name="Liberado publicamente?",
        help_text="Controla se este plano pode aparecer para todos os usuários nos fluxos do sistema.",
    )
    contratacao_publica_liberada = models.BooleanField(
        default=False,
        verbose_name="Contratação pública liberada?",
        help_text="Controla se este plano pode ser contratado por qualquer ministério fora da lista piloto.",
    )
    ordem_liberacao = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem de liberação",
        help_text="Ajuda a organizar o rollout gradual dos planos.",
    )
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Stripe Product ID", help_text="ID do produto no Stripe (prod_...).")
    stripe_price_id_mensal = models.CharField(max_length=100, blank=True, null=True, verbose_name="Stripe Price ID (Mensal)")
    stripe_price_id_anual = models.CharField(max_length=100, blank=True, null=True, verbose_name="Stripe Price ID (Anual)")

    def __str__(self):
        return self.get_nome_display() # Usa o método automático do Django

    def get_modulos_configurados(self):
        """Retorna a lista de módulos e status para renderização dinâmica nos cards."""
        return [
            {
                'campo': campo,
                'nome': nome,
                'ativo': bool(getattr(self, campo, False)),
            }
            for campo, nome, _ in self.MODULOS_CONFIGURAVEIS
        ]

    def get_modulos_configurados_marketing(self):
        """Retorna módulos com nomenclatura orientada à página de vendas."""
        return [
            {
                'campo': campo,
                'nome': nome_marketing,
                'ativo': bool(getattr(self, campo, False)),
            }
            for campo, _, nome_marketing in self.MODULOS_CONFIGURAVEIS
        ]

    def get_suportes_configurados(self):
        """Retorna suportes e status para renderização dinâmica nos cards."""
        return [
            {
                'campo': campo,
                'nome': nome,
                'ativo': bool(getattr(self, campo, False)),
            }
            for campo, nome, _ in self.SUPORTES_CONFIGURAVEIS
        ]

    def get_suportes_configurados_marketing(self):
        """Retorna suportes com nomenclatura orientada à página de vendas."""
        return [
            {
                'campo': campo,
                'nome': nome_marketing,
                'ativo': bool(getattr(self, campo, False)),
            }
            for campo, _, nome_marketing in self.SUPORTES_CONFIGURAVEIS
        ]


    class Meta:
        verbose_name = "Plano de Assinatura"
        verbose_name_plural = "Planos de Assinatura"
        ordering = ['ordem_liberacao', 'preco_mensal']


class LiberacaoPlanoMinisterio(models.Model):
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        related_name='liberacoes_planos',
        verbose_name="Ministério",
    )
    plano = models.ForeignKey(
        Plano,
        on_delete=models.CASCADE,
        related_name='liberacoes_ministerios',
        verbose_name="Plano",
    )
    pode_visualizar = models.BooleanField(default=True, verbose_name="Pode visualizar?")
    pode_contratar = models.BooleanField(default=True, verbose_name="Pode contratar?")
    acesso_beta = models.BooleanField(default=True, verbose_name="Acesso beta?")
    ativo = models.BooleanField(default=True, verbose_name="Liberação ativa?")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ministerio.nome_fantasia} -> {self.plano.get_nome_display()}"

    class Meta:
        verbose_name = "Liberação de Plano por Ministério"
        verbose_name_plural = "Liberações de Planos por Ministério"
        unique_together = ('ministerio', 'plano')
        ordering = ['ministerio__nome_fantasia', 'plano__ordem_liberacao', 'plano__preco_mensal']



class AssinaturaMinisterio(models.Model):
    STATUS_ASSINATURA_CHOICES = [
        ('ativa', 'Ativa'),
        ('pendente_pagamento', 'Pendente de Pagamento'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
        ('gratuita', 'Gratuita'),
    ]
    CICLO_PAGAMENTO_CHOICES = [
        ('mensal', 'Mensal'),
        ('anual', 'Anual'),
    ]
    ministerio = models.OneToOneField(
        Ministerio,
        on_delete=models.CASCADE,
        related_name='assinatura',
        verbose_name="Ministério"
    )
    plano = models.ForeignKey(
        Plano,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assinaturas',
        verbose_name="Plano Contratado"
    )
    data_inicio = models.DateTimeField(verbose_name="Data de Início")
    data_fim = models.DateTimeField(verbose_name="Data de Fim", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_ASSINATURA_CHOICES, default='pendente_pagamento', verbose_name="Status")
    ciclo_pagamento = models.CharField(
        max_length=10,
        choices=CICLO_PAGAMENTO_CHOICES,
        null=True, blank=True,
        verbose_name="Ciclo de Pagamento"
    )
    id_transacao_gateway = models.CharField(max_length=200, blank=True, null=True, verbose_name="ID da Transação (Gateway)")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    periodo_cortesia_ativo = models.BooleanField(default=False, verbose_name="Período de Cortesia Ativo?")
    data_inicio_cortesia = models.DateTimeField(null=True, blank=True, verbose_name="Início da Cortesia")
    data_ultima_falha_pagamento = models.DateTimeField(null=True, blank=True, verbose_name="Última Falha de Pagamento")
    tentativas_falha_pagamento = models.IntegerField(default=0, verbose_name="Tentativas Falhas de Pagamento")
    data_fim_graca_inadimplencia = models.DateTimeField(null=True, blank=True, verbose_name="Fim do Período de Graça (Inadimplência)")
    data_inicio_trial = models.DateTimeField(null=True, blank=True, verbose_name="Início do Período de Trial")
    trial_ativo = models.BooleanField(default=False, verbose_name="Trial Ativo?")
    dias_trial_totais = models.IntegerField(default=14, verbose_name="Total de Dias de Trial")

    def __str__(self):
        plano_nome = self.plano.get_nome_display() if self.plano else "N/D"
        return f"Assinatura de {self.ministerio.nome_fantasia} - Plano: {plano_nome} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Assinatura do Ministério"
        verbose_name_plural = "Assinaturas dos Ministérios"
        ordering = ['-data_fim', 'ministerio__nome_fantasia']

    def is_periodo_cortesia_valido(self):
        """Verifica se o período de cortesia está ativo e dentro da validade de 3 dias."""
        if self.periodo_cortesia_ativo and self.data_inicio_cortesia:
            data_fim_cortesia = self.data_inicio_cortesia + timedelta(days=3)
            return timezone.now() < data_fim_cortesia
        return False

class AtualizacaoSistema(models.Model):
    titulo = models.CharField(max_length=200)
    versao = models.CharField(max_length=20, blank=True, null=True, help_text="Ex: 1.2.3")
    data_publicacao = models.DateField(default=timezone.now)
    conteudo = models.TextField(help_text="Descreva as atualizações e novidades. Você pode usar Markdown aqui se configurar um renderizador.")
    publicado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Atualização do Sistema"
        verbose_name_plural = "Atualizações do Sistema"
        ordering = ['-data_publicacao', '-versao']

    def __str__(self):
        return f"{self.titulo} ({self.data_publicacao.strftime('%d/%m/%Y')})"


# ---------------------------------------------------------------------------
# MÉTRICAS DE FUNIL — rastreia os eventos-chave da jornada de conversão
# ---------------------------------------------------------------------------
class EventoFunil(models.Model):
    TIPO_CHOICES = [
        ('visita_landing', 'Visita à Landing Page'),
        ('clique_cta', 'Clique no CTA da Landing'),
        ('cadastro', 'Cadastro Realizado'),
        ('primeiro_login', 'Primeiro Login'),
        ('checkout_iniciado', 'Checkout Iniciado'),
        ('checkout_completo', 'Checkout Completo (Pago)'),
        ('pagamento_confirmado', 'Pagamento Confirmado (Invoice Paid)'),
        ('plano_cancelado', 'Plano Cancelado'),
        ('upgrade', 'Upgrade de Plano'),
    ]

    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, db_index=True)
    ministerio = models.ForeignKey(
        'Ministerio',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='eventos_funil',
        verbose_name='Ministério',
    )
    plano = models.ForeignKey(
        'Plano',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='eventos_funil',
        verbose_name='Plano',
    )
    ciclo_pagamento = models.CharField(
        max_length=10, blank=True, null=True,
        choices=[('mensal', 'Mensal'), ('anual', 'Anual')],
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Dados contextuais extras (user-agent resumido, origem etc.)
    extra = models.JSONField(default=dict, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Evento de Funil'
        verbose_name_plural = 'Eventos de Funil'
        ordering = ['-criado_em']

    def __str__(self):
        ministerio_nome = self.ministerio.nome_fantasia if self.ministerio else '(anônimo)'
        return f"{self.get_tipo_display()} — {ministerio_nome} ({self.criado_em:%d/%m/%Y %H:%M})"


class CodigoPromocional(models.Model):
    """Rastreia cupons/códigos promocionais do Stripe para uso no checkout."""
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('expirado', 'Expirado'),
        ('inativo', 'Inativo'),
    ]
    
    codigo_stripe = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID do Cupom no Stripe",
        help_text="Ex: promo_123abc. Deve existir na sua conta Stripe."
    )
    descricao = models.CharField(max_length=200, blank=True, verbose_name="Descrição Interna")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo', verbose_name="Status")
    percentual_desconto = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        verbose_name="% de Desconto (informativo)"
    )
    data_inicio = models.DateField(verbose_name="Data de Início", default=timezone.now)
    data_termino = models.DateField(verbose_name="Data de Término", blank=True, null=True)
    usos_restantes = models.IntegerField(
        blank=True, null=True,
        verbose_name="Usos Restantes (None = ilimitado)"
    )
    
    # Rastreamento
    vezes_usado = models.IntegerField(default=0, verbose_name="Vezes Usado")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Código Promocional"
        verbose_name_plural = "Códigos Promocionais"
        ordering = ['-data_inicio']

    def __str__(self):
        return f"{self.codigo_stripe} ({self.get_status_display()})"
    
    def is_valido(self):
        """Verifica se o cupom é válido e ainda pode ser usado."""
        from django.utils import timezone as tz
        
        if self.status != 'ativo':
            return False
        
        # Verificar data de término
        if self.data_termino and tz.now().date() > self.data_termino:
            self.status = 'expirado'
            self.save(update_fields=['status'])
            return False
        
        # Verificar usos restantes
        if self.usos_restantes is not None and self.usos_restantes <= 0:
            return False
        
        return True
    
    def registrar_uso(self):
        """Incrementa contador de usos e decrementa limite se houver."""
        self.vezes_usado += 1
        if self.usos_restantes is not None:
            self.usos_restantes -= 1
        self.save(update_fields=['vezes_usado', 'usos_restantes'])


class CategoriaGastoSistema(models.Model):
    nome = models.CharField(max_length=80, unique=True, verbose_name='Categoria')
    slug = models.SlugField(max_length=80, unique=True, verbose_name='Slug')
    ordem = models.PositiveIntegerField(default=100, verbose_name='Ordem')
    ativo = models.BooleanField(default=True, verbose_name='Ativa')

    class Meta:
        verbose_name = 'Categoria de Gasto do Sistema'
        verbose_name_plural = 'Categorias de Gastos do Sistema'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class GastoSistema(models.Model):
    categoria = models.ForeignKey(
        CategoriaGastoSistema,
        on_delete=models.PROTECT,
        related_name='gastos',
        verbose_name='Categoria',
    )
    descricao = models.CharField(max_length=255, verbose_name='Descricao')
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor')
    data_competencia = models.DateField(verbose_name='Competencia')
    data_pagamento = models.DateField(null=True, blank=True, verbose_name='Data do pagamento')
    observacao = models.TextField(blank=True, verbose_name='Observacao')
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gastos_sistema_criados',
        verbose_name='Criado por',
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Gasto do Sistema'
        verbose_name_plural = 'Gastos do Sistema'
        ordering = ['-data_competencia', '-id']
        indexes = [
            models.Index(fields=['-data_competencia']),
            models.Index(fields=['categoria', '-data_competencia']),
        ]

    def __str__(self):
        return f"{self.data_competencia:%m/%Y} - {self.descricao}"


def normalizar_texto_catalogo(valor: str) -> str:
    """Normaliza texto para busca sem acento e comparação estável."""
    if not valor:
        return ''
    texto = unicodedata.normalize('NFKD', str(valor).strip().lower())
    texto = ''.join(ch for ch in texto if not unicodedata.combining(ch))
    return ' '.join(texto.split())


class Pais(models.Model):
    """Catálogo global de países (base para i18n/localização)."""
    codigo_iso2 = models.CharField(max_length=2, unique=True, verbose_name='Código ISO2')
    codigo_iso3 = models.CharField(max_length=3, unique=True, blank=True, null=True, verbose_name='Código ISO3')
    nome_oficial = models.CharField(max_length=120, verbose_name='Nome oficial')
    nome_curto = models.CharField(max_length=120, blank=True, verbose_name='Nome curto')
    nome_normalizado = models.CharField(max_length=140, db_index=True, editable=False)
    idioma_padrao = models.CharField(max_length=10, default='pt-BR', verbose_name='Idioma padrão')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ['nome_oficial']
        constraints = [
            models.UniqueConstraint(fields=['codigo_iso3'], condition=models.Q(codigo_iso3__isnull=False), name='uq_pais_iso3_not_null'),
        ]

    def save(self, *args, **kwargs):
        self.codigo_iso2 = (self.codigo_iso2 or '').upper().strip()
        self.codigo_iso3 = (self.codigo_iso3 or '').upper().strip() or None
        self.nome_normalizado = normalizar_texto_catalogo(self.nome_curto or self.nome_oficial)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome_oficial} ({self.codigo_iso2})"

    def nome_exibicao(self, idioma='pt-BR'):
        traducao = self.traducoes.filter(idioma=idioma).only('nome').first()
        if traducao:
            return traducao.nome
        if self.idioma_padrao and self.idioma_padrao != idioma:
            traducao_padrao = self.traducoes.filter(idioma=self.idioma_padrao).only('nome').first()
            if traducao_padrao:
                return traducao_padrao.nome
        return self.nome_curto or self.nome_oficial


class SubdivisaoAdministrativa(models.Model):
    """Subdivisão administrativa por país (estado/província/região)."""
    NIVEL_ESTADO = 'estado'
    NIVEL_PROVINCIA = 'provincia'
    NIVEL_REGIAO = 'regiao'
    NIVEL_DISTRITO = 'distrito'
    NIVEL_CHOICES = [
        (NIVEL_ESTADO, 'Estado'),
        (NIVEL_PROVINCIA, 'Província'),
        (NIVEL_REGIAO, 'Região'),
        (NIVEL_DISTRITO, 'Distrito'),
    ]

    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name='subdivisoes')
    codigo = models.CharField(max_length=20, verbose_name='Código da subdivisão')
    nome = models.CharField(max_length=120, verbose_name='Nome')
    nome_normalizado = models.CharField(max_length=140, db_index=True, editable=False)
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default=NIVEL_ESTADO, verbose_name='Nível')
    ativo = models.BooleanField(default=True, verbose_name='Ativa')

    class Meta:
        verbose_name = 'Subdivisão administrativa'
        verbose_name_plural = 'Subdivisões administrativas'
        ordering = ['pais__nome_oficial', 'nome']
        constraints = [
            models.UniqueConstraint(fields=['pais', 'codigo'], name='uq_subdivisao_pais_codigo'),
            models.UniqueConstraint(fields=['pais', 'nome_normalizado', 'nivel'], name='uq_subdivisao_pais_nome_nivel'),
        ]

    def save(self, *args, **kwargs):
        self.codigo = (self.codigo or '').upper().strip()
        self.nome_normalizado = normalizar_texto_catalogo(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.pais.codigo_iso2}"

    def nome_exibicao(self, idioma='pt-BR'):
        traducao = self.traducoes.filter(idioma=idioma).only('nome').first()
        if traducao:
            return traducao.nome
        return self.nome


class CidadeCatalogo(models.Model):
    """Cidade global com suporte a país/subdivisão e traduções."""
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name='cidades')
    subdivisao = models.ForeignKey(
        SubdivisaoAdministrativa,
        on_delete=models.PROTECT,
        related_name='cidades',
        null=True,
        blank=True,
    )
    nome = models.CharField(max_length=160, verbose_name='Nome')
    nome_normalizado = models.CharField(max_length=180, db_index=True, editable=False)
    ativo = models.BooleanField(default=True, verbose_name='Ativa')

    class Meta:
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'
        ordering = ['pais__nome_oficial', 'subdivisao__nome', 'nome']
        constraints = [
            models.UniqueConstraint(
                fields=['pais', 'subdivisao', 'nome_normalizado'],
                name='uq_cidade_pais_subdivisao_nome'
            ),
        ]
        indexes = [
            models.Index(fields=['pais', 'subdivisao', 'nome_normalizado']),
            models.Index(fields=['nome_normalizado']),
        ]

    def save(self, *args, **kwargs):
        self.nome_normalizado = normalizar_texto_catalogo(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.subdivisao:
            return f"{self.nome}/{self.subdivisao.codigo}"
        return f"{self.nome}/{self.pais.codigo_iso2}"

    def nome_exibicao(self, idioma='pt-BR'):
        traducao = self.traducoes.filter(idioma=idioma).only('nome').first()
        if traducao:
            return traducao.nome
        return self.nome


class PaisTraducao(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='traducoes')
    idioma = models.CharField(max_length=10, db_index=True)
    nome = models.CharField(max_length=120)

    class Meta:
        verbose_name = 'Tradução de país'
        verbose_name_plural = 'Traduções de países'
        constraints = [
            models.UniqueConstraint(fields=['pais', 'idioma'], name='uq_pais_traducao_idioma'),
        ]

    def __str__(self):
        return f"{self.pais.codigo_iso2} [{self.idioma}]"


class SubdivisaoTraducao(models.Model):
    subdivisao = models.ForeignKey(SubdivisaoAdministrativa, on_delete=models.CASCADE, related_name='traducoes')
    idioma = models.CharField(max_length=10, db_index=True)
    nome = models.CharField(max_length=120)

    class Meta:
        verbose_name = 'Tradução de subdivisão'
        verbose_name_plural = 'Traduções de subdivisões'
        constraints = [
            models.UniqueConstraint(fields=['subdivisao', 'idioma'], name='uq_subdivisao_traducao_idioma'),
        ]

    def __str__(self):
        return f"{self.subdivisao.codigo} [{self.idioma}]"


class CidadeTraducao(models.Model):
    cidade = models.ForeignKey(CidadeCatalogo, on_delete=models.CASCADE, related_name='traducoes')
    idioma = models.CharField(max_length=10, db_index=True)
    nome = models.CharField(max_length=160)

    class Meta:
        verbose_name = 'Tradução de cidade'
        verbose_name_plural = 'Traduções de cidades'
        constraints = [
            models.UniqueConstraint(fields=['cidade', 'idioma'], name='uq_cidade_traducao_idioma'),
        ]

    def __str__(self):
        return f"{self.cidade.nome} [{self.idioma}]"