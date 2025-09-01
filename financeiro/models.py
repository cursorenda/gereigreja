# financeiro/models.py
from django.db import models
from django.utils import timezone
# Importa Membro, que já tem relação com Igreja -> Ministerio
from secretaria.models import Membro
from decimal import Decimal
# PRECISAMOS importar Igreja e Ministerio para adicionar as FKs
from configuracao.models import Igreja, Ministerio # <<< ADICIONAR IMPORT
from django.conf import settings
import logging # Adicione no topo do arquivo se já não estiver
logger = logging.getLogger(__name__) # Adicione no topo do arquivo


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

    def __str__(self):
        return self.nome

    class Meta:
        # Remover db_table para deixar o Django gerenciar
        # db_table = 'categoria_despesa'
        verbose_name = "Categoria de Despesa"
        verbose_name_plural = "Categorias de Despesas"
        # Garantir que o nome seja único DENTRO de cada ministério
        unique_together = ('ministerio', 'nome')


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
    # --- FIM ADIÇÃO ---
    data = models.DateField(verbose_name="Data")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    # Categoria agora é filtrada por ministério na view/form
    categoria = models.ForeignKey(CategoriaDespesa, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    fechado = models.BooleanField(default=False, verbose_name="Fechado")
    conta_bancaria = models.ForeignKey(
        'ContaBancaria',
        on_delete=models.SET_NULL, # Se a conta for excluída, a despesa não é, mas perde o vínculo
        null=True, blank=True, # Permitir despesas sem conta vinculada
        related_name='despesas_associadas', # Nome do related_name alterado para evitar conflito
        verbose_name="Conta/Caixa de Origem"
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

    class Meta:
        # Remover db_table
        # db_table = 'despesas'
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"
        ordering = ['-data'] # Ordenar por data descendente

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
     
    def delete(self, *args, **kwargs):
        from django.db import transaction # Import local
        # Se a despesa tinha uma conta e valor, reverte o saldo ao excluir
        if self.conta_bancaria and self.valor is not None:
            with transaction.atomic():
                conta_afetada = ContaBancaria.objects.select_for_update().get(pk=self.conta_bancaria_id)
                conta_afetada.saldo_atual += self.valor # Adiciona o valor de volta
                conta_afetada.save(update_fields=['saldo_atual'])
        super().delete(*args, **kwargs) # Deleta a despesa


class Receitas(models.Model):
    """
    Modelo para representar uma receita.
    PRECISA de link para Igreja (mais robusto que via Membro).
    """
    CATEGORIA_CHOICES = [
        ('dizimo', 'Dízimo'),
        ('oferta', 'Oferta'),
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

    
    _original_valor_receita = None
    _original_conta_bancaria_id_receita = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk:
            self._original_valor_receita = self.valor
            self._original_conta_bancaria_id_receita = self.conta_bancaria_id

    def save(self, *args, **kwargs):
       
        from django.db import transaction # Import local

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
        return f"Fechamento {self.igreja.nome_igreja}: {self.data_inicio} a {self.data_fim}"

    class Meta:
        # Remover db_table
        # db_table = 'fechamento_caixa'
        verbose_name = "Fechamento de Caixa"
        verbose_name_plural = "Fechamentos de Caixa"
        ordering = ['-data_fim', 'igreja'] # Ordenar por data e igreja
        # Garantir que não haja fechamentos sobrepostos para a mesma igreja
        unique_together = ('igreja', 'data_inicio', 'data_fim')



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

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome']
        # Garante nome único por ministério
        unique_together = ('ministerio', 'nome')

    def __str__(self):
        return self.nome


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

    def __str__(self):
        return f"{self.descricao} - {self.fornecedor.nome} (Venc: {self.data_vencimento.strftime('%d/%m/%Y')})"

    @property
    def is_vencida(self):
        # Verifica se está vencida e ainda pendente
        return self.data_vencimento < timezone.now().date() and self.status == 'PEN'

# ==================================================
# ========= FIM: NOVOS MODELOS PARA CONTAS A PAGAR =========
# ==================================================
