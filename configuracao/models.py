# c:\Gereigreja\configuracao\models.py
from django.db import models
from django.conf import settings # Necessário para referenciar o User model padrão do Django
from django.utils import timezone # Importar timezone se usar default=timezone.now
import uuid # Para nomes de arquivo únicos
import os   # Para manipulação de caminhos
from datetime import timedelta # Para calcular data_fim da assinatura
from django.apps import apps # Para import tardio e evitar circularidade


# --- Função para upload_to do logo da Organização ---
def get_organizacao_logo_upload_path(instance, filename):
    """ Gera um caminho de upload único para os logos das organizações. """
    ext = os.path.splitext(filename)[1] # Pega a extensão .jpg, .png, etc.
    return os.path.join('logos_organizacoes', f'org_{instance.pk_or_uuid}_{uuid.uuid4().hex}{ext}')

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

# --- Modelo para a Organização/Ministério ---
class Organizacao(models.Model):
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
        related_name='organizacoes_administradas',
        verbose_name="Administrador Principal"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    ativo = models.BooleanField(
        default=False,
        verbose_name="Ativo (Aprovado pelo Desenvolvedor)",
        help_text="Organizações inativas podem ter acesso limitado até serem aprovadas."
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
        upload_to=get_organizacao_logo_upload_path, # Função para gerar o caminho
        null=True,
        blank=True,
        verbose_name="Logo da Organização"
    )
    def __str__(self):
        return self.nome_fantasia

    class Meta:
        verbose_name = "Organização"
        verbose_name_plural = "Organizações"
        ordering = ['nome_fantasia']

    def save(self, *args, **kwargs):
        # Define um atributo temporário pk_or_uuid que será usado pela função de upload
        # se o objeto ainda não tiver um PK (ou seja, está sendo criado).
        # Isso ajuda a função de upload a ter um identificador mesmo antes do save completo.
        self.pk_or_uuid = self.pk or uuid.uuid4().hex
        super().save(*args, **kwargs)

    def verificar_elegibilidade_plano_gratuito(self):
        """
        Verifica se a organização é elegível para o plano gratuito.
        Condições:
        1. Ter exatamente uma igreja.
        2. Essa igreja ser do tipo 'independente'.
        3. Essa igreja ter no máximo 50 membros ativos.
        """
        if self.igrejas.count() == 1:
            igreja_unica = self.igrejas.first()
            if igreja_unica.tipo_igreja == 'independente':
                try:
                    Membro = apps.get_model('secretaria', 'Membro')
                    membros_ativos_count = Membro.objects.filter(
                        igreja=igreja_unica,
                        status__considerar_ativo_relatorios=True # Do modelo Tiposstatus em secretaria
                    ).count()
                    return membros_ativos_count <= 50
                except LookupError: # Caso o modelo Membro ou app secretaria não seja encontrado
                    return False
        return False        

# --- Modelo para o Perfil do Usuário ---
class PerfilUsuario(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil' # related_name útil para acessar perfil a partir do user
    )
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.CASCADE, # Ou models.PROTECT se um perfil impedir deletar Org
        related_name='perfis_usuarios'
    )
    igrejas_permitidas = models.ManyToManyField(
        'Igreja', # <-- Use a string 'Igreja'
        blank=True,
        related_name='usuarios_permitidos',
        verbose_name="Igrejas Permitidas",
        help_text="Selecione as igrejas específicas que este usuário pode gerenciar (deixe em branco para acesso baseado apenas no papel/organização)."
    )
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True, verbose_name="Foto do Perfil")
 # --- NOVOS CAMPOS DE CONTATO E ATUALIZAÇÃO ---
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
        auto_now=True, # Atualiza automaticamente ao salvar
        verbose_name="Última Atualização"
    )
    # --- FIM NOVOS CAMPOS ---

    def __str__(self):
        user_display = self.user.get_full_name() or self.user.username
        return f"Perfil de {user_display} ({self.organizacao.nome_fantasia})"

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

# --- Funções para upload_to dos logos da Igreja ---
def get_logo_upload_path(instance, filename, logo_type_prefix):
    """
    Gera um caminho de upload único para os logos da igreja.
    Ex: logos_igrejas/igreja_123/logo1_uuidaleatorio.jpg
    """
    ext = os.path.splitext(filename)[1] # Pega a extensão .jpg, .png, etc.
    # Gera um nome de arquivo único usando UUID
    unique_filename = f"{logo_type_prefix}_{uuid.uuid4().hex}{ext}"
    # Organiza os logos em uma pasta por ID da igreja
    # instance.pk pode ser None se a igreja ainda não foi salva (caso de criação)
    # Django lida com isso: salva o modelo primeiro, obtém o PK, depois salva o arquivo.
    return os.path.join('logos_igrejas', f'igreja_{instance.pk_or_initial}', unique_filename)

def logo1_upload_to_path(instance, filename):
    instance.pk_or_initial = instance.pk or "nova" # Para o caso de nova igreja
    return get_logo_upload_path(instance, filename, 'logo1')

def logo2_upload_to_path(instance, filename):
    instance.pk_or_initial = instance.pk or "nova" # Para o caso de nova igreja
    return get_logo_upload_path(instance, filename, 'logo2')


# --- Modelo para cada Igreja (Sede, Regional, Congregação) ---
class Igreja(models.Model):
    # --- Relacionamentos ---
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.CASCADE, # Se deletar Org, deleta igrejas
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
    numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=255, blank=True, null=True, verbose_name="Bairro")
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
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro", null=True) # Adicionado null=True temporariamente se houver dados existentes
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização", null=True) # Adicionado null=True temporariamente

    def __str__(self):
        org_nome = self.organizacao.nome_fantasia if self.organizacao else "Sem Organização"
        return f"{self.nome_igreja} ({self.get_tipo_igreja_display()}) - [{org_nome}]"

    def get_descendants(self, include_self=False):
        """
        Retorna um QuerySet de todas as igrejas descendentes (subordinadas diretas e indiretas).
        """
        descendants = Igreja.objects.none()
        if include_self:
            descendants |= Igreja.objects.filter(pk=self.pk)

        children = self.igrejas_subordinadas.all()
        
        for child in children:
            descendants |= Igreja.objects.filter(pk=child.pk)
            descendants |= child.get_descendants(include_self=False)
        
        return descendants.distinct()

    class Meta:
        verbose_name = "Igreja"
        verbose_name_plural = "Igrejas"
        ordering = ['organizacao', 'nome_igreja']

        unique_together = ('organizacao', 'nome_igreja')

# --- NOVOS MODELOS PARA PLANOS E ASSINATURAS ---

class Plano(models.Model):
    NOME_CHOICES = [
        ('mensal', 'Mensal'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
        ('gratuito', 'Gratuito'),
    ]
    nome = models.CharField(max_length=50, choices=NOME_CHOICES, unique=True, verbose_name="Nome do Plano")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço (R$)")
    duracao_dias = models.IntegerField(verbose_name="Duração em Dias", help_text="Ex: 30, 90, 365. Para Gratuito, pode ser um valor simbólico alto ou não usado se o status da assinatura for 'gratuita'.")
    ativo = models.BooleanField(default=True, verbose_name="Plano Ativo?")
    codigo_referencia_gateway = models.CharField(max_length=100, blank=True, null=True, verbose_name="Código de Referência (Gateway)", help_text="ID do plano no gateway de pagamento, se aplicável.")

    def __str__(self):
        return f"{self.get_nome_display()} - R$ {self.preco}"

    class Meta:
        verbose_name = "Plano de Assinatura"
        verbose_name_plural = "Planos de Assinatura"
        ordering = ['preco']


class AssinaturaOrganizacao(models.Model):
    STATUS_ASSINATURA_CHOICES = [
        ('ativa', 'Ativa'),
        ('pendente_pagamento', 'Pendente de Pagamento'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
        ('gratuita', 'Gratuita'),
    ]
    organizacao = models.OneToOneField( # Garante uma assinatura por organização
        Organizacao,
        on_delete=models.CASCADE,
        related_name='assinatura', # Acesso fácil: organizacao.assinatura
        verbose_name="Organização"
    )
    plano = models.ForeignKey(
        Plano,
        on_delete=models.SET_NULL,
        null=True, blank=True, # Plano pode ser nulo se for 'gratuita' e gerenciada de outra forma
        related_name='assinaturas',
        verbose_name="Plano Contratado"
    )
    data_inicio = models.DateTimeField(verbose_name="Data de Início")
    data_fim = models.DateTimeField(verbose_name="Data de Fim", blank=True, null=True) # Nulo para 'gratuita' vitalícia
    status = models.CharField(max_length=20, choices=STATUS_ASSINATURA_CHOICES, default='pendente_pagamento', verbose_name="Status")
    id_transacao_gateway = models.CharField(max_length=200, blank=True, null=True, verbose_name="ID da Transação (Gateway)")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
     # --- Campos para Período de Graça/Cortesia ---
    periodo_cortesia_ativo = models.BooleanField(default=False, verbose_name="Período de Cortesia Ativo?")
    data_inicio_cortesia = models.DateTimeField(null=True, blank=True, verbose_name="Início da Cortesia")
    # --- Fim Campos Cortesia ---
    def __str__(self):
        plano_nome = self.plano.get_nome_display() if self.plano else "N/D"
        return f"Assinatura de {self.organizacao.nome_fantasia} - Plano: {plano_nome} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Assinatura da Organização"
        verbose_name_plural = "Assinaturas das Organizações"
        ordering = ['-data_fim', 'organizacao__nome_fantasia']

    def is_periodo_cortesia_valido(self):
        """Verifica se o período de cortesia está ativo e dentro da validade de 3 dias."""
        if self.periodo_cortesia_ativo and self.data_inicio_cortesia:
            # Calcula a data de fim da cortesia (3 dias após o início)
            data_fim_cortesia = self.data_inicio_cortesia + timedelta(days=3)
            # Verifica se a data atual é menor ou igual à data de fim da cortesia
            return timezone.now() <= data_fim_cortesia
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