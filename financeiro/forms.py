# c:\Gereigreja\financeiro\forms.py
from django import forms
from .models import (
    Receitas, Despesas, CategoriaDespesa, FechamentoCaixa, ContaBancaria,
    Fornecedor, ContaPagar, RecorrenciaContaPagar
)
from .models import TransferenciaCaixa
from configuracao.models import Igreja, Ministerio
from secretaria.models import Membro
from decimal import Decimal
from django.utils import timezone
# --- IMPORTAR UTILS DE PERMISSÃO ---
from .utils import is_admin_org
import logging

# Define o logger no nível do módulo para ser usado por todos os formulários
logger = logging.getLogger(__name__)

# Widget de data para consistência
class DateInput(forms.DateInput):
    """Widget para usar input type="date" do HTML5."""
    input_type = 'date'


class CategoriaDespesaForm(forms.ModelForm):
    """ Formulário para Categoria de Despesa (ligada à Ministério) """
    class Meta:
        model = CategoriaDespesa
        exclude = ['ministerio']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TransferenciaCaixaForm(forms.ModelForm):
    """Formulário para transferências entre caixas da MESMA Igreja"""

    class Meta:
        model = TransferenciaCaixa
        fields = ['caixa_origem', 'caixa_destino', 'valor', 'observacao']
        widgets = {
            'caixa_origem': forms.Select(attrs={'class': 'form-select'}),
            'caixa_destino': forms.Select(attrs={'class': 'form-select'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        # Compatibilidade com chamadas antigas
        kwargs.pop('ministerio', None)
        kwargs.pop('user', None)
        kwargs.pop('allowed_churches', None)
        super().__init__(*args, **kwargs)

        igreja_ativa = None
        if request and getattr(request, 'igreja_ativa', None):
            igreja_ativa = request.igreja_ativa
        elif request:
            igreja_ativa_id = request.session.get('igreja_ativa_id')
            if igreja_ativa_id:
                igreja_ativa = Igreja.objects.filter(pk=igreja_ativa_id).first()
        
        # Configurar labels
        self.fields['caixa_origem'].label = "Caixa de Origem"
        self.fields['caixa_destino'].label = "Caixa de Destino"
        self.fields['caixa_origem'].empty_label = "Selecione a caixa de origem"
        self.fields['caixa_destino'].empty_label = "Selecione a caixa de destino"
        self.fields['valor'].label = "Valor a Transferir"
        self.fields['observacao'].label = "Observação (Opcional)"
        self.fields['observacao'].required = False

        if igreja_ativa:
            caixas_queryset = ContaBancaria.objects.filter(igreja=igreja_ativa).order_by('nome_identificacao')
        elif self.instance and self.instance.pk and self.instance.caixa_origem:
            caixas_queryset = ContaBancaria.objects.filter(igreja=self.instance.caixa_origem.igreja).order_by('nome_identificacao')
        else:
            caixas_queryset = ContaBancaria.objects.none()

        self.fields['caixa_origem'].queryset = caixas_queryset
        self.fields['caixa_destino'].queryset = caixas_queryset
    
    def clean(self):
        cleaned_data = super().clean()
        caixa_origem = cleaned_data.get('caixa_origem')
        caixa_destino = cleaned_data.get('caixa_destino')

        # Validar que origem e destino pertencem à mesma Igreja
        if caixa_origem and caixa_destino:
            if caixa_origem.igreja != caixa_destino.igreja:
                raise forms.ValidationError('As caixas de origem e destino devem pertencer à mesma Igreja.')

        return cleaned_data

class ContaBancariaForm(forms.ModelForm):
    """ Formulário para Conta Bancária (ligada à Igreja) """
    class Meta:
        model = ContaBancaria
        fields = [
            'igreja', 'nome_identificacao', 'tipo',
            'instituicao_bancaria', 'agencia', 'conta', 'saldo_inicial', 'is_principal'
        ]
        widgets = {
            'igreja': forms.Select(attrs={'class': 'form-select'}),
            'nome_identificacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Caixa da Sede, Bradesco Ag. 123'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'instituicao_bancaria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Banco (se aplicável)'}),
            'agencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'conta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'saldo_inicial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        user = kwargs.pop('user', None)
        allowed_churches = kwargs.pop('allowed_churches', Igreja.objects.none())
        igreja_selecionada_inicial = kwargs.pop('igreja_selecionada_inicial', None)
        super().__init__(*args, **kwargs)

        if not self.is_bound and not (self.instance and self.instance.pk) and not self.initial.get('data'):
            self.initial['data'] = timezone.localdate()

        if user and not is_admin_org(user) and allowed_churches is not None:
            if not hasattr(allowed_churches, 'all'):
                self.fields['igreja'].queryset = Igreja.objects.filter(pk__in=[i.pk for i in allowed_churches])
            else:
                self.fields['igreja'].queryset = allowed_churches
        elif ministerio:
            self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio)
        else:
            self.fields['igreja'].queryset = Igreja.objects.none()
        self.fields['igreja'].empty_label = "Selecione a Igreja"

        if igreja_selecionada_inicial and self.fields['igreja'].queryset.filter(pk=igreja_selecionada_inicial.pk).exists():
            self.initial['igreja'] = igreja_selecionada_inicial
            self.fields['igreja'].disabled = True
            self.fields['igreja'].required = False

        self.fields['instituicao_bancaria'].required = False
        self.fields['agencia'].required = False
        self.fields['conta'].required = False


class ReceitaForm(forms.ModelForm):
    """ Formulário para Receitas (ligada à Igreja) """
    FORMAS_PAGAMENTO_DIZIMO_OFERTA = {'DIN', 'PIX', 'CRE'}

    class Meta:
        model = Receitas
        fields = ['igreja', 'membro', 'data', 'categoria', 'valor', 'forma_pgto', 'conta_bancaria', 'observacao']
        widgets = {
            'igreja': forms.Select(attrs={'class': 'form-select'}),
            'membro': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'forma_pgto': forms.Select(attrs={'class': 'form-select'}),
            'conta_bancaria': forms.Select(attrs={'class': 'form-select'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        user = kwargs.pop('user', None)
        allowed_churches = kwargs.pop('allowed_churches', Igreja.objects.none())
        igreja_selecionada_inicial = kwargs.pop('igreja_selecionada_inicial', None)
        super().__init__(*args, **kwargs)

        if user and not is_admin_org(user) and allowed_churches is not None:
            if not hasattr(allowed_churches, 'all'):
                self.fields['igreja'].queryset = Igreja.objects.filter(pk__in=[i.pk for i in allowed_churches])
            else:
                self.fields['igreja'].queryset = allowed_churches
        elif ministerio:
            self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio)
        else:
            self.fields['igreja'].queryset = Igreja.objects.none()

        self.fields['igreja'].empty_label = "Selecione a Igreja"
        # Somente UI: usar 'Pessoa' no rótulo visível e no texto do empty_label
        self.fields['membro'].label = "Pessoa (Opcional)"
        self.fields['membro'].empty_label = "Selecione a Pessoa (Opcional)"
        self.fields['membro'].required = False
        self.fields['conta_bancaria'].empty_label = "Selecione a Conta/Caixa de Destino (Opcional)"
        self.fields['conta_bancaria'].required = False

        if igreja_selecionada_inicial and self.fields['igreja'].queryset.filter(pk=igreja_selecionada_inicial.pk).exists():
            self.initial['igreja'] = igreja_selecionada_inicial
            self.fields['igreja'].disabled = True

        igreja_para_filtrar_campos_dependentes = None
        if self.instance and self.instance.pk and self.instance.igreja:
            igreja_para_filtrar_campos_dependentes = self.instance.igreja
        elif self.is_bound and 'igreja' in self.data and self.data['igreja']:
            try:
                igreja_id_post = int(self.data['igreja'])
                igreja_para_filtrar_campos_dependentes = Igreja.objects.get(pk=igreja_id_post)
            except (ValueError, TypeError, Igreja.DoesNotExist):
                pass
        elif igreja_selecionada_inicial:
            igreja_para_filtrar_campos_dependentes = igreja_selecionada_inicial
        
        if igreja_para_filtrar_campos_dependentes:
            self.fields['membro'].queryset = Membro.objects.filter(igreja=igreja_para_filtrar_campos_dependentes).order_by('nome')
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.filter(igreja=igreja_para_filtrar_campos_dependentes).order_by('nome_identificacao')
            if not self.is_bound and not self.initial.get('conta_bancaria'):
                conta_padrao_receitas = getattr(igreja_para_filtrar_campos_dependentes, 'conta_padrao_receitas', None)
                if conta_padrao_receitas and self.fields['conta_bancaria'].queryset.filter(pk=conta_padrao_receitas.pk).exists():
                    self.initial['conta_bancaria'] = conta_padrao_receitas
                else:
                    caixa_principal = self.fields['conta_bancaria'].queryset.filter(is_principal=True).first()
                    if caixa_principal:
                        self.initial['conta_bancaria'] = caixa_principal
        elif ministerio:
            self.fields['membro'].queryset = Membro.objects.filter(igreja__ministerio=ministerio).order_by('igreja__nome_igreja', 'nome')
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.filter(igreja__ministerio=ministerio).order_by('igreja__nome_igreja', 'nome_identificacao')
        else:
            self.fields['membro'].queryset = Membro.objects.none()
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        forma_pgto = cleaned_data.get('forma_pgto')

        if categoria in {'dizimo', 'oferta'} and forma_pgto and forma_pgto not in self.FORMAS_PAGAMENTO_DIZIMO_OFERTA:
            self.add_error('forma_pgto', 'Para Dízimo/Oferta, use Dinheiro, PIX ou Cartão de Crédito.')

        return cleaned_data


class DespesaForm(forms.ModelForm):
    """ Formulário para Despesas (ligada à Igreja) """
    class Meta:
        model = Despesas
        fields = ['igreja', 'categoria', 'data', 'valor', 'descricao', 'conta_bancaria', 'observacao']
        widgets = {
            'igreja': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'conta_bancaria': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        user = kwargs.pop('user', None)
        allowed_churches = kwargs.pop('allowed_churches', Igreja.objects.none())
        igreja_selecionada_inicial = kwargs.pop('igreja_selecionada_inicial', None)
        super().__init__(*args, **kwargs)

        if not self.is_bound and not (self.instance and self.instance.pk) and not self.initial.get('data'):
            self.initial['data'] = timezone.localdate()

        if user and not is_admin_org(user) and allowed_churches is not None:
            if not hasattr(allowed_churches, 'all'):
                self.fields['igreja'].queryset = Igreja.objects.filter(pk__in=[i.pk for i in allowed_churches])
            else:
                self.fields['igreja'].queryset = allowed_churches
        elif ministerio:
            self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio)
            self.fields['categoria'].queryset = CategoriaDespesa.objects.filter(ministerio=ministerio)
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.filter(igreja__ministerio=ministerio).order_by('igreja__nome_igreja', 'nome_identificacao')
        else:
            self.fields['igreja'].queryset = Igreja.objects.none()
            self.fields['categoria'].queryset = CategoriaDespesa.objects.none()
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.none()

        self.fields['igreja'].empty_label = "Selecione a Igreja"
        self.fields['categoria'].empty_label = "Selecione a Categoria"
        self.fields['categoria'].required = True
        self.fields['conta_bancaria'].empty_label = "Selecione a Conta/Caixa de Origem (Opcional)"
        self.fields['conta_bancaria'].required = False
        
        if igreja_selecionada_inicial and self.fields['igreja'].queryset.filter(pk=igreja_selecionada_inicial.pk).exists():
            self.initial['igreja'] = igreja_selecionada_inicial
            self.fields['igreja'].disabled = True

        igreja_para_filtrar_contas = None
        if self.instance and self.instance.pk and self.instance.igreja:
            igreja_para_filtrar_contas = self.instance.igreja
        elif self.is_bound and 'igreja' in self.data and self.data['igreja']:
            try:
                igreja_id_post = int(self.data['igreja'])
                igreja_para_filtrar_contas = Igreja.objects.get(pk=igreja_id_post)
            except (ValueError, TypeError, Igreja.DoesNotExist):
                pass
        elif igreja_selecionada_inicial:
            igreja_para_filtrar_contas = igreja_selecionada_inicial

        if igreja_para_filtrar_contas:
             self.fields['conta_bancaria'].queryset = ContaBancaria.objects.filter(igreja=igreja_para_filtrar_contas).order_by('nome_identificacao')
             if not self.is_bound and not self.initial.get('conta_bancaria'):
                conta_padrao_despesas = getattr(igreja_para_filtrar_contas, 'conta_padrao_despesas', None)
                if conta_padrao_despesas and self.fields['conta_bancaria'].queryset.filter(pk=conta_padrao_despesas.pk).exists():
                    self.initial['conta_bancaria'] = conta_padrao_despesas
                else:
                    caixa_principal = self.fields['conta_bancaria'].queryset.filter(is_principal=True).first()
                    if caixa_principal:
                        self.initial['conta_bancaria'] = caixa_principal


class FechamentoCaixaForm(forms.Form):
    """ Formulário para INICIAR o processo de fechamento de caixa (selecionar igreja e período) """
    igreja = forms.ModelChoiceField(
        queryset=Igreja.objects.none(),
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
        ministerio = kwargs.pop('ministerio', None)
        user = kwargs.pop('user', None)
        allowed_churches = kwargs.pop('allowed_churches', Igreja.objects.none())
        igreja_selecionada_inicial = kwargs.pop('igreja_selecionada_inicial', None)
        super().__init__(*args, **kwargs)

        if user and not is_admin_org(user) and allowed_churches is not None:
            self.fields['igreja'].queryset = allowed_churches
        elif ministerio:
            self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio)
        else:
            self.fields['igreja'].queryset = Igreja.objects.none()
        self.fields['igreja'].empty_label = "Selecione a Igreja"

        if igreja_selecionada_inicial and self.fields['igreja'].queryset.filter(pk=igreja_selecionada_inicial.pk).exists():
            self.initial['igreja'] = igreja_selecionada_inicial
            self.fields['igreja'].disabled = True
            self.fields['igreja'].required = False

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
        exclude = ['ministerio', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj_cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
        }


class RecorrenciaContaPagarForm(forms.ModelForm):
    """Formulário para criar/editar template de despesa fixa."""

    class Meta:
        model = RecorrenciaContaPagar
        fields = [
            'igreja',
            'fornecedor',
            'categoria',
            'descricao',
            'valor',
            'dia_vencimento',
            'frequencia',
            'data_inicio',
            'data_fim',
            'conta_debito_padrao',
            'forma_pagamento_padrao',
            'gerar_automaticamente',
            'ativo',
            'observacoes',
        ]
        widgets = {
            'igreja': forms.Select(attrs={'class': 'form-select'}),
            'fornecedor': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'dia_vencimento': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 31}),
            'frequencia': forms.Select(attrs={'class': 'form-select'}),
            'data_inicio': DateInput(attrs={'class': 'form-control'}),
            'data_fim': DateInput(attrs={'class': 'form-control'}),
            'conta_debito_padrao': forms.Select(attrs={'class': 'form-select'}),
            'forma_pagamento_padrao': forms.Select(attrs={'class': 'form-select'}),
            'gerar_automaticamente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        user = kwargs.pop('user', None)
        allowed_churches = kwargs.pop('allowed_churches', Igreja.objects.none())
        igreja_selecionada_inicial = kwargs.pop('igreja_selecionada_inicial', None)
        super().__init__(*args, **kwargs)

        if user and not is_admin_org(user) and allowed_churches is not None:
            self.fields['igreja'].queryset = allowed_churches
        elif ministerio:
            self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio)
        else:
            self.fields['igreja'].queryset = Igreja.objects.none()

        if ministerio:
            self.fields['fornecedor'].queryset = Fornecedor.objects.filter(ministerio=ministerio, ativo=True)
            self.fields['categoria'].queryset = CategoriaDespesa.objects.filter(ministerio=ministerio)
            self.fields['conta_debito_padrao'].queryset = ContaBancaria.objects.filter(
                igreja__ministerio=ministerio
            ).order_by('igreja__nome_igreja', 'nome_identificacao')
        else:
            self.fields['fornecedor'].queryset = Fornecedor.objects.none()
            self.fields['categoria'].queryset = CategoriaDespesa.objects.none()
            self.fields['conta_debito_padrao'].queryset = ContaBancaria.objects.none()

        if igreja_selecionada_inicial and self.fields['igreja'].queryset.filter(pk=igreja_selecionada_inicial.pk).exists():
            self.initial['igreja'] = igreja_selecionada_inicial
            self.fields['igreja'].disabled = True

        igreja_para_filtrar_conta = None
        if self.instance and self.instance.pk and self.instance.igreja:
            igreja_para_filtrar_conta = self.instance.igreja
        elif self.is_bound and self.data.get('igreja'):
            try:
                igreja_para_filtrar_conta = Igreja.objects.get(pk=int(self.data.get('igreja')))
            except (ValueError, TypeError, Igreja.DoesNotExist):
                igreja_para_filtrar_conta = None
        elif igreja_selecionada_inicial:
            igreja_para_filtrar_conta = igreja_selecionada_inicial

        if igreja_para_filtrar_conta:
            self.fields['conta_debito_padrao'].queryset = ContaBancaria.objects.filter(
                igreja=igreja_para_filtrar_conta
            ).order_by('nome_identificacao')
            if not self.is_bound and not self.initial.get('conta_debito_padrao'):
                conta_padrao = getattr(igreja_para_filtrar_conta, 'conta_padrao_despesas', None)
                if not conta_padrao:
                    conta_padrao = getattr(igreja_para_filtrar_conta, 'conta_padrao_receitas', None)

                if conta_padrao and self.fields['conta_debito_padrao'].queryset.filter(pk=conta_padrao.pk).exists():
                    self.initial['conta_debito_padrao'] = conta_padrao
                else:
                    caixa_principal = self.fields['conta_debito_padrao'].queryset.filter(is_principal=True).first()
                    if caixa_principal:
                        self.initial['conta_debito_padrao'] = caixa_principal

        self.fields['igreja'].empty_label = "Selecione a Igreja"
        self.fields['fornecedor'].empty_label = "Selecione o Fornecedor"
        self.fields['categoria'].empty_label = "Selecione a Categoria (Opcional)"
        self.fields['categoria'].required = False
        self.fields['conta_debito_padrao'].empty_label = "Selecione a Conta/Caixa (Opcional)"
        self.fields['conta_debito_padrao'].required = False
        self.fields['forma_pagamento_padrao'].required = False
        self.fields['data_fim'].required = False
        self.fields['observacoes'].required = False

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        igreja = cleaned_data.get('igreja')
        conta_debito_padrao = cleaned_data.get('conta_debito_padrao')

        if data_inicio and data_fim and data_fim < data_inicio:
            raise forms.ValidationError('A data final não pode ser anterior à data inicial.')

        if conta_debito_padrao and igreja and conta_debito_padrao.igreja_id != igreja.id:
            self.add_error('conta_debito_padrao', 'A conta/caixa de débito deve pertencer à mesma igreja da recorrência.')

        return cleaned_data

class ContaPagarForm(forms.ModelForm):
    """ Formulário para Criar/Editar a obrigação (Conta/Parcela) """
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.none(),
        label="Fornecedor",
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={'required': 'Por favor, selecione o fornecedor para esta conta.'}
    )
    class Meta:
        model = ContaPagar
        fields = [
            'igreja', 'fornecedor', 'categoria',
            'descricao', 'numero_documento', 'valor',
            'data_emissao', 'data_vencimento', 'observacoes',
        ]
        widgets = {
            'igreja': forms.Select(attrs={'class': 'form-select'}),
            'fornecedor': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_emissao': DateInput(attrs={'class': 'form-control'}),
            'data_vencimento': DateInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
        }

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        user = kwargs.pop('user', None)
        allowed_churches = kwargs.pop('allowed_churches', Igreja.objects.none())
        igreja_selecionada_inicial = kwargs.pop('igreja_selecionada_inicial', None)

        logger.info(f"[ContaPagarForm.__init__] Recebida ministerio: {ministerio}")

        super().__init__(*args, **kwargs)
        # --- Lógica para filtrar o campo 'igreja' ---

        if user and not is_admin_org(user) and allowed_churches is not None:
            # Este bloco filtra o campo 'igreja' pelas igrejas permitidas
            self.fields['igreja'].queryset = allowed_churches
        elif ministerio: # Este bloco agora APENAS filtra o campo 'igreja' se a condição do IF anterior for falsa
            self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio)
        else:
            logger.info("[ContaPagarForm.__init__] Nenhuma ministerio recebida. Querysets de igreja, fornecedor e categoria serão vazios.")
            self.fields['igreja'].queryset = Igreja.objects.none()
            # Estes querysets também devem ser vazios se não houver ministério
            self.fields['fornecedor'].queryset = Fornecedor.objects.none()
            self.fields['categoria'].queryset = CategoriaDespesa.objects.none()
        # --- Lógica para filtrar campos dependentes do ministério (fornecedor, categoria) ---
        # Esta lógica deve rodar sempre que a ministério estiver disponível,
        # independentemente de como o campo 'igreja' foi filtrado.
        if ministerio:

            
            logger.info(f"[ContaPagarForm.__init__] (Bloco IF ministerio) Verificando fornecedores para ministerio ID: {ministerio.pk if ministerio else 'N/A'}")

            fornecedores_da_org = Fornecedor.objects.filter(ministerio=ministerio)
            logger.info(f"[ContaPagarForm.__init__] (Bloco IF ministerio) Fornecedores APENAS pela ministerio ({fornecedores_da_org.count()}): {list(fornecedores_da_org.values_list('nome', 'ativo'))}")

            fornecedores_ativos_da_org = fornecedores_da_org.filter(ativo=True)
            logger.info(f"[ContaPagarForm.__init__] (Bloco IF ministerio) Fornecedores PELA ministerio E ativo=True ({fornecedores_ativos_da_org.count()}): {list(fornecedores_ativos_da_org.values_list('nome', flat=True))}")
            
            self.fields['fornecedor'].queryset = fornecedores_ativos_da_org
            self.fields['categoria'].queryset = CategoriaDespesa.objects.filter(ministerio=ministerio)
        # --- Fim Lógica para filtrar campos dependentes do ministério ---


        self.fields['igreja'].empty_label = "Selecione a Igreja"
        self.fields['fornecedor'].empty_label = "Selecione o Fornecedor"
        self.fields['categoria'].empty_label = "Selecione a Categoria (Opcional)"
        self.fields['categoria'].required = False

        if igreja_selecionada_inicial and self.fields['igreja'].queryset.filter(pk=igreja_selecionada_inicial.pk).exists():
            self.initial['igreja'] = igreja_selecionada_inicial
            self.fields['igreja'].disabled = True

class RegistrarPagamentoContaPagarForm(forms.ModelForm):
    """ Formulário para registrar os detalhes do pagamento de uma ContaPagar existente """
    class Meta:
        model = ContaPagar
        fields = [
            'data_pagamento', 'valor_pago', 'juros_multa', 'desconto',
            'conta_debito', 'forma_pagamento', 'comprovante',
        ]
        widgets = {
            'data_pagamento': DateInput(attrs={'class': 'form-control', 'required': True}),
            'valor_pago': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
            'juros_multa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desconto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'conta_debito': forms.Select(attrs={'class': 'form-select'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'comprovante': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        conta = kwargs.get('instance')
        self.instance = conta
        ministerio = kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)

        igreja_da_conta = self.instance.igreja if self.instance else None

        if conta:
            self.fields['valor_pago'].initial = conta.valor
            if igreja_da_conta:
                self.fields['conta_debito'].queryset = ContaBancaria.objects.filter(
                    igreja=igreja_da_conta
                ).order_by('nome_identificacao')
                if hasattr(igreja_da_conta, 'conta_padrao_despesas') and igreja_da_conta.conta_padrao_despesas:
                    self.initial['conta_debito'] = igreja_da_conta.conta_padrao_despesas
            elif ministerio:
                self.fields['conta_debito'].queryset = ContaBancaria.objects.filter(
                    igreja__ministerio=ministerio
                ).order_by('igreja__nome_igreja', 'nome_identificacao')
            else:
                self.fields['conta_debito'].queryset = ContaBancaria.objects.none()
        else:
            self.fields['conta_debito'].queryset = ContaBancaria.objects.none()

        self.fields['forma_pagamento'].empty_label = "Selecione a Forma"
        self.fields['forma_pagamento'].required = True

    def clean_valor_pago(self):
        valor_pago = self.cleaned_data.get('valor_pago')
        if valor_pago is not None and valor_pago <= 0:
            raise forms.ValidationError("O valor pago deve ser maior que zero.")
        return valor_pago

    def clean_data_pagamento(self):
        data_pagamento = self.cleaned_data.get('data_pagamento')
        if not data_pagamento:
             raise forms.ValidationError("A data do pagamento é obrigatória.")
        # Opcional: impedir data futura?
        # if data_pagamento > timezone.now().date():
        #    raise forms.ValidationError("A data do pagamento não pode ser futura.")
        return data_pagamento

    def save(self, commit=True):
        conta = super().save(commit=False)
        conta.status = 'PAG'
        if commit:
            conta.save()
        return conta

# ==================================================
# ========= FIM: NOVOS FORMULÁRIOS PARA CONTAS A PAGAR =========
# ==================================================
