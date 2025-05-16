# c:\Gereigreja\financeiro\forms.py
from django import forms
# Modelos existentes + novos
from .models import (
    Receitas, Despesas, CategoriaDespesa, FechamentoCaixa, ContaBancaria,
    Fornecedor, ContaPagar # Adicionar novos modelos importados
)
from configuracao.models import Igreja, Organizacao
from secretaria.models import Membro
from decimal import Decimal # Importar Decimal para validações
# --- IMPORTAR UTILS DE PERMISSÃO ---
from .utils import is_admin_org # Para verificar se o usuário é admin


# --- GARANTA QUE ESTA CLASSE ESTEJA AQUI E DESCOMENTADA ---
class DateInput(forms.DateInput):
    """Widget para usar input type="date" do HTML5."""
    input_type = 'date'
# --- FIM DA VERIFICAÇÃO ---

class CategoriaDespesaForm(forms.ModelForm):
    """ Formulário para Categoria de Despesa (ligada à Organização) """
    class Meta:
        model = CategoriaDespesa
        # Exclui 'organizacao' pois será definida na view
        exclude = ['organizacao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ContaBancariaForm(forms.ModelForm):
    """ Formulário para Conta Bancária (ligada à Igreja) """
    class Meta:
        model = ContaBancaria
        # Inclui 'igreja' para seleção
        fields = [
            'igreja', 'nome_identificacao', 'tipo',
            'instituicao_bancaria', 'agencia', 'conta', 'saldo_inicial'
        ]
        widgets = {
            'igreja': forms.Select(attrs={'class': 'form-select'}),
            'nome_identificacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Caixa da Sede, Bradesco Ag. 123'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'instituicao_bancaria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Banco (se aplicável)'}),
            'agencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'conta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'saldo_inicial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


    def __init__(self, *args, **kwargs):
        # Pega a organização passada pela view
        organizacao = kwargs.pop('organizacao', None)
        user = kwargs.pop('user', None) # Pega o usuário
        allowed_churches = kwargs.pop('allowed_churches', None) # Pega as igrejas permitidas
        super().__init__(*args, **kwargs)

        # Filtra o queryset de 'igreja'
        if user and not is_admin_org(user) and allowed_churches is not None:
            # Se não for admin, filtra pelas igrejas permitidas
            self.fields['igreja'].queryset = allowed_churches
        elif organizacao: # Se for admin ou não houver filtro específico, usa a organização
            self.fields['igreja'].queryset = Igreja.objects.filter(organizacao=organizacao)
        else:
            self.fields['igreja'].queryset = Igreja.objects.none()
        self.fields['igreja'].empty_label = "Selecione a Igreja"

        # Tornar campos opcionais no formulário, alinhando com o modelo (blank=True)
        self.fields['instituicao_bancaria'].required = False
        self.fields['agencia'].required = False
        self.fields['conta'].required = False


class ReceitaForm(forms.ModelForm):
    """ Formulário para Receitas (ligada à Igreja) """
    class Meta:
        model = Receitas
        fields = ['igreja', 'membro', 'data', 'categoria', 'valor', 'forma_pgto', 'conta_bancaria', 'observacao'] # conta_bancaria já estava, forma_pgto também
        widgets = {
            'igreja': forms.Select(attrs={'class': 'form-select'}),
            'membro': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}), # Usa choices do modelo
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'forma_pgto': forms.Select(attrs={'class': 'form-select'}), # Alterado para Select
            'conta_bancaria': forms.Select(attrs={'class': 'form-select'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        organizacao = kwargs.pop('organizacao', None)
        user = kwargs.pop('user', None) # Pega o usuário
        allowed_churches = kwargs.pop('allowed_churches', None) # Pega as igrejas permitidas
        super().__init__(*args, **kwargs)

        # Filtra igrejas
        if user and not is_admin_org(user) and allowed_churches is not None:
            # Se não for admin, filtra pelas igrejas permitidas
            self.fields['igreja'].queryset = allowed_churches
        elif organizacao: # Se for admin ou não houver filtro específico, usa a organização
            self.fields['igreja'].queryset = Igreja.objects.filter(organizacao=organizacao)
            # Filtra membros (apenas membros da organização) - MANTÉM FILTRO POR ORGANIZAÇÃO
            self.fields['membro'].queryset = Membro.objects.filter(igreja__organizacao=organizacao)
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.filter(igreja__organizacao=organizacao).order_by('igreja__nome_igreja', 'nome_identificacao')

        else:
            self.fields['igreja'].queryset = Igreja.objects.none()
            self.fields['membro'].queryset = Membro.objects.none()
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.none()

        # Definir empty_labels e required
        self.fields['igreja'].empty_label = "Selecione a Igreja"
        self.fields['membro'].empty_label = "Selecione o Membro (Opcional)"
        self.fields['membro'].required = False # Membro é opcional no modelo
        self.fields['conta_bancaria'].empty_label = "Selecione a Conta/Caixa de Destino (Opcional)"
        self.fields['conta_bancaria'].required = False



class DespesaForm(forms.ModelForm):
    """ Formulário para Despesas (ligada à Igreja) """
    class Meta:
        model = Despesas
        fields = ['igreja', 'categoria', 'data', 'valor', 'descricao', 'conta_bancaria', 'observacao'] # conta_bancaria já estava
        widgets = {
            'igreja': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}), # Usar TextInput para descrição curta
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'conta_bancaria': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        organizacao = kwargs.pop('organizacao', None)
        user = kwargs.pop('user', None) # Pega o usuário
        allowed_churches = kwargs.pop('allowed_churches', None) # Pega as igrejas permitidas
        super().__init__(*args, **kwargs)

        # Filtra igrejas
        if user and not is_admin_org(user) and allowed_churches is not None:
            # Se não for admin, filtra pelas igrejas permitidas
            self.fields['igreja'].queryset = allowed_churches
        elif organizacao: # Se for admin ou não houver filtro específico, usa a organização
            self.fields['igreja'].queryset = Igreja.objects.filter(organizacao=organizacao)
            # Filtra categorias de despesa (MANTÉM FILTRO POR ORGANIZAÇÃO)
            self.fields['categoria'].queryset = CategoriaDespesa.objects.filter(organizacao=organizacao)
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.filter(igreja__organizacao=organizacao).order_by('igreja__nome_igreja', 'nome_identificacao')
        else:
            self.fields['igreja'].queryset = Igreja.objects.none()
            self.fields['categoria'].queryset = CategoriaDespesa.objects.none()
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.none()

        # Definir empty_labels e required
        self.fields['igreja'].empty_label = "Selecione a Igreja"
        self.fields['categoria'].empty_label = "Selecione a Categoria"
        self.fields['categoria'].required = True # Categoria de despesa é obrigatória? Ajuste se não for.
        self.fields['conta_bancaria'].empty_label = "Selecione a Conta/Caixa de Origem (Opcional)"
        self.fields['conta_bancaria'].required = False


class FechamentoCaixaForm(forms.Form):
    """ Formulário para INICIAR o processo de fechamento de caixa (selecionar igreja e período) """
    igreja = forms.ModelChoiceField(
        queryset=Igreja.objects.none(), # Filtrado no __init__
        label="Igreja",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Selecione a Igreja"
    )
    data_inicio = forms.DateField(
        label="Data de Início",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_fim = forms.DateField(
        label="Data de Fim",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    observacoes = forms.CharField(
        label="Observações (Opcional)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def __init__(self, *args, **kwargs):
        organizacao = kwargs.pop('organizacao', None)
        user = kwargs.pop('user', None) # Pega o usuário
        allowed_churches = kwargs.pop('allowed_churches', None) # Pega as igrejas permitidas
        super().__init__(*args, **kwargs)

        # Filtra igrejas
        if user and not is_admin_org(user) and allowed_churches is not None:
            # Se não for admin, filtra pelas igrejas permitidas
            self.fields['igreja'].queryset = allowed_churches
        elif organizacao: # Se for admin ou não houver filtro específico, usa a organização
            self.fields['igreja'].queryset = Igreja.objects.filter(organizacao=organizacao)
        else:
            self.fields['igreja'].queryset = Igreja.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get("data_inicio")
        data_fim = cleaned_data.get("data_fim")

        if data_inicio and data_fim and data_fim < data_inicio:
            raise forms.ValidationError("A data final não pode ser anterior à data inicial.")

        return cleaned_data

# ====================================================
# ========= INÍCIO: NOVOS FORMULÁRIOS PARA CONTAS A PAGAR =========
# ====================================================

class FornecedorForm(forms.ModelForm):
    """ Formulário para Criar/Editar Fornecedores """
    class Meta:
        model = Fornecedor
        # Exclui 'organizacao' (definida na view) e 'ativo' (gerenciado separadamente, se necessário)
        exclude = ['organizacao', 'ativo']
        widgets = {
            # Adiciona classes Bootstrap para estilização
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj_cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}), # Adicionar máscara JS no template
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}), # Adicionar máscara JS no template
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
        }

class ContaPagarForm(forms.ModelForm):
    """ Formulário para Criar/Editar a obrigação (Conta/Parcela) """
    class Meta:
        model = ContaPagar
        # Campos relevantes para definir a obrigação
        fields = [
            'igreja', 'fornecedor', 'categoria',
            'descricao', 'numero_documento', 'valor', # Usar 'valor' (não 'valor_total')
            'data_emissao', 'data_vencimento', 'observacoes',
            # 'centro_custo', # Adicionar se for usar Centro de Custo
        ]
        widgets = {
            'igreja': forms.Select(attrs={'class': 'form-select'}),
            'fornecedor': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            # 'centro_custo': forms.Select(attrs={'class': 'form-select'}), # Se usar
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_emissao': DateInput(attrs={'class': 'form-control'}), # Usar widget DateInput
            'data_vencimento': DateInput(attrs={'class': 'form-control'}), # Usar widget DateInput
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
        }

    def __init__(self, *args, **kwargs):
        # Pega a organização passada pela view para filtrar os QuerySets
        organizacao = kwargs.pop('organizacao', None)
        user = kwargs.pop('user', None) # Pega o usuário
        allowed_churches = kwargs.pop('allowed_churches', None) # Pega as igrejas permitidas
        super().__init__(*args, **kwargs)

        # Filtra campos ForeignKey pela organização ou igrejas permitidas
        if user and not is_admin_org(user) and allowed_churches is not None:
            # Se não for admin, filtra igreja pelas permitidas
            self.fields['igreja'].queryset = allowed_churches
        elif organizacao: # Se for admin ou não houver filtro específico, usa a organização
            self.fields['igreja'].queryset = Igreja.objects.filter(organizacao=organizacao)
            # Filtros por organização para outros campos
            self.fields['fornecedor'].queryset = Fornecedor.objects.filter(organizacao=organizacao, ativo=True) # Só fornecedores ativos
            self.fields['categoria'].queryset = CategoriaDespesa.objects.filter(organizacao=organizacao)
            # if 'centro_custo' in self.fields: # Se usar
            #     self.fields['centro_custo'].queryset = CentroCusto.objects.filter(organizacao=organizacao)
            #     self.fields['centro_custo'].required = False
            #     self.fields['centro_custo'].empty_label = "Nenhum (Opcional)"
        else:
            # Querysets vazios se não houver organização (segurança)
            self.fields['igreja'].queryset = Igreja.objects.none()
            self.fields['fornecedor'].queryset = Fornecedor.objects.none()
            self.fields['categoria'].queryset = CategoriaDespesa.objects.none()
            # if 'centro_custo' in self.fields: self.fields['centro_custo'].queryset = CentroCusto.objects.none()

        # Definir labels vazios e se campos são obrigatórios
        self.fields['igreja'].empty_label = "Selecione a Igreja"
        self.fields['fornecedor'].empty_label = "Selecione o Fornecedor"
        self.fields['categoria'].empty_label = "Selecione a Categoria (Opcional)"
        self.fields['categoria'].required = False # Categoria é opcional? Ajuste se necessário.

class RegistrarPagamentoContaPagarForm(forms.ModelForm):
    """ Formulário para registrar os detalhes do pagamento de uma ContaPagar existente """
    class Meta:
        model = ContaPagar
        # Campos específicos do pagamento
        fields = [
            'data_pagamento', 'valor_pago', 'juros_multa', 'desconto',
            'conta_debito', 'forma_pagamento', 'comprovante',
            # 'observacoes' # Pode adicionar aqui se quiser observações SÓ do pagamento
        ]
        widgets = {
            'data_pagamento': DateInput(attrs={'class': 'form-control', 'required': True}), # Data é obrigatória
            'valor_pago': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}), # Valor pago é obrigatório
            'juros_multa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desconto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'conta_debito': forms.Select(attrs={'class': 'form-select'}), # Conta de saída
            'forma_pagamento': forms.Select(attrs={'class': 'form-select'}), # Forma de pagamento
            'comprovante': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # A instância da ContaPagar é passada pela view
        conta = kwargs.get('instance')
        # Pega a organização explicitamente da view (mais seguro que depender da instância)
        organizacao = kwargs.pop('organizacao', None)
        super().__init__(*args, **kwargs)

        if conta:
            # Sugerir valor pago igual ao valor da conta/parcela (usuário pode alterar)
            self.fields['valor_pago'].initial = conta.valor
            # Filtrar conta de débito pela organização
            if organizacao:
                 # Filtra contas pela organização da igreja associada à conta bancária
                 self.fields['conta_debito'].queryset = ContaBancaria.objects.filter(igreja__organizacao=organizacao)
                 self.fields['conta_debito'].empty_label = "Selecione a Conta/Caixa de Saída"
                 self.fields['conta_debito'].required = True # Pagamento exige conta de saída? Ajuste se não.
            else:
                 self.fields['conta_debito'].queryset = ContaBancaria.objects.none()
        else:
             # Segurança: se não houver instância ou organização, não mostrar contas
             self.fields['conta_debito'].queryset = ContaBancaria.objects.none()

        self.fields['forma_pagamento'].empty_label = "Selecione a Forma"
        self.fields['forma_pagamento'].required = True # Pagamento exige forma? Ajuste se não.

    def clean_valor_pago(self):
        # Validação básica do valor pago
        valor_pago = self.cleaned_data.get('valor_pago')
        if valor_pago is not None and valor_pago <= 0:
            raise forms.ValidationError("O valor pago deve ser maior que zero.")
        return valor_pago

    def clean_data_pagamento(self):
        # Validação básica da data
        data_pagamento = self.cleaned_data.get('data_pagamento')
        if not data_pagamento:
             raise forms.ValidationError("A data do pagamento é obrigatória.")
        # Opcional: impedir data futura?
        # if data_pagamento > timezone.now().date():
        #    raise forms.ValidationError("A data do pagamento não pode ser futura.")
        return data_pagamento

    def save(self, commit=True):
        # Sobrescreve o save para definir o status como 'Paga'
        conta = super().save(commit=False)
        # Como é um registro por parcela/conta, ao registrar pagamento, o status vira 'Paga'
        conta.status = 'PAG'
        if commit:
            conta.save()
        return conta

# ==================================================
# ========= FIM: NOVOS FORMULÁRIOS PARA CONTAS A PAGAR =========
# ==================================================
