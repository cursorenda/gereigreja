# c:\Gereigreja\configuracao\models.py
from django.db import models
from django.conf import settings # Necessário para referenciar o User model padrão do Django
from django.utils import timezone # Importar timezone se usar default=timezone.now

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

    def __str__(self):
        return self.nome_fantasia

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

    def __str__(self):
        user_display = self.user.get_full_name() or self.user.username
        return f"Perfil de {user_display} ({self.organizacao.nome_fantasia})"

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"


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
    logo1 = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name="Logo 1")
    logo2 = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name="Logo 2")
    
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
