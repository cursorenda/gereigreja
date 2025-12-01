from django.db import models
from django.utils import timezone
from django.conf import settings
from secretaria.models import Membro

# --- MODELO DEPARTAMENTO ---
class Departamento(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


# Sugestão de nomes para facilitar o cadastro inicial
DEPARTAMENTOS_SUGERIDOS = [
    "Infantil",
    "Adolescentes",
    "Jovens",
    "Adultos",
    "Discipulado",
    "Casais",
    "Senhoras",
    "Senhores",
    "Música",
    "Missões"
]

# --- MODELOS DE APOIO PARA EBD ---
class AnoLetivo(models.Model):
    """Ano letivo da EBD."""
    ano = models.PositiveIntegerField(unique=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-ano']
        verbose_name = 'Ano Letivo'
        verbose_name_plural = 'Anos Letivos'

    def __str__(self):
        return str(self.ano)

# --- NOVO MODELO: Período da EBD ---
class PeriodoEBD(models.Model):
    """Período da EBD (trimestre, quadrimestre, semestre, ano) vinculado ao ano letivo."""
    ano_letivo = models.ForeignKey('AnoLetivo', on_delete=models.CASCADE, related_name='periodos')
    numero = models.PositiveIntegerField(verbose_name='Número do Período')
    tipo = models.CharField(max_length=20, choices=[
        ('trimestre', 'Trimestre'),
        ('quadrimestre', 'Quadrimestre'),
        ('semestre', 'Semestre'),
        ('ano', 'Ano'),
    ], default='trimestre', verbose_name='Tipo de Período')
    data_inicio = models.DateField()
    data_fim = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('ano_letivo', 'numero', 'tipo')
        ordering = ['ano_letivo', 'numero']
        verbose_name = 'Período da EBD'
        verbose_name_plural = 'Períodos da EBD'

    def __str__(self):
        return f"{self.get_tipo_display()} {self.numero} ({self.ano_letivo.ano})"

class Classe(models.Model):
    """Classe de alunos da EBD (faixa etária, nome, etc)."""
    DEPARTAMENTO_CHOICES = [
        ("INFANTIL", "Infantil"),
        ("ADULTO", "Adulto"),
    ]
    nome = models.CharField(max_length=100, unique=True)
    departamento = models.CharField(max_length=20, choices=DEPARTAMENTO_CHOICES, default="INFANTIL")
    faixa_etaria = models.CharField(max_length=50, blank=True)
    descricao = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'

    def __str__(self):
        return self.nome





class Turma(models.Model):
    """Turma de alunos da EBD, vinculada a um ano letivo e classe."""
    nome = models.CharField(max_length=100)
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT)
    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.PROTECT)
    membros = models.ManyToManyField(Membro, related_name='turmas_ebd', blank=True, verbose_name='Colaboradores/Membros da Turma')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["ano_letivo"]),
        ]

    def __str__(self):
        return f"{self.nome} ({self.ano_letivo})"

    def get_professor_nome(self):
        from secretaria.models import MembroCargo
        cargos = MembroCargo.objects.filter(
            membro__in=self.membros.all(),
            cargo__is_ebd=True,
            cargo__nome__icontains='professor',
            data_fim__isnull=True
        ).select_related('membro').order_by('membro__nome')
        if cargos.exists():
            return cargos.first().membro.nome
        return ''

class Aluno(models.Model):
    """Aluno matriculado na EBD."""
    nome = models.CharField(max_length=150)
    data_nascimento = models.DateField(null=True, blank=True)
    turma = models.ForeignKey('Turma', on_delete=models.PROTECT, related_name='alunos')
    responsavel = models.CharField(max_length=150, blank=True)
    telefone_responsavel = models.CharField(max_length=20, blank=True)
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["ativo"]),
        ]

    def __str__(self):
        return self.nome

class Frequencia(models.Model):
    """Registro de presença do aluno por data."""
    aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE)
    data = models.DateField()
    presente = models.BooleanField(default=True)
    observacao = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("aluno", "data")
        indexes = [
            models.Index(fields=["data"]),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.data > timezone.now().date():
            raise ValidationError("Não é possível registrar frequência em data futura.")

    def __str__(self):
        return f"{self.aluno} - {self.data} - {'Presente' if self.presente else 'Faltou'}"

class Licao(models.Model):
    """Lição ministrada para uma turma em uma data específica."""
    turma = models.ForeignKey('Turma', on_delete=models.CASCADE)
    data = models.DateField()
    tema = models.CharField(max_length=200)  # Verifique se o modelo Licao possui os campos: turma, data, tema, material, observacoes, horario, status, professor
    descricao = models.TextField(blank=True)
    material = models.CharField(max_length=255, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    horario = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('ativa', 'Ativa'), ('rascunho', 'Rascunho')], default='ativa')
    professor = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tema} - {self.data}"


# Oferta por Classe e Data
class OfertaClasse(models.Model):
    """Oferta arrecadada por classe em uma data."""
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    data = models.DateField()
    valor = models.DecimalField("Oferta (R$)", max_digits=8, decimal_places=2)
    observacao = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("classe", "data")
        verbose_name = "Oferta da Classe"
        verbose_name_plural = "Ofertas das Classes"

    def __str__(self):
        return f"{self.classe} - {self.data} - R$ {self.valor}"


# Registro de transferências de alunos entre turmas/classes
class TransferenciaAluno(models.Model):
    """Registro de transferências de alunos entre turmas/classes."""
    aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE, related_name='transferencias')
    turma_origem = models.ForeignKey('Turma', on_delete=models.SET_NULL, null=True, blank=True, related_name='transferencias_saida')
    turma_destino = models.ForeignKey('Turma', on_delete=models.PROTECT, related_name='transferencias_entrada')
    data_transferencia = models.DateField(auto_now_add=True)
    motivo = models.CharField(max_length=255, blank=True)
    usuario_responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='transferencias_realizadas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_transferencia']
        verbose_name = 'Transferência de Aluno'
        verbose_name_plural = 'Transferências de Alunos'

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.turma_origem == self.turma_destino:
            raise ValidationError("A turma de origem e destino não podem ser iguais.")

    def __str__(self):
        return f"{self.aluno} de {self.turma_origem} para {self.turma_destino} em {self.data_transferencia}"


class Avaliacao(models.Model):
    """Avaliação do aluno em uma lição."""
    aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE)
    licao = models.ForeignKey('Licao', on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    participacao = models.BooleanField(default=False)
    observacao = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("aluno", "licao")

    def __str__(self):
        return f"{self.aluno} - {self.licao} - Nota: {self.nota}"
