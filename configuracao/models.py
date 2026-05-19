from django.db import models
from django.core.exceptions import ValidationError
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
    modelo_carta_recomendacao = models.CharField(
        max_length=40,
        default='padrao',
        blank=True,
        verbose_name='Modelo da Carta de Recomendacao',
        help_text='Codigo do modelo selecionado para carta de recomendacao.'
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