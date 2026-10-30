
from django.db import models
from django.conf import settings

class PermissaoCaixa(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    caixa = models.ForeignKey('ContaBancaria', on_delete=models.CASCADE, related_name='permissoes')
    pode_visualizar = models.BooleanField(default=True)
    pode_transferir = models.BooleanField(default=False)
    pode_editar = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'caixa')
        verbose_name = 'Permissão de Caixa'
        verbose_name_plural = 'Permissões de Caixas'

    def __str__(self):
        return f"{self.usuario} - {self.caixa} ({'Transferir' if self.pode_transferir else 'Visualizar'})"
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
class TransferenciaCaixa(models.Model):
    caixa_origem = models.ForeignKey('ContaBancaria', related_name='transferencias_saida', on_delete=models.PROTECT)
    caixa_destino = models.ForeignKey('ContaBancaria', related_name='transferencias_entrada', on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def clean(self):
        if self.caixa_origem == self.caixa_destino:
            raise ValidationError('Caixa de origem e destino devem ser diferentes.')
        # ✅ VALIDAÇÃO CRÍTICA: Origem e destino devem ser da MESMA Igreja
        if self.caixa_origem.igreja != self.caixa_destino.igreja:
            raise ValidationError('Ambas as caixas devem pertencer à mesma Igreja. Transferências entre igrejas não são permitidas.')
        if self.valor <= 0:
            raise ValidationError('O valor da transferência deve ser maior que zero.')
        if self.caixa_origem.saldo_atual < self.valor:
            raise ValidationError('Saldo insuficiente no caixa de origem.')

    def save(self, *args, **kwargs):
        from django.db import transaction
        self.clean()
        with transaction.atomic():
            # Atualiza os saldos
            origem = ContaBancaria.objects.select_for_update().get(pk=self.caixa_origem.pk)
            destino = ContaBancaria.objects.select_for_update().get(pk=self.caixa_destino.pk)
            origem.saldo_atual -= self.valor
            destino.saldo_atual += self.valor
            origem.save(update_fields=['saldo_atual'])
            destino.save(update_fields=['saldo_atual'])
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Transferência entre Caixas'
        verbose_name_plural = 'Transferências entre Caixas'
        ordering = ['-data']
# financeiro/models.py
from django.db import models
from django.utils import timezone
# Importa Membro, que já tem relação com Igreja -> Ministerio
from secretaria.models import Membro
from decimal import Decimal
# PRECISAMOS importar Igreja e Ministerio para adicionar as FKs
from configuracao.models import Departamento, Igreja, Ministerio # <<< ADICIONAR IMPORT
from django.conf import settings
import logging # Adicione no topo do arquivo se já não estiver
from .policies import categorias_receita_permitidas_por_fundo
logger = logging.getLogger(__name__) # Adicione no topo do arquivo


def _obter_ou_criar_fundo_departamental(igreja, evento=None):
    """Resolve o fundo padrão para lancamentos legados sem fundo explícito."""
    from django.db import connection
    from django.db.utils import OperationalError, ProgrammingError

    if not igreja:
        return None

    # Compatibilidade com bases antigas sem a tabela de fundos departamentais.
    try:
        if 'financeiro_fundodepartamental' not in connection.introspection.table_names():
            return None
    except Exception:
        return None

    codigo = FundoDepartamental.CODIGO_EVENTOS if getattr(evento, 'pk', None) else FundoDepartamental.CODIGO_LOCAL
    nomes = {
        FundoDepartamental.CODIGO_LOCAL: 'Tesouraria Local',
        FundoDepartamental.CODIGO_EVENTOS: 'Eventos',
        FundoDepartamental.CODIGO_MISSOES: 'Missoes',
        FundoDepartamental.CODIGO_ASSISTENCIA: 'Assistencia Social',
    }

    try:
        fundo, _ = FundoDepartamental.objects.get_or_create(
            igreja=igreja,
            codigo=codigo,
            defaults={'nome_exibicao': nomes[codigo]},
        )
        return fundo
    except (ProgrammingError, OperationalError):
        return None


def _categorias_receita_permitidas_por_fundo(codigo_fundo):
    return categorias_receita_permitidas_por_fundo(codigo_fundo)


class CategoriaDespesa(models.Model):
    """
    Modelo para representar uma categoria de Despesa.
    DECISÃO: Tornar por Ministério.
    """
    # --- ADICIONAR FK para Ministerio ---
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE, # Se deletar a Org, deleta as categorias dela
        related_name='categorias_despesa',
        verbose_name="Ministério"
        # null=False, blank=False por padrão
    )
    # --- FIM ADIÇÃO ---
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria") # Remover unique=True global
    padrao_global = models.BooleanField(default=False, verbose_name="Padrão Global?")

    def __str__(self):
        return self.nome

    class Meta:
        # Remover db_table para deixar o Django gerenciar
        # db_table = 'categoria_despesa'
        verbose_name = "Categoria de Despesa"
        verbose_name_plural = "Categorias de Despesas"
        # Garantir que o nome seja único DENTRO de cado ministério
        unique_together = ('ministerio', 'nome')


class FundoDepartamental(models.Model):
    """Representa o destino/finalidade ministerial da movimentacao financeira."""
    CODIGO_LOCAL = 'LOCAL'
    CODIGO_EVENTOS = 'EVENTOS'
    CODIGO_MISSOES = 'MISSOES'
    CODIGO_ASSISTENCIA = 'ASSISTENCIA'

    CODIGO_CHOICES = [
        (CODIGO_LOCAL, 'Tesouraria Local'),
        (CODIGO_EVENTOS, 'Eventos'),
        (CODIGO_MISSOES, 'Missoes'),
        (CODIGO_ASSISTENCIA, 'Assistencia Social'),
    ]

    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.CASCADE,
        related_name='fundos_departamentais',
        verbose_name='Igreja',
    )
    codigo = models.CharField(max_length=20, choices=CODIGO_CHOICES, verbose_name='Codigo do Fundo')
    nome_exibicao = models.CharField(max_length=100, verbose_name='Nome de Exibicao')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Fundo Departamental'
        verbose_name_plural = 'Fundos Departamentais'
        unique_together = ('igreja', 'codigo')
        ordering = ['igreja__nome_igreja', 'nome_exibicao']

    def __str__(self):
        return f"{self.nome_exibicao} ({self.igreja.nome_igreja})"


def _normalizar_codigo_departamento(valor):
    return (valor or '').strip().upper().replace(' ', '_')


class DepartamentoFinanceiro(models.Model):
    """Departamento financeiro por igreja para organizar operacao e governanca."""

    TIPO_PADRAO = 'PADRAO'
    TIPO_PERSONALIZADO = 'PERSONALIZADO'

    TIPO_CHOICES = [
        (TIPO_PADRAO, 'Padrao do Sistema'),
        (TIPO_PERSONALIZADO, 'Personalizado'),
    ]

    CODIGO_LOCAL = 'LOCAL'
    CODIGO_EVENTOS = 'EVENTOS'
    CODIGO_MISSOES = 'MISSOES'
    CODIGO_ASSISTENCIA = 'ASSISTENCIA'

    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.CASCADE,
        related_name='departamentos_financeiros',
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
    departamento = models.OneToOneField(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='configuracao_financeira',
        verbose_name='Departamento Organizacional',
    )
    fundo_departamental = models.OneToOneField(
        'FundoDepartamental',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departamento_financeiro',
        verbose_name='Fundo Departamental Legado',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Departamento Financeiro'
        verbose_name_plural = 'Departamentos Financeiros'
        unique_together = ('igreja', 'codigo_interno')
        ordering = ['igreja__nome_igreja', 'ordem_exibicao', 'nome_exibicao']

    def __str__(self):
        return f"{self.nome_exibicao} ({self.igreja.nome_igreja})"

    def clean(self):
        super().clean()
        self.codigo_interno = _normalizar_codigo_departamento(self.codigo_interno)
        if self.departamento_id and self.departamento.igreja_id != self.igreja_id:
            raise ValidationError({'departamento': 'O departamento organizacional deve pertencer a mesma igreja.'})
        if self.fundo_departamental_id and self.fundo_departamental.igreja_id != self.igreja_id:
            raise ValidationError({'fundo_departamental': 'O fundo legado deve pertencer a mesma igreja do departamento.'})

    def save(self, *args, **kwargs):
        self.codigo_interno = _normalizar_codigo_departamento(self.codigo_interno)
        super().save(*args, **kwargs)


class PoliticaDepartamentoFinanceiro(models.Model):
    """Politicas operacionais e contabeis configuraveis por departamento."""

    departamento = models.OneToOneField(
        'DepartamentoFinanceiro',
        on_delete=models.CASCADE,
        related_name='politica',
        verbose_name='Departamento',
    )
    exige_nota_fiscal = models.BooleanField(default=False, verbose_name='Exige Nota Fiscal')
    exige_envio_contabilidade = models.BooleanField(default=False, verbose_name='Exige Envio para Contabilidade')
    permite_prestacao_local_simplificada = models.BooleanField(
        default=True,
        verbose_name='Permite Prestacao Local Simplificada',
    )
    exige_aprovacao_para_saida = models.BooleanField(default=False, verbose_name='Exige Aprovacao para Saida')
    valor_minimo_para_anexo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Valor Minimo para Anexo',
    )
    valor_minimo_para_aprovacao = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Valor Minimo para Aprovacao',
    )

    class Meta:
        verbose_name = 'Politica de Departamento Financeiro'
        verbose_name_plural = 'Politicas de Departamentos Financeiros'

    def __str__(self):
        return f"Politica - {self.departamento.nome_exibicao}"


class PoliticaFinanceiraIgreja(models.Model):
    """Politica local de autorizacao pre-pagamento por Igreja."""

    LEVEL_1_SIMPLE = 'LEVEL_1_SIMPLE'
    LEVEL_2_CONTROLLED = 'LEVEL_2_CONTROLLED'
    LEVEL_3_STRONG = 'LEVEL_3_STRONG'
    SEGREGATION_LEVEL_CHOICES = [
        (LEVEL_1_SIMPLE, 'Nivel 1 - Simples'),
        (LEVEL_2_CONTROLLED, 'Nivel 2 - Controlado'),
        (LEVEL_3_STRONG, 'Nivel 3 - Forte'),
    ]

    igreja = models.OneToOneField(
        Igreja,
        on_delete=models.CASCADE,
        related_name='politica_financeira',
        verbose_name='Igreja',
    )
    approval_required = models.BooleanField(default=False, verbose_name='Exige Aprovacao Pre-Pagamento')
    segregation_level = models.CharField(
        max_length=20,
        choices=SEGREGATION_LEVEL_CHOICES,
        default=LEVEL_1_SIMPLE,
        verbose_name='Nivel de Segregacao',
    )
    version = models.PositiveIntegerField(default=1, verbose_name='Versao da Politica')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Politica Financeira da Igreja'
        verbose_name_plural = 'Politicas Financeiras das Igrejas'

    def __str__(self):
        return f"Politica Financeira - {self.igreja.nome_igreja} (v{self.version})"

    def clean(self):
        super().clean()
        if not self.approval_required and self.segregation_level != self.LEVEL_1_SIMPLE:
            raise ValidationError({
                'segregation_level': 'Politica sem aprovacao obrigatoria deve usar LEVEL_1_SIMPLE.',
            })
        if self.approval_required and self.segregation_level == self.LEVEL_1_SIMPLE:
            raise ValidationError({
                'segregation_level': 'Politica com aprovacao obrigatoria deve usar LEVEL_2_CONTROLLED ou LEVEL_3_STRONG.',
            })


class DepartamentoCaixa(models.Model):
    """Vinculo entre departamento financeiro e caixas permitidos para movimentacao."""

    departamento = models.ForeignKey(
        'DepartamentoFinanceiro',
        on_delete=models.CASCADE,
        related_name='caixas_vinculados',
        verbose_name='Departamento',
    )
    conta_bancaria = models.ForeignKey(
        'ContaBancaria',
        on_delete=models.CASCADE,
        related_name='departamentos_vinculados',
        verbose_name='Conta/Caixa',
    )
    is_padrao = models.BooleanField(default=False, verbose_name='Caixa Padrao do Departamento')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Vinculo Departamento x Caixa'
        verbose_name_plural = 'Vinculos Departamento x Caixa'
        unique_together = ('departamento', 'conta_bancaria')

    def __str__(self):
        return f"{self.departamento.nome_exibicao} -> {self.conta_bancaria.nome_identificacao}"

    def clean(self):
        super().clean()
        if self.departamento_id and self.conta_bancaria_id:
            if self.departamento.igreja_id != self.conta_bancaria.igreja_id:
                raise ValidationError({'conta_bancaria': 'A conta/caixa deve pertencer a mesma igreja do departamento.'})
        if self.is_padrao and self.departamento_id:
            qs = DepartamentoCaixa.objects.filter(departamento=self.departamento, is_padrao=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({'is_padrao': 'Ja existe um caixa padrao para este departamento.'})


class Despesas(models.Model):
    """
    Modelo para representar uma despesa.
    PRECISA de link para Igreja.
    """
    # --- ADICIONAR FK para Igreja ---
    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT, # Proteger para não deletar igreja com despesas
        related_name='despesas',
        verbose_name="Igreja"
    )
    evento = models.ForeignKey(
        'eventos.Evento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despesas_evento',
        verbose_name='Evento (Opcional)',
        help_text='Vincule a despesa a um evento/festividade para composicao do resultado financeiro do evento.',
    )
    # --- FIM ADIÇÃO ---
    data = models.DateField(verbose_name="Data")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    # Categoria agora é filtrada por ministério na view/form
    categoria = models.ForeignKey(CategoriaDespesa, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    fechado = models.BooleanField(default=False, verbose_name="Fechado")
    APROVACAO_PENDENTE = 'PENDENTE'
    APROVACAO_APROVADA = 'APROVADA'
    APROVACAO_REJEITADA = 'REJEITADA'
    APROVACAO_STATUS_CHOICES = [
        (APROVACAO_PENDENTE, 'Pendente'),
        (APROVACAO_APROVADA, 'Aprovada'),
        (APROVACAO_REJEITADA, 'Rejeitada'),
    ]
    aprovacao_status = models.CharField(
        max_length=20,
        choices=APROVACAO_STATUS_CHOICES,
        default=APROVACAO_APROVADA,
        verbose_name='Status de Aprovacao',
    )
    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despesas_aprovadas',
        verbose_name='Aprovado por',
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despesas_criadas',
        verbose_name='Criado por',
    )
    aprovado_em = models.DateTimeField(null=True, blank=True, verbose_name='Aprovado em')
    observacao_aprovacao = models.TextField(blank=True, null=True, verbose_name='Observacao da Aprovacao')
    conta_bancaria = models.ForeignKey(
        'ContaBancaria',
        on_delete=models.SET_NULL, # Se a conta for excluída, a despesa não é, mas perde o vínculo
        null=True, blank=True, # Permitir despesas sem conta vinculada
        related_name='despesas_associadas', # Nome do related_name alterado para evitar conflito
        verbose_name="Conta/Caixa de Origem"
    )
    fundo_departamental = models.ForeignKey(
        'FundoDepartamental',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despesas',
        verbose_name='Fundo Departamental',
    )

     # --- NOVOS CAMPOS PARA INTEGRAÇÃO COM CONTAS A PAGAR ---
    origem_conta_pagar = models.ForeignKey(
        'ContaPagar',
        on_delete=models.SET_NULL, # Se a conta a pagar for excluída, a despesa permanece mas perde o vínculo direto
        null=True, blank=True,
        related_name='despesa_gerada',
        verbose_name="Origem (Conta a Pagar)",
        help_text="Conta a Pagar que originou esta despesa, se aplicável."
    )
    usuario_registro_pagamento = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True, # Quem registrou o pagamento que gerou esta despesa
        related_name='despesas_registradas_via_pagamento',
        verbose_name="Pagamento Registrado por"
    )
    # --- FIM NOVOS CAMPOS ---

    def __str__(self):
        return self.descricao

    def clean(self):
        super().clean()
        if self.evento and self.igreja_id and self.evento.igreja_id != self.igreja_id:
            raise ValidationError({'evento': 'O evento selecionado deve pertencer a mesma igreja da despesa.'})
        if self.conta_bancaria and self.igreja_id and self.conta_bancaria.igreja_id != self.igreja_id:
            raise ValidationError({'conta_bancaria': 'A conta/caixa deve pertencer a mesma igreja da despesa.'})
        if self.fundo_departamental and self.igreja_id and self.fundo_departamental.igreja_id != self.igreja_id:
            raise ValidationError({'fundo_departamental': 'O fundo departamental deve pertencer a mesma igreja da despesa.'})
        if self.evento and self.fundo_departamental and self.fundo_departamental.codigo != FundoDepartamental.CODIGO_EVENTOS:
            raise ValidationError({'fundo_departamental': 'Lancamentos vinculados a evento devem usar o fundo Eventos.'})
        conta_evento_efetiva_id = None
        if self.evento:
            conta_evento_efetiva_id = self.evento.conta_bancaria_evento_id or getattr(self.evento.igreja, 'conta_padrao_eventos_id', None)
        if conta_evento_efetiva_id:
            if not self.conta_bancaria_id:
                raise ValidationError({'conta_bancaria': 'Este evento possui caixa definido. Informe o caixa/conta do evento para lançar a despesa.'})
            if self.conta_bancaria_id != conta_evento_efetiva_id:
                raise ValidationError({'conta_bancaria': 'Esta despesa deve usar o caixa vinculado ao evento.'})

    class Meta:
        # Remover db_table
        # db_table = 'despesas'
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"
        ordering = ['-data'] # Ordenar por data descendente
        constraints = [
            models.UniqueConstraint(
                fields=['origem_conta_pagar'],
                name='financeiro_unique_despesa_origem_conta_pagar',
            ),
        ]

    _original_valor = None
    _original_conta_bancaria_id = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk: # Se o objeto já existe (não é novo)
            self._original_valor = self.valor
            self._original_conta_bancaria_id = self.conta_bancaria_id

    def save(self, *args, **kwargs):
        from django.db import transaction # Import local para melhor ministério
        logger.info(f"Despesa SAVE - Despesa ID: {self.pk}, Valor: {self.valor}, ContaBancaria ID: {self.conta_bancaria_id}")

        if self.igreja_id:
            if self.evento_id:
                self.fundo_departamental = _obter_ou_criar_fundo_departamental(self.igreja, self.evento)
            elif not self.fundo_departamental_id:
                self.fundo_departamental = _obter_ou_criar_fundo_departamental(self.igreja, None)

        # 1. Lidar com a conta bancária ANTIGA (se estiver editando e a conta mudou ou foi removida)
        if not self._state.adding and self._original_conta_bancaria_id:
            if self._original_conta_bancaria_id != self.conta_bancaria_id or not self.conta_bancaria_id:
                # Reverte o valor original na conta antiga
                if self._original_valor is not None:
                    try:
                        with transaction.atomic():
                            conta_antiga = ContaBancaria.objects.select_for_update().get(pk=self._original_conta_bancaria_id)
                            conta_antiga.saldo_atual += self._original_valor # Adiciona de volta (despesa)
                            conta_antiga.save(update_fields=['saldo_atual'])
                    except ContaBancaria.DoesNotExist:
                        pass # Conta antiga pode ter sido deletada, não há o que reverter

        super().save(*args, **kwargs) # 2. Salva o objeto Despesa (ou Receita)

        # 3. Lidar com a conta bancária NOVA (se nova despesa/receita, ou conta mudou, ou valor mudou na mesma conta)
        if self.conta_bancaria_id:
            if self._state.adding or \
               self._original_conta_bancaria_id != self.conta_bancaria_id or \
               (self._original_conta_bancaria_id == self.conta_bancaria_id and self._original_valor != self.valor):
                
                with transaction.atomic():
                    # Usar select_for_update para bloquear a linha da conta durante a atualização
                    conta_nova = ContaBancaria.objects.select_for_update().get(pk=self.conta_bancaria_id)
                    logger.info(f"Despesa SAVE - ContaBancaria ID: {conta_nova.pk} - Saldo Atual ANTES da despesa: {conta_nova.saldo_atual}")

                    if self._state.adding or self._original_conta_bancaria_id != self.conta_bancaria_id:
                        # Nova despesa ou a conta bancária mudou: aplica o valor total da despesa
                        if self.valor is not None:
                            conta_nova.saldo_atual -= self.valor # Subtrai (despesa)
                    elif self._original_valor != self.valor: # Mesma conta, mas o valor mudou
                        # Calcula a diferença para aplicar ao saldo
                        # Se o novo valor da despesa é menor, a diferença é positiva (aumenta o saldo)
                        # Se o novo valor da despesa é maior, a diferença é negativa (diminui o saldo)
                        diferenca = (self._original_valor or Decimal(0)) - (self.valor or Decimal(0))
                        conta_nova.saldo_atual += diferenca
                    logger.info(f"Despesa SAVE - ContaBancaria ID: {conta_nova.pk} - Saldo Atual DEPOIS da despesa: {conta_nova.saldo_atual}")

                    conta_nova.save(update_fields=['saldo_atual'])

             
        # Atualiza os valores originais para o próximo save
        self._original_valor = self.valor
        self._original_conta_bancaria_id = self.conta_bancaria_id
    def delete(self, using=None, keep_parents=False):
        from django.db import router, transaction

        if not self._is_pk_set():
            return super().delete(using=using, keep_parents=keep_parents)

        using = using or router.db_for_write(self.__class__, instance=self)

        with transaction.atomic(using=using):
            locked = (
                type(self)._base_manager.using(using)
                .select_for_update()
                .filter(pk=self.pk)
                .first()
            )

            if locked is None:
                setattr(self, self._meta.pk.attname, None)
                return 0, {}

            if locked.conta_bancaria_id and locked.valor is not None:
                conta_afetada = (
                    ContaBancaria.objects.using(using)
                    .select_for_update()
                    .get(pk=locked.conta_bancaria_id)
                )
                conta_afetada.saldo_atual += locked.valor
                conta_afetada.save(using=using, update_fields=['saldo_atual'])

            result = super(Despesas, locked).delete(
                using=using,
                keep_parents=keep_parents,
            )
            setattr(self, self._meta.pk.attname, getattr(locked, locked._meta.pk.attname))
            return result


class Receitas(models.Model):
    """
    Modelo para representar uma receita.
    PRECISA de link para Igreja (mais robusto que via Membro).
    """
    CATEGORIA_CHOICES = [
        ('dizimo', 'Dízimo'),
        ('oferta', 'Oferta'),
        ('doacao', 'Doacao'),
        ('voto', 'Voto'),
        ('campanha', 'Campanha'),
        # Adicionar outras se necessário
        ('outro', 'Outro'),
    ]
    # --- ADICIONAR FK para Igreja ---
    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT,
        related_name='receitas',
        verbose_name="Igreja"
    )
    evento = models.ForeignKey(
        'eventos.Evento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receitas_evento',
        verbose_name='Evento (Opcional)',
        help_text='Vincule a receita a um evento/festividade para composicao do resultado financeiro do evento.',
    )
    # --- FIM ADIÇÃO ---
    categoria = models.CharField( # Mover categoria para cima para agrupar com outros campos de dados
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='oferta', # Talvez 'oferta' seja um default melhor?
        verbose_name="Categoria"
    )
     # Reutilizar ou adaptar as opções de forma de pagamento de ContaPagar
    FORMA_PAGAMENTO_CHOICES = (
        ('BOL', 'Boleto'), # Menos comum para receita, mas possível
        ('TRA', 'Transferência (TED/DOC)'),
        ('PIX', 'PIX'),
        ('DIN', 'Dinheiro'),
        ('DEB', 'Cartão de Débito'),
        ('CRE', 'Cartão de Crédito'),
        ('OUT', 'Outro'),
    )
    # Membro pode ser opcional
    membro = models.ForeignKey(Membro, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Membro (Opcional)')
    data = models.DateField(verbose_name="Data")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    fechado = models.BooleanField(default=False, verbose_name="Fechado")
    conta_bancaria = models.ForeignKey(
        'ContaBancaria',
        on_delete=models.SET_NULL, # Se a conta for excluída, a receita não é, mas perde o vínculo
        null=True, blank=True, # Permitir receitas sem conta vinculada (ex: caixa geral não rastreado)
        related_name='receitas_associadas', # Nome do related_name alterado para evitar conflito
        verbose_name="Conta/Caixa de Destino"
    )
    fundo_departamental = models.ForeignKey(
        'FundoDepartamental',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receitas',
        verbose_name='Fundo Departamental',
    )
    forma_pgto = models.CharField(
        max_length=50, # CORRIGIDO: Aumentar para acomodar valores antigos como "Dinheiro"
        choices=FORMA_PAGAMENTO_CHOICES, # Adicionar as opções
        blank=True, null=True, # Manter como opcional
        verbose_name="Forma de Pagamento"
    )
    class Meta:
        # Remover db_table
        # db_table = 'receitas'
        verbose_name = "Receita"
        verbose_name_plural = "Receitas"
        ordering = ['-data'] # Ordenar por data descendente

    def clean(self):
        super().clean()
        if self.evento and self.igreja_id and self.evento.igreja_id != self.igreja_id:
            raise ValidationError({'evento': 'O evento selecionado deve pertencer a mesma igreja da receita.'})
        if self.conta_bancaria and self.igreja_id and self.conta_bancaria.igreja_id != self.igreja_id:
            raise ValidationError({'conta_bancaria': 'A conta/caixa deve pertencer a mesma igreja da receita.'})
        if self.fundo_departamental and self.igreja_id and self.fundo_departamental.igreja_id != self.igreja_id:
            raise ValidationError({'fundo_departamental': 'O fundo departamental deve pertencer a mesma igreja da receita.'})
        if self.evento and self.fundo_departamental and self.fundo_departamental.codigo != FundoDepartamental.CODIGO_EVENTOS:
            raise ValidationError({'fundo_departamental': 'Lancamentos vinculados a evento devem usar o fundo Eventos.'})
        if self.fundo_departamental and self.categoria:
            permitidas = _categorias_receita_permitidas_por_fundo(self.fundo_departamental.codigo)
            if self.categoria not in permitidas:
                raise ValidationError({'categoria': 'Categoria nao permitida para o fundo departamental selecionado.'})
        conta_evento_efetiva_id = None
        if self.evento:
            conta_evento_efetiva_id = self.evento.conta_bancaria_evento_id or getattr(self.evento.igreja, 'conta_padrao_eventos_id', None)
        if conta_evento_efetiva_id:
            if not self.conta_bancaria_id:
                raise ValidationError({'conta_bancaria': 'Este evento possui caixa definido. Informe o caixa/conta do evento para lançar a receita.'})
            if self.conta_bancaria_id != conta_evento_efetiva_id:
                raise ValidationError({'conta_bancaria': 'Esta receita deve usar o caixa vinculado ao evento.'})

    
    _original_valor_receita = None
    _original_conta_bancaria_id_receita = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk:
            self._original_valor_receita = self.valor
            self._original_conta_bancaria_id_receita = self.conta_bancaria_id

    def save(self, *args, **kwargs):
       
        from django.db import transaction # Import local

        if self.igreja_id:
            if self.evento_id:
                self.fundo_departamental = _obter_ou_criar_fundo_departamental(self.igreja, self.evento)
            elif not self.fundo_departamental_id:
                self.fundo_departamental = _obter_ou_criar_fundo_departamental(self.igreja, None)

        # 1. Lidar com a conta bancária ANTIGA (se estiver editando e a conta mudou ou foi removida)
        if not self._state.adding and self._original_conta_bancaria_id_receita:
            if self._original_conta_bancaria_id_receita != self.conta_bancaria_id or not self.conta_bancaria_id:
                # Reverte o valor original na conta antiga
                if self._original_valor_receita is not None:
                    try:
                        with transaction.atomic():
                            conta_antiga = ContaBancaria.objects.select_for_update().get(pk=self._original_conta_bancaria_id_receita)
                            conta_antiga.saldo_atual -= self._original_valor_receita # Subtrai da antiga (receita)
                            conta_antiga.save(update_fields=['saldo_atual'])
                    except ContaBancaria.DoesNotExist:
                        pass 

        super().save(*args, **kwargs) # 2. Salva o objeto Receita

        # 3. Lidar com a conta bancária NOVA
        if self.conta_bancaria_id:
            if self._state.adding or \
               self._original_conta_bancaria_id_receita != self.conta_bancaria_id or \
               (self._original_conta_bancaria_id_receita == self.conta_bancaria_id and self._original_valor_receita != self.valor):
                
                with transaction.atomic():
                    conta_nova = ContaBancaria.objects.select_for_update().get(pk=self.conta_bancaria_id)
                    
                    if self._state.adding or self._original_conta_bancaria_id_receita != self.conta_bancaria_id:
                        # Nova receita ou a conta bancária mudou: aplica o valor total da receita
                        if self.valor is not None:
                            conta_nova.saldo_atual += self.valor # Adiciona (receita)
                    elif self._original_valor_receita != self.valor: # Mesma conta, mas o valor mudou
                        # Calcula a diferença para aplicar ao saldo
                        # Se o novo valor da receita é maior, a diferença é positiva (aumenta o saldo)
                        diferenca = (self.valor or Decimal(0)) - (self._original_valor_receita or Decimal(0))
                        conta_nova.saldo_atual += diferenca
                    
                    conta_nova.save(update_fields=['saldo_atual'])
        
      
        self._original_valor_receita = self.valor
        self._original_conta_bancaria_id_receita = self.conta_bancaria_id
    
    def delete(self, *args, **kwargs):
        from django.db import transaction # Import local para melhor ministério
        # Se a receita tinha uma conta e valor, reverte o saldo ao excluir
        if self.conta_bancaria and self.valor is not None:
            with transaction.atomic():
                conta_afetada = ContaBancaria.objects.select_for_update().get(pk=self.conta_bancaria_id)
                conta_afetada.saldo_atual -= self.valor # Subtrai o valor da receita
                conta_afetada.save(update_fields=['saldo_atual'])
        super().delete(*args, **kwargs) # Deleta a receita após a lógica de saldo


# --- NOVO MODELO: ContaBancaria (Exemplo) ---
# Se você não tiver, adicione algo assim
class ContaBancaria(models.Model):
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.is_principal:
            qs = ContaBancaria.objects.filter(igreja=self.igreja, is_principal=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("Já existe um caixa principal para esta igreja.")
    TIPO_CONTA_CHOICES = [
        ('bancaria', 'Conta Bancária'),
        ('caixa_fisico', 'Caixa Físico/Carteira'),
    ]
    """ Modelo para contas bancárias associadas a uma igreja """
    igreja = models.ForeignKey(Igreja, on_delete=models.CASCADE, related_name='contas_bancarias', verbose_name="Igreja")
    nome_identificacao = models.CharField(max_length=100, verbose_name="Nome de Identificação (Ex: Caixa Sede, Bradesco Ag.123)")
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CONTA_CHOICES,
        default='bancaria',
        verbose_name="Tipo de Conta/Caixa"
    )
    instituicao_bancaria = models.CharField(max_length=100, verbose_name="Instituição Bancária", blank=True, null=True, help_text="Preencher se for Conta Bancária")
    agencia = models.CharField(max_length=20, verbose_name="Agência", blank=True, null=True, help_text="Preencher se for Conta Bancária")
    conta = models.CharField(max_length=30, verbose_name="Número da Conta", blank=True, null=True, help_text="Preencher se for Conta Bancária")
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Saldo Inicial")
    saldo_atual = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Saldo Atual",
        help_text="Este saldo é atualizado automaticamente pelas transações.",
        editable=False # Geralmente não é editável diretamente pelo usuário no form
    )
    padrao_global = models.BooleanField(default=False, verbose_name="Padrão Global?")
    is_principal = models.BooleanField(
        default=False,
        verbose_name="Caixa Principal?",
        help_text="Marque se este é o caixa principal da igreja. Só deve haver um por igreja."
    )

    def __str__(self):
        return f"{self.nome_identificacao} ({self.igreja.nome_igreja})"
    
    def save(self, *args, **kwargs):
        logger.info(f"ContaBancaria SAVE - PK: {self.pk}, Saldo Inicial: {self.saldo_inicial}, Saldo Atual ANTES: {self.saldo_atual}")

        # Se for uma nova conta (não tem pk ainda), inicializa o saldo atual com o saldo inicial
        if not self.pk:
            self.saldo_atual = self.saldo_inicial
            logger.info(f"ContaBancaria SAVE (NOVA) - Saldo Atual DEPOIS de atribuir inicial: {self.saldo_atual}")
        super().save(*args, **kwargs)
        # Para verificar o que foi salvo no banco, você precisaria recarregar o objeto:
        # if not self.pk: # Isso não vai funcionar bem aqui pois o pk já foi setado
        #    reloaded_self = ContaBancaria.objects.get(pk=self.pk)
        #    logger.info(f"ContaBancaria SAVE (NOVA) - Saldo Atual NO BANCO (após reload): {reloaded_self.saldo_atual}")
        logger.info(f"ContaBancaria SAVE - Saldo Atual FINAL (em memória): {self.saldo_atual}")


    class Meta:
        verbose_name = "Conta Bancária/Caixa"
        verbose_name_plural = "Contas Bancárias/Caixas"
        # Garante que o nome de identificação seja único para cada igreja
        unique_together = ('igreja', 'nome_identificacao')




    # --- FIM NOVO MODELO ---


class FechamentoCaixa(models.Model):
    """
    Modelo para representar um Fechamento de Caixa.
    PRECISA de link para Igreja ou Ministério. Link para Igreja é mais granular.
    """
    STATUS_CHOICES = [
        ('aberto', 'Aberto'), # Status inicial ao criar/reabrir
        ('fechado', 'Fechado'), # Status após fechar com sucesso
        # 'reaberto' pode não ser necessário como status, a ação de editar pode reabrir
    ]
    # --- ADICIONAR FK para Igreja ---
    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT, # Proteger para não deletar igreja com fechamentos
        related_name='fechamentos_caixa',
        verbose_name="Igreja"
    )
    fundo_departamental = models.ForeignKey(
        'FundoDepartamental',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fechamentos_caixa',
        verbose_name='Fundo Departamental (Opcional)',
    )
    # --- FIM ADIÇÃO ---
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Fim")
    data_fechamento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Registro") # Data que o registro foi criado/atualizado
    total_entradas = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total de Entradas (Calculado)")
    total_saidas = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total de Saídas (Calculado)")
    saldo_final = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Saldo Final (Calculado)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='fechado', verbose_name="Status") # Default 'fechado' ao salvar
    # ajuste = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ajuste") # Campo ajuste parece desnecessário se o saldo é calculado
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações") # Campo para observações gerais

    # Remover campos redundantes que podem ser obtidos da Igreja associada
    # sub_sede = models.CharField(max_length=255, blank=True, null=True)
    # congregacao = models.CharField(max_length=255, blank=True, null=True)
    # rua = models.CharField(max_length=255, blank=True, null=True, verbose_name="Rua")
    # bairro = models.CharField(max_length=255, blank=True, null=True, verbose_name="Bairro")

    def __str__(self):
        escopo = self.fundo_departamental.nome_exibicao if self.fundo_departamental_id else 'Geral'
        return f"Fechamento {self.igreja.nome_igreja} ({escopo}): {self.data_inicio} a {self.data_fim}"

    def clean(self):
        super().clean()
        if self.fundo_departamental_id and self.igreja_id and self.fundo_departamental.igreja_id != self.igreja_id:
            raise ValidationError({'fundo_departamental': 'O fundo departamental deve pertencer a mesma igreja do fechamento.'})

    class Meta:
        # Remover db_table
        # db_table = 'fechamento_caixa'
        verbose_name = "Fechamento de Caixa"
        verbose_name_plural = "Fechamentos de Caixa"
        ordering = ['-data_fim', 'igreja'] # Ordenar por data e igreja
        # Garantir que não haja fechamentos sobrepostos para a mesma igreja
        unique_together = ('igreja', 'data_inicio', 'data_fim')


class LogTransacaoFinanceira(models.Model):
    TIPO_LANCAMENTO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
        ('transferencia', 'Transferencia'),
        ('fechamento', 'Fechamento'),
    ]

    ACAO_CHOICES = [
        ('criado', 'Criado'),
        ('atualizado', 'Atualizado'),
        ('excluido', 'Excluido'),
    ]

    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT,
        related_name='logs_transacoes_financeiras',
        verbose_name='Igreja',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_transacoes_financeiras',
        verbose_name='Usuario',
    )
    tipo_lancamento = models.CharField(max_length=20, choices=TIPO_LANCAMENTO_CHOICES, verbose_name='Tipo')
    acao = models.CharField(max_length=20, choices=ACAO_CHOICES, verbose_name='Acao')
    referencia_modelo = models.CharField(max_length=80, verbose_name='Referencia do Modelo')
    referencia_id = models.PositiveBigIntegerField(verbose_name='ID da Referencia')
    valor = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Valor')
    detalhes = models.TextField(blank=True, null=True, verbose_name='Detalhes')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Log de Transacao Financeira'
        verbose_name_plural = 'Logs de Transacoes Financeiras'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['igreja', 'criado_em']),
            models.Index(fields=['tipo_lancamento', 'criado_em']),
            models.Index(fields=['referencia_modelo', 'referencia_id']),
        ]

    def __str__(self):
        return f"{self.get_tipo_lancamento_display()} {self.get_acao_display()} ({self.referencia_modelo} #{self.referencia_id})"


class ImportacaoExtratoOFX(models.Model):
    conta_bancaria = models.ForeignKey(
        'ContaBancaria',
        on_delete=models.CASCADE,
        related_name='importacoes_ofx',
        verbose_name='Conta Bancaria',
    )
    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT,
        related_name='importacoes_ofx',
        verbose_name='Igreja',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='importacoes_ofx',
        verbose_name='Usuario',
    )
    arquivo_nome = models.CharField(max_length=255, blank=True, verbose_name='Nome do Arquivo')
    hash_arquivo = models.CharField(max_length=64, verbose_name='Hash do Arquivo')
    banco_id = models.CharField(max_length=30, blank=True, verbose_name='Banco ID')
    conta_id = models.CharField(max_length=60, blank=True, verbose_name='Conta ID')
    tipo_conta = models.CharField(max_length=30, blank=True, verbose_name='Tipo de Conta')
    data_inicio = models.DateTimeField(null=True, blank=True, verbose_name='Data Inicial do Extrato')
    data_fim = models.DateTimeField(null=True, blank=True, verbose_name='Data Final do Extrato')
    saldo_final = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Saldo Final')
    importado_em = models.DateTimeField(auto_now_add=True, verbose_name='Importado em')

    class Meta:
        verbose_name = 'Importacao de Extrato OFX'
        verbose_name_plural = 'Importacoes de Extratos OFX'
        ordering = ['-importado_em']
        unique_together = ('conta_bancaria', 'hash_arquivo')

    def __str__(self):
        return f"Extrato OFX {self.conta_bancaria.nome_identificacao} ({self.importado_em:%d/%m/%Y %H:%M})"


class LancamentoExtratoOFX(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saida'),
    ]
    CONCILIADO_TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    ]

    importacao = models.ForeignKey(
        ImportacaoExtratoOFX,
        on_delete=models.CASCADE,
        related_name='lancamentos',
        verbose_name='Importacao',
    )
    data = models.DateTimeField(verbose_name='Data do Lancamento')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name='Tipo')
    trn_type = models.CharField(max_length=20, blank=True, verbose_name='Tipo OFX')
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor')
    fit_id = models.CharField(max_length=80, blank=True, verbose_name='FITID')
    memo = models.TextField(blank=True, verbose_name='Memo')
    documento = models.CharField(max_length=80, blank=True, verbose_name='Documento')
    conciliado = models.BooleanField(default=False, verbose_name='Conciliado')
    conciliado_tipo = models.CharField(
        max_length=20,
        choices=CONCILIADO_TIPO_CHOICES,
        blank=True,
        verbose_name='Conciliado com Tipo',
    )
    conciliado_referencia_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name='ID de Referencia Conciliada',
    )
    conciliado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conciliacoes_ofx_realizadas',
        verbose_name='Conciliado por',
    )
    conciliado_em = models.DateTimeField(null=True, blank=True, verbose_name='Conciliado em')

    class Meta:
        verbose_name = 'Lancamento de Extrato OFX'
        verbose_name_plural = 'Lancamentos de Extrato OFX'
        ordering = ['data', 'id']

    def __str__(self):
        return f"{self.get_tipo_display()} {self.valor} em {self.data:%d/%m/%Y}"



# ====================================================
# ========= INÍCIO: NOVOS MODELOS PARA CONTAS A PAGAR =========
# ====================================================

class Fornecedor(models.Model):
    """ Modelo para Fornecedores/Credores """
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        related_name='fornecedores_financeiro', # Usar related_name específico
        verbose_name="Ministério"
    )
    nome = models.CharField(max_length=150, verbose_name="Nome/Razão Social")
    cnpj_cpf = models.CharField(max_length=18, blank=True, null=True, verbose_name="CNPJ/CPF")
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    ativo = models.BooleanField(default=True, verbose_name="Ativo?")
    padrao_global = models.BooleanField(default=False, verbose_name="Padrão Global?")

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome']
        # Garante nome único por ministério
        unique_together = ('ministerio', 'nome')

    padrao_global = models.BooleanField(default=False, verbose_name="Padrão Global?")
    def __str__(self):
        return self.nome


class RecorrenciaContaPagar(models.Model):
    """Template de despesa fixa para geracao automatica de contas a pagar."""
    FREQUENCIA_CHOICES = (
        ('MEN', 'Mensal'),
    )
    FORMA_PAGAMENTO_CHOICES = (
        ('BOL', 'Boleto'),
        ('TRA', 'Transferência (TED/DOC)'),
        ('PIX', 'PIX'),
        ('DIN', 'Dinheiro'),
        ('DEB', 'Cartão de Débito'),
        ('CRE', 'Cartão de Crédito'),
        ('OUT', 'Outro'),
    )

    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.PROTECT,
        related_name='recorrencias_contas_pagar',
        verbose_name='Ministério',
    )
    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT,
        related_name='recorrencias_contas_pagar',
        verbose_name='Igreja',
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT,
        related_name='recorrencias_contas_pagar',
        verbose_name='Fornecedor',
    )
    categoria = models.ForeignKey(
        CategoriaDespesa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorrencias_contas_pagar',
        verbose_name='Categoria',
    )
    descricao = models.CharField(max_length=255, verbose_name='Descrição')
    valor = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor')
    dia_vencimento = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name='Dia do Vencimento',
    )
    frequencia = models.CharField(max_length=3, choices=FREQUENCIA_CHOICES, default='MEN', verbose_name='Frequência')
    data_inicio = models.DateField(default=timezone.localdate, verbose_name='Data de Início')
    data_fim = models.DateField(null=True, blank=True, verbose_name='Data de Fim')
    conta_debito_padrao = models.ForeignKey(
        ContaBancaria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorrencias_contas_pagar',
        verbose_name='Conta/Caixa de Débito Padrão',
    )
    forma_pagamento_padrao = models.CharField(
        max_length=3,
        choices=FORMA_PAGAMENTO_CHOICES,
        null=True,
        blank=True,
        verbose_name='Forma de Pagamento Padrão',
    )
    gerar_automaticamente = models.BooleanField(default=True, verbose_name='Gerar Automaticamente?')
    ultima_competencia_gerada = models.CharField(max_length=7, null=True, blank=True, verbose_name='Última Competência Gerada')
    ativo = models.BooleanField(default=True, verbose_name='Ativa?')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    usuario_criacao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorrencias_contas_pagar_criadas',
        verbose_name='Criado por',
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Recorrência de Conta a Pagar'
        verbose_name_plural = 'Recorrências de Contas a Pagar'
        ordering = ['igreja__nome_igreja', 'descricao']

    def __str__(self):
        return f"{self.descricao} ({self.igreja.nome_igreja})"


class ContaPagar(models.Model):
    """ Modelo para Contas a Pagar (Obrigações/Parcelas) """
    STATUS_CHOICES = (
        ('PEN', 'Pendente'),
        ('PAG', 'Paga'),
        ('VEN', 'Vencida'),
        ('CAN', 'Cancelada'),
        # ('PAR', 'Parcialmente Paga') - Não usaremos com 1 registro por parcela
    )
    FORMA_PAGAMENTO_CHOICES = (
        ('BOL', 'Boleto'),
        ('TRA', 'Transferência (TED/DOC)'),
        ('PIX', 'PIX'),
        ('DIN', 'Dinheiro'),
        ('DEB', 'Cartão de Débito'),
        ('CRE', 'Cartão de Crédito'),
        ('OUT', 'Outro'),
    )
    AUTHORIZATION_NOT_REQUIRED = 'NOT_REQUIRED'
    AUTHORIZATION_PENDING = 'PENDING'
    AUTHORIZATION_APPROVED = 'APPROVED'
    AUTHORIZATION_REJECTED = 'REJECTED'
    AUTHORIZATION_STATUS_CHOICES = (
        (AUTHORIZATION_NOT_REQUIRED, 'Nao Requerida'),
        (AUTHORIZATION_PENDING, 'Pendente'),
        (AUTHORIZATION_APPROVED, 'Aprovada'),
        (AUTHORIZATION_REJECTED, 'Rejeitada'),
    )
    AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED = 'POLICY_NOT_REQUIRED'
    AUTHORIZATION_ORIGIN_POLICY_REQUIRED = 'POLICY_REQUIRED'
    AUTHORIZATION_ORIGIN_USER_APPROVAL = 'USER_APPROVAL'
    AUTHORIZATION_ORIGIN_LEGACY_MIGRATION = 'LEGACY_MIGRATION'
    AUTHORIZATION_ORIGIN_CHOICES = (
        (AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED, 'Politica sem Aprovacao'),
        (AUTHORIZATION_ORIGIN_POLICY_REQUIRED, 'Politica com Aprovacao'),
        (AUTHORIZATION_ORIGIN_USER_APPROVAL, 'Aprovacao de Usuario'),
        (AUTHORIZATION_ORIGIN_LEGACY_MIGRATION, 'Migracao de Legado'),
    )

    # Ligações principais
    ministerio = models.ForeignKey(Ministerio, on_delete=models.PROTECT, related_name='contas_a_pagar_financeiro') # related_name específico
    igreja = models.ForeignKey(Igreja, on_delete=models.PROTECT, related_name='contas_a_pagar_financeiro', verbose_name="Igreja Responsável")
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name='contas_a_pagar', verbose_name="Fornecedor")
    categoria = models.ForeignKey(CategoriaDespesa, on_delete=models.SET_NULL, null=True, blank=True, related_name='contas_a_pagar', verbose_name="Categoria")

    # Detalhes da Obrigação/Parcela
    descricao = models.CharField(max_length=255, verbose_name="Descrição (Conta/Parcela)")
    numero_documento = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nº Documento/NF/Parcela")
    valor = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor da Conta/Parcela") # Renomeado de valor_total para valor
    data_emissao = models.DateField(default=timezone.now, verbose_name="Data de Emissão")
    data_vencimento = models.DateField(db_index=True, verbose_name="Data de Vencimento")

    # Detalhes do Pagamento (preenchidos ao pagar ESTA conta/parcela)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='PEN', db_index=True, verbose_name="Status")
    data_pagamento = models.DateField(null=True, blank=True, verbose_name="Data do Pagamento")
    valor_pago = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor Efetivamente Pago") # Pode ser diferente do valor previsto
    juros_multa = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Juros/Multa Pagos")
    desconto = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Desconto Obtido")
    conta_debito = models.ForeignKey(ContaBancaria, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagamentos_contas_pagar', verbose_name="Conta/Caixa de Saída")
    forma_pagamento = models.CharField(max_length=3, choices=FORMA_PAGAMENTO_CHOICES, null=True, blank=True, verbose_name="Forma de Pagamento")
    comprovante = models.FileField(upload_to='comprovantes_contapagar/%Y/%m/', blank=True, null=True, verbose_name="Anexar Comprovante")
    recorrencia_origem = models.ForeignKey(
        'RecorrenciaContaPagar',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contas_geradas',
        verbose_name='Recorrência de Origem',
    )
    competencia = models.CharField(max_length=7, null=True, blank=True, db_index=True, verbose_name='Competência (AAAA-MM)')
    criado_automaticamente = models.BooleanField(default=False, verbose_name='Criado Automaticamente?')

    # Campos expansivos: nullable ate que todos os produtores usem o servico
    # de dominio de autorizacao pre-pagamento no patch 3B.2B2.
    authorization_status = models.CharField(max_length=12, choices=AUTHORIZATION_STATUS_CHOICES, null=True, blank=True, verbose_name='Status de Autorizacao')
    authorization_origin = models.CharField(max_length=24, choices=AUTHORIZATION_ORIGIN_CHOICES, null=True, blank=True, verbose_name='Origem da Autorizacao')
    authorization_policy_version = models.PositiveIntegerField(null=True, blank=True, verbose_name='Versao da Politica de Autorizacao')
    current_material_fingerprint = models.CharField(max_length=74, null=True, blank=True, verbose_name='Fingerprint Material Atual')
    approved_material_fingerprint = models.CharField(max_length=74, null=True, blank=True, verbose_name='Fingerprint Material Aprovado')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='contas_pagar_autorizadas', verbose_name='Aprovado por')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Aprovado em')
    rejected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='contas_pagar_rejeitadas', verbose_name='Rejeitado por')
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name='Rejeitado em')
    current_rejection_reason = models.TextField(null=True, blank=True, verbose_name='Motivo Atual da Rejeicao')

    # Opcional: Campo para agrupar parcelas da mesma compra
    # compra_uuid = models.UUIDField(null=True, blank=True, editable=False, help_text="Identificador único para agrupar parcelas da mesma compra")

    # Metadados
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    usuario_criacao = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='contas_pagar_criadas', verbose_name="Criado por")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conta a Pagar"
        verbose_name_plural = "Contas a Pagar"
        ordering = ['data_vencimento', 'status'] # Ordenar por vencimento
        permissions = [
            ('approve_contapagar', 'Pode aprovar ou rejeitar contas a pagar'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['recorrencia_origem', 'competencia'],
                condition=models.Q(recorrencia_origem__isnull=False),
                name='uniq_conta_recorrencia_competencia',
            ),
        ]

    def __str__(self):
        return f"{self.descricao} - {self.fornecedor.nome} (Venc: {self.data_vencimento.strftime('%d/%m/%Y')})"

    @property
    def is_vencida(self):
        # Verifica se está vencida e ainda pendente
        return self.data_vencimento < timezone.now().date() and self.status == 'PEN'


class ContaPagarAutorizacaoEvento(models.Model):
    """Evidencia append-only das decisoes de autorizacao de ContaPagar."""

    EVENT_CREATED = 'CREATED'
    EVENT_EDITED = 'EDITED'
    EVENT_APPROVAL_REQUESTED = 'APPROVAL_REQUESTED'
    EVENT_APPROVED = 'APPROVED'
    EVENT_REJECTED = 'REJECTED'
    EVENT_APPROVAL_INVALIDATED = 'APPROVAL_INVALIDATED'
    EVENT_CANCELLED = 'CANCELLED'
    EVENT_PAID = 'PAID'
    EVENT_LEGACY_MIGRATED = 'LEGACY_MIGRATED'
    EVENT_TYPE_CHOICES = (
        (EVENT_CREATED, 'Criado'),
        (EVENT_EDITED, 'Editado'),
        (EVENT_APPROVAL_REQUESTED, 'Aprovacao Solicitada'),
        (EVENT_APPROVED, 'Aprovado'),
        (EVENT_REJECTED, 'Rejeitado'),
        (EVENT_APPROVAL_INVALIDATED, 'Aprovacao Invalidada'),
        (EVENT_CANCELLED, 'Cancelado'),
        (EVENT_PAID, 'Pago'),
        (EVENT_LEGACY_MIGRATED, 'Legado Migrado'),
    )

    conta_pagar = models.ForeignKey(ContaPagar, on_delete=models.PROTECT, related_name='eventos_autorizacao', verbose_name='Conta a Pagar')
    event_type = models.CharField(max_length=24, choices=EVENT_TYPE_CHOICES, verbose_name='Tipo de Evento')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos_autorizacao_conta_pagar', verbose_name='Ator')
    actor_user_id_snapshot = models.PositiveBigIntegerField(null=True, blank=True, verbose_name='ID Historico do Ator')
    actor_display_name_snapshot = models.CharField(max_length=150, null=True, blank=True, verbose_name='Nome Historico do Ator')
    occurred_at = models.DateTimeField(auto_now_add=True, verbose_name='Ocorrido em')
    authorization_status_before = models.CharField(max_length=12, choices=ContaPagar.AUTHORIZATION_STATUS_CHOICES, null=True, blank=True, verbose_name='Status de Autorizacao Anterior')
    authorization_status_after = models.CharField(max_length=12, choices=ContaPagar.AUTHORIZATION_STATUS_CHOICES, verbose_name='Status de Autorizacao Posterior')
    financial_status_before = models.CharField(max_length=3, choices=ContaPagar.STATUS_CHOICES, null=True, blank=True, verbose_name='Status Financeiro Anterior')
    financial_status_after = models.CharField(max_length=3, choices=ContaPagar.STATUS_CHOICES, verbose_name='Status Financeiro Posterior')
    material_fingerprint = models.CharField(max_length=74, null=True, blank=True, verbose_name='Fingerprint Material')
    material_snapshot = models.JSONField(null=True, blank=True, verbose_name='Snapshot Material')
    policy_snapshot = models.JSONField(null=True, blank=True, verbose_name='Snapshot da Politica')
    reason = models.TextField(null=True, blank=True, verbose_name='Motivo')
    correlation_id = models.UUIDField(null=True, blank=True, verbose_name='ID de Correlacao')

    class Meta:
        verbose_name = 'Evento de Autorizacao de Conta a Pagar'
        verbose_name_plural = 'Eventos de Autorizacao de Contas a Pagar'
        ordering = ['-occurred_at', '-id']

    def __str__(self):
        return f"{self.get_event_type_display()} - Conta #{self.conta_pagar_id}"

# ==================================================
# ========= FIM: NOVOS MODELOS PARA CONTAS A PAGAR =========
# ==================================================
