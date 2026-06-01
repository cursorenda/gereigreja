from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from collections import defaultdict
import unicodedata
from secretaria.models import Membro
from configuracao.models import Igreja


def _normalizar_texto(valor):
    texto = unicodedata.normalize('NFKD', (valor or '').strip())
    texto_sem_acentos = ''.join(caractere for caractere in texto if not unicodedata.combining(caractere))
    return ' '.join(texto_sem_acentos.casefold().split())


def _get_turma_ministerio(turma):
    if turma is None:
        return None

    igreja = getattr(turma, 'igreja', None)
    if igreja and getattr(igreja, 'ministerio', None):
        return igreja.ministerio

    classe = getattr(turma, 'classe', None)
    if classe and getattr(classe, 'igreja', None) and getattr(classe.igreja, 'ministerio', None):
        return classe.igreja.ministerio

    membro = turma.membros.exclude(igreja__ministerio__isnull=True).select_related('igreja__ministerio').first()
    if membro and membro.igreja and membro.igreja.ministerio:
        return membro.igreja.ministerio

    return None


def _get_config_ebd_turma(turma):
    from configuracao.models import ConfiguracaoSistema

    igreja = getattr(turma, 'igreja', None)
    if igreja is None:
        classe = getattr(turma, 'classe', None)
        if classe is not None:
            igreja = getattr(classe, 'igreja', None)

    if igreja is not None and (
        igreja.ebd_periodo
        or igreja.ebd_dia_semana is not None
        or igreja.ebd_horario is not None
    ):
        return igreja

    ministerio = _get_turma_ministerio(turma)
    if not ministerio:
        return None
    return ConfiguracaoSistema.objects.filter(ministerio=ministerio).first()


def _get_periodo_ebd_turma_para_data(turma, data_referencia):
    if turma is None or data_referencia is None:
        return None

    config = _get_config_ebd_turma(turma)
    tipo_periodo = config.ebd_periodo if config and config.ebd_periodo else 'trimestre'

    return PeriodoEBD.objects.filter(
        ano_letivo=turma.ano_letivo,
        tipo=tipo_periodo,
        data_inicio__lte=data_referencia,
        data_fim__gte=data_referencia,
    ).first()

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
    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT,
        related_name='classes_ebd',
        null=True,
        blank=True,
        verbose_name='Igreja',
    )
    nome = models.CharField(max_length=100)
    departamento = models.CharField(max_length=20, choices=DEPARTAMENTO_CHOICES, default="INFANTIL")
    faixa_etaria = models.CharField(max_length=50, blank=True)
    descricao = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        constraints = [
            models.UniqueConstraint(fields=['igreja', 'nome'], name='uq_classe_nome_por_igreja'),
        ]

    def __str__(self):
        return self.nome





class Turma(models.Model):
    """Turma de alunos da EBD, vinculada a um ano letivo e classe."""
    nome = models.CharField(max_length=100)
    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT,
        related_name='turmas_ebd',
        null=True,
        blank=True,
        verbose_name='Igreja',
    )
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

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.classe_id and self.igreja_id and self.classe.igreja_id and self.classe.igreja_id != self.igreja_id:
            raise ValidationError('A turma deve estar vinculada a uma classe da mesma igreja.')

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


class CadastroAluno(models.Model):
    """Cadastro mestre do aluno na EBD, independente do ano/turma."""
    pessoa = models.ForeignKey(
        'secretaria.Pessoa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registros_ebd',
        verbose_name='Pessoa (Secretaria)',
    )
    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT,
        related_name='cadastros_alunos_ebd',
        verbose_name='Igreja',
    )
    nome = models.CharField(max_length=150)
    data_nascimento = models.DateField(null=True, blank=True)
    responsavel = models.CharField(max_length=150, blank=True)
    telefone_responsavel = models.CharField(max_length=20, blank=True)
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        indexes = [
            models.Index(fields=['pessoa']),
            models.Index(fields=['igreja', 'nome']),
            models.Index(fields=['ativo']),
        ]
        verbose_name = 'Cadastro de Aluno EBD'
        verbose_name_plural = 'Cadastros de Alunos EBD'

    def __str__(self):
        return self.nome

    def tentar_vincular_pessoa(self, force=False):
        if self.pessoa_id and not force:
            return self.pessoa

        pessoa = self._resolver_pessoa_existente()
        if pessoa is not None:
            self.pessoa = pessoa
        return pessoa

    def _resolver_pessoa_existente(self):
        if self.pessoa_id or not self.igreja_id:
            return self.pessoa if self.pessoa_id else None

        nome = (self.nome or '').strip()
        if not nome:
            return None

        from secretaria.models import Pessoa

        candidatos = list(Pessoa.objects.filter(igreja_id=self.igreja_id, nome__iexact=nome))
        if not candidatos:
            return None

        if self.data_nascimento:
            correspondencias_exatas = [
                pessoa for pessoa in candidatos if pessoa.nascimento == self.data_nascimento
            ]
            if len(correspondencias_exatas) == 1:
                return correspondencias_exatas[0]
            return None

        correspondencias_por_nome = [
            pessoa for pessoa in candidatos if _normalizar_texto(pessoa.nome) == _normalizar_texto(nome)
        ]
        if len(correspondencias_por_nome) == 1:
            return correspondencias_por_nome[0]
        return None

    def _sincronizar_com_pessoa(self):
        if not self.pessoa_id:
            return

        if self.pessoa.igreja_id and self.igreja_id != self.pessoa.igreja_id:
            self.igreja = self.pessoa.igreja
        if self.nome != self.pessoa.nome:
            self.nome = self.pessoa.nome
        if self.data_nascimento != self.pessoa.nascimento:
            self.data_nascimento = self.pessoa.nascimento

    def _sincronizar_matriculas(self):
        if not self.pk:
            return

        matriculas = self.matriculas.all()
        if self.pessoa_id:
            matriculas.exclude(nome=self.nome, data_nascimento=self.data_nascimento).update(
                nome=self.nome,
                data_nascimento=self.data_nascimento,
            )

    def save(self, *args, **kwargs):
        if not self.pessoa_id:
            pessoa = self._resolver_pessoa_existente()
            if pessoa is not None:
                self.pessoa = pessoa

        self._sincronizar_com_pessoa()
        super().save(*args, **kwargs)
        self._sincronizar_matriculas()

    def get_matricula_atual(self):
        return self.matriculas.select_related('turma', 'turma__ano_letivo').order_by(
            '-ativo', '-turma__ano_letivo__ano', '-updated_at', '-id'
        ).first()

    def get_matricula_referencia(self, data_referencia=None, matriculas=None):
        data_referencia = data_referencia or timezone.now().date()
        matriculas = list(matriculas if matriculas is not None else self.matriculas.select_related('turma', 'turma__ano_letivo').all())
        if not matriculas:
            return None

        matriculas_por_turma = defaultdict(list)
        for matricula in matriculas:
            matriculas_por_turma[matricula.turma_id].append(matricula)

        for turma_id in matriculas_por_turma:
            matriculas_por_turma[turma_id].sort(key=lambda item: (item.ativo, item.updated_at, item.id), reverse=True)

        transferencias = list(
            TransferenciaAluno.objects.filter(aluno__cadastro_id=self.pk)
            .select_related('turma_origem', 'turma_destino')
            .order_by('data_transferencia', 'id')
        )

        transferencia_passada = None
        transferencia_futura = None
        for transferencia in transferencias:
            if transferencia.data_transferencia and transferencia.data_transferencia <= data_referencia:
                transferencia_passada = transferencia
            elif transferencia_futura is None:
                transferencia_futura = transferencia
                break

        if transferencia_passada is not None:
            candidatas = matriculas_por_turma.get(transferencia_passada.turma_destino_id)
            if candidatas:
                return candidatas[0]

        if transferencia_futura is not None:
            candidatas = matriculas_por_turma.get(transferencia_futura.turma_origem_id)
            if candidatas:
                return candidatas[0]

        matricula_ativa = next((matricula for matricula in sorted(matriculas, key=lambda item: (item.ativo, item.updated_at, item.id), reverse=True) if matricula.ativo), None)
        if matricula_ativa is not None:
            return matricula_ativa

        return sorted(matriculas, key=lambda item: (item.updated_at, item.id), reverse=True)[0]

class Aluno(models.Model):
    """Aluno matriculado na EBD."""
    cadastro = models.ForeignKey('CadastroAluno', on_delete=models.PROTECT, related_name='matriculas')
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

    def _resolver_igreja_cadastro(self):
        if not self.turma_id:
            return None
        turma = getattr(self, 'turma', None)
        if turma is None:
            turma = Turma.objects.select_related('igreja', 'classe__igreja').filter(pk=self.turma_id).first()
        if turma is None:
            return None
        igreja = turma.igreja or getattr(turma.classe, 'igreja', None)
        if igreja is not None:
            return igreja

        igreja_ids = list(
            turma.membros.exclude(igreja_id__isnull=True)
            .values_list('igreja_id', flat=True)
            .distinct()[:2]
        )
        if len(igreja_ids) == 1:
            return Igreja.objects.filter(pk=igreja_ids[0]).first()

        return None

    def _resolver_cadastro_existente(self, igreja):
        nome = (self.nome or '').strip()
        responsavel = (self.responsavel or '').strip()
        telefone = (self.telefone_responsavel or '').strip()

        qs = CadastroAluno.objects.filter(igreja=igreja, nome__iexact=nome)
        if self.data_nascimento:
            qs = qs.filter(data_nascimento=self.data_nascimento)
        else:
            qs = qs.filter(data_nascimento__isnull=True)
            if responsavel:
                qs = qs.filter(responsavel__iexact=responsavel)
            if telefone:
                qs = qs.filter(telefone_responsavel=telefone)
        return qs.order_by('id').first()

    def _obter_ou_criar_cadastro(self):
        igreja = self._resolver_igreja_cadastro()
        if igreja is None:
            return None

        cadastro_existente = self._resolver_cadastro_existente(igreja)
        if cadastro_existente:
            return cadastro_existente

        cadastro = CadastroAluno(
            igreja=igreja,
            nome=self.nome,
            data_nascimento=self.data_nascimento,
            responsavel=self.responsavel,
            telefone_responsavel=self.telefone_responsavel,
            observacoes=self.observacoes,
            ativo=self.ativo,
        )
        cadastro.save()
        return cadastro

    def _sincronizar_do_cadastro(self):
        if not self.cadastro_id:
            return

        cadastro = getattr(self, 'cadastro', None)
        if cadastro is None or cadastro.pk != self.cadastro_id:
            cadastro = CadastroAluno.objects.select_related('pessoa').filter(pk=self.cadastro_id).first()
            if cadastro is None:
                return
            self.cadastro = cadastro

        if cadastro.pessoa_id:
            self.nome = cadastro.nome
            self.data_nascimento = cadastro.data_nascimento

    def _sincronizar_cadastro(self):
        if not self.cadastro_id:
            return

        cadastro = getattr(self, 'cadastro', None)
        if cadastro is None or cadastro.pk != self.cadastro_id:
            cadastro = CadastroAluno.objects.select_related('pessoa').filter(pk=self.cadastro_id).first()
            if cadastro is None:
                return
            self.cadastro = cadastro

        igreja = self._resolver_igreja_cadastro()
        mudou = False

        if igreja and cadastro.igreja_id != igreja.id:
            cadastro.igreja = igreja
            mudou = True

        campos_sincronizados = ['responsavel', 'telefone_responsavel', 'observacoes', 'ativo']
        if not cadastro.pessoa_id:
            campos_sincronizados = ['nome', 'data_nascimento', *campos_sincronizados]

        for field in campos_sincronizados:
            valor_atual = getattr(cadastro, field)
            valor_novo = getattr(self, field)
            if valor_atual != valor_novo:
                setattr(cadastro, field, valor_novo)
                mudou = True

        if mudou:
            cadastro.save()

    def save(self, *args, **kwargs):
        if not self.cadastro_id:
            cadastro = self._obter_ou_criar_cadastro()
            if cadastro is not None:
                self.cadastro = cadastro
        self._sincronizar_do_cadastro()
        super().save(*args, **kwargs)
        self._sincronizar_cadastro()

    def transferir_para(self, turma_destino, usuario_responsavel=None, motivo=''):
        if turma_destino.pk == self.turma_id:
            raise ValidationError('A turma de origem e destino não podem ser iguais.')

        matricula_ativa_destino = Aluno.objects.filter(
            cadastro_id=self.cadastro_id,
            turma=turma_destino,
            ativo=True,
        ).exclude(pk=self.pk).first()
        if matricula_ativa_destino is not None:
            raise ValidationError('Este aluno já possui uma matrícula ativa na turma de destino.')

        turma_origem = self.turma
        self.ativo = False
        self.save()

        matricula_destino = Aluno.objects.create(
            cadastro=self.cadastro,
            nome=self.nome,
            data_nascimento=self.data_nascimento,
            turma=turma_destino,
            responsavel=self.responsavel,
            telefone_responsavel=self.telefone_responsavel,
            observacoes=self.observacoes,
            ativo=True,
        )

        transferencia = TransferenciaAluno.objects.create(
            aluno=self,
            turma_origem=turma_origem,
            turma_destino=turma_destino,
            motivo=motivo or '',
            usuario_responsavel=usuario_responsavel,
        )
        return transferencia, matricula_destino

class Frequencia(models.Model):
    """Registro de presença do aluno por data."""
    aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE)
    data = models.DateField()
    presente = models.BooleanField(default=True)
    observacao = models.CharField(max_length=200, blank=True)
    trouxe_biblia = models.BooleanField(default=False, verbose_name='Trouxe Bíblia')
    trouxe_revista = models.BooleanField(default=False, verbose_name='Trouxe Revista')
    trouxe_visitante = models.BooleanField(default=False, verbose_name='Trouxe Visitante')
    trouxe_oferta = models.BooleanField(default=False, verbose_name='Trouxe Oferta')
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

        turma = getattr(self.aluno, 'turma', None)
        if turma is None:
            return

        periodo = _get_periodo_ebd_turma_para_data(turma, self.data)
        if periodo is None:
            raise ValidationError(
                f"A frequência em {self.data.strftime('%d/%m/%Y')} está fora do período EBD configurado para a turma."
            )

        config = _get_config_ebd_turma(turma)
        if config and config.ebd_dia_semana is not None and self.data.weekday() != config.ebd_dia_semana:
            raise ValidationError(
                f"A chamada só pode ser registrada para o dia padrão da EBD: {config.get_ebd_dia_semana_display()}."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.aluno} - {self.data} - {'Presente' if self.presente else 'Faltou'}"

class Licao(models.Model):
    """Lição ministrada para uma turma em uma data específica."""
    turma = models.ForeignKey('Turma', on_delete=models.CASCADE)
    periodo = models.ForeignKey(
        'PeriodoEBD',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='licoes',
        verbose_name='Período EBD',
    )
    data = models.DateField()
    tema = models.CharField(max_length=200)  # Verifique se o modelo Licao possui os campos: turma, data, tema, material, observacoes, horario, status, professor
    descricao = models.TextField(blank=True)
    material = models.CharField(max_length=255, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    horario = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('ativa', 'Ativa'), ('rascunho', 'Rascunho')], default='ativa')
    professor = models.ForeignKey('secretaria.Membro', on_delete=models.SET_NULL, blank=True, null=True, related_name='licoes_ministradas')
    evento_agenda = models.ForeignKey(
        'eventos.Evento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='licoes_ebd',
        verbose_name='Evento da Agenda',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['turma', 'data'], name='uq_licao_turma_data'),
        ]

    def clean(self):
        periodo = _get_periodo_ebd_turma_para_data(self.turma, self.data)
        if periodo is None:
            raise ValidationError(
                f"A lição em {self.data.strftime('%d/%m/%Y')} está fora do período EBD configurado para a turma."
            )
        self.periodo = periodo

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tema} - {self.data}"


# Oferta por Classe e Data
class OfertaClasse(models.Model):
    """Oferta arrecadada por classe em uma data."""
    turma = models.ForeignKey('Turma', on_delete=models.CASCADE, null=True, blank=True, related_name='ofertas')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    data = models.DateField()
    valor = models.DecimalField("Oferta (R$)", max_digits=8, decimal_places=2)
    observacao = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Oferta da Classe"
        verbose_name_plural = "Ofertas das Classes"
        constraints = [
            models.UniqueConstraint(fields=['turma', 'data'], name='uq_oferta_turma_data'),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.turma_id:
            if self.classe_id and self.turma.classe_id != self.classe_id:
                raise ValidationError('A oferta deve usar a mesma classe vinculada na turma.')

            periodo = _get_periodo_ebd_turma_para_data(self.turma, self.data)
            if periodo is None:
                raise ValidationError(
                    f"A oferta em {self.data.strftime('%d/%m/%Y')} está fora do período EBD configurado para a turma."
                )
        elif not self.classe_id:
            raise ValidationError('Informe a turma da oferta.')

    def save(self, *args, **kwargs):
        if self.turma_id:
            self.classe = self.turma.classe
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        referencia = self.turma if self.turma_id else self.classe
        return f"{referencia} - {self.data} - R$ {self.valor}"


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
