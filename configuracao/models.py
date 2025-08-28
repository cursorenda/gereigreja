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
    ext = os.path.splitext(filename)[1]
    # Cria um nome de arquivo único que não depende do PK do objeto.
    unique_filename = f"org_logo_{uuid.uuid4().hex}{ext}"
    return os.path.join('logos_organizacoes', unique_filename)

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

    # --- CAMPO PARA INTEGRAÇÃO COM GATEWAY DE PAGAMENTO ---
    stripe_customer_id = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="ID do Cliente no Stripe",
        help_text="ID do cliente no Stripe, usado para gerenciar assinaturas."
    )

    def __str__(self):
        return self.nome_fantasia

    

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
                        status_pessoa__considerar_ativo_relatorios=True # CORRIGIDO: Usa o novo relacionamento
                    ).count()
                    return membros_ativos_count <= 50
                except LookupError: # Caso o modelo Membro ou app secretaria não seja encontrado
                    return False
        return False        
    
    class Meta:
        verbose_name = "Organização"
        verbose_name_plural = "Organizações"
        ordering = ['nome_fantasia']

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

    def save(self, *args, **kwargs):
        print("[DEBUG MODEL] Chamou save do PerfilUsuario, foto_perfil:", self.foto_perfil)
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
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
 
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
    NOME_PLANO_CHOICES = [
        ('pioneiro', 'Pioneiro'),
        ('crescimento', 'Crescimento'),
        ('ministerio', 'Ministério'),
    ]
    nome = models.CharField(max_length=50, choices=NOME_PLANO_CHOICES, unique=True, verbose_name="Nome do Plano")
    codigo_plano = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Identificador único para o sistema (ex: 'pioneiro', 'crescimento', 'ministerio').")    
    # Preços
    preco_mensal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Mensal (R$)")
    preco_anual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Anual (R$)")

    # Limites e Features
    limite_membros = models.PositiveIntegerField(default=50, help_text="Número máximo de pessoas ativas (consideradas para relatórios). 0 para ilimitado.", verbose_name="Limite de Pessoas Ativas")
    limite_igrejas = models.PositiveIntegerField(default=1, help_text="Número máximo de igrejas/congregações. 0 para ilimitado.")
    permite_modulo_comunicacao = models.BooleanField(default=False, verbose_name="Permite Módulo de Comunicação?")
    suporte_prioritario = models.BooleanField(default=False, verbose_name="Suporte Prioritário?")
    

    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Plano Ativo no Sistema?")
    is_visible = models.BooleanField(default=True, help_text="Marque para exibir este plano nas páginas de preço/venda.")
    stripe_price_id_mensal = models.CharField(max_length=100, blank=True, null=True, verbose_name="Stripe Price ID (Mensal)")
    stripe_price_id_anual = models.CharField(max_length=100, blank=True, null=True, verbose_name="Stripe Price ID (Anual)")

    def __str__(self):
        return self.get_nome_display() # Usa o método automático do Django


    class Meta:
        verbose_name = "Plano de Assinatura"
        verbose_name_plural = "Planos de Assinatura"
        ordering = ['preco_mensal']


class AssinaturaOrganizacao(models.Model):
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
    ciclo_pagamento = models.CharField(
        max_length=10,
        choices=CICLO_PAGAMENTO_CHOICES,
        null=True, blank=True,
        verbose_name="Ciclo de Pagamento"
    )
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