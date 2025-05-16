# c:\Gereigreja\configuracao\forms.py
from django import forms
from .models import Igreja, Organizacao, PerfilUsuario, ESTADO_CHOICES  # Modelos necessários
from django.contrib.auth.models import User # Modelo de usuário padrão
from financeiro.models import ContaBancaria # Importar ContaBancaria
from django.db import transaction # Para garantir atomicidade no registro



# --- FORMULÁRIO IGREJA CORRIGIDO E COMPLETO ---
class IgrejaForm(forms.ModelForm):
    """ Formulário para Criar/Editar Igrejas """
    # Definir igreja_superior aqui para filtrar dinamicamente se necessário
    # (A lógica de filtragem no admin.py pode ser adaptada para o __init__ do form)
    igreja_superior = forms.ModelChoiceField(
        queryset=Igreja.objects.none(), # Será filtrado no __init__
        required=False,
        label="Igreja Superior (Sede/Regional)",
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Selecione a Sede ou Regional à qual esta igreja está vinculada (se aplicável)."
    )
    conta_padrao_receitas = forms.ModelChoiceField(
        queryset=ContaBancaria.objects.none(), # Será filtrado no __init__
        required=False,
        label="Conta/Caixa Padrão para Receitas",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    conta_padrao_despesas = forms.ModelChoiceField(
        queryset=ContaBancaria.objects.none(), # Será filtrado no __init__
        required=False,
        label="Conta/Caixa Padrão para Despesas",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Igreja
        # Exclui 'organizacao' pois será definida na view
        exclude = ['organizacao']
        # Listar todos os campos do modelo unificado (exceto organizacao)
        fields = [
            'nome_igreja', 'tipo_igreja', 'igreja_superior', 'data_fundacao',
            'cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'pais',
            'email', 'cnpj', 'telefone', 'celular', 'site', 'conta_padrao_receitas', 'conta_padrao_despesas',
            'pastor_local', 'pastor_regional',
            'moeda', 'observacoes', 'logo1', 'logo2',
        ]
        widgets = {
            'nome_igreja': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_igreja': forms.Select(attrs={'class': 'form-select'}),
            # 'igreja_superior' já definido acima
            'data_fundacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'estado': forms.Select(attrs={'class': 'form-select'}), # Modelo já tem choices
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'pastor_local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Pastor/Responsável'}), # CORRIGIDO
            'pastor_regional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'moeda': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
            'logo1': forms.FileInput(attrs={'class': 'form-control'}),
            'logo2': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Pega a organização passada pela view para filtrar igreja_superior
        organizacao = kwargs.pop('organizacao', None)
        # Pega a instância da igreja (se estiver editando)
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if organizacao:
            # Filtra o queryset de 'igreja_superior' para mostrar apenas igrejas da mesma organização
            qs = Igreja.objects.filter(organizacao=organizacao)
            if instance:
                # Exclui a própria igreja da lista de superiores ao editar
                qs = qs.exclude(pk=instance.pk)
            self.fields['igreja_superior'].queryset = qs

             # Filtra contas padrão para mostrar apenas as da igreja que está sendo editada
            if instance: # Só faz sentido se estiver editando uma igreja existente
                self.fields['conta_padrao_receitas'].queryset = ContaBancaria.objects.filter(igreja=instance).order_by('nome_identificacao')
                self.fields['conta_padrao_despesas'].queryset = ContaBancaria.objects.filter(igreja=instance).order_by('nome_identificacao')
        

        else:
            # Se não houver organização, não mostra nenhuma igreja superior
            self.fields['igreja_superior'].queryset = Igreja.objects.none()
            self.fields['conta_padrao_receitas'].queryset = ContaBancaria.objects.none()
            self.fields['conta_padrao_despesas'].queryset = ContaBancaria.objects.none()

        # Definir empty_label para igreja_superior
        self.fields['igreja_superior'].empty_label = "Nenhuma (Igreja Sede ou sem vínculo)"
        self.fields['conta_padrao_receitas'].empty_label = "Nenhuma Conta/Caixa Padrão"
        self.fields['conta_padrao_despesas'].empty_label = "Nenhuma Conta/Caixa Padrão"


# --- FORMULÁRIO PARA EDITAR DADOS DA ORGANIZAÇÃO (PELO ADMIN DA ORG) ---
class OrganizacaoEditForm(forms.ModelForm):
    """ Formulário para o Admin da Org editar dados da própria organização """
    # Sobrescrever o campo estado para garantir o widget correto se necessário
    # Embora o modelo já tenha choices, definir explicitamente aqui é seguro
    estado = forms.ChoiceField(
        choices=[('', '---------')] + ESTADO_CHOICES, # Adiciona opção vazia
        required=False, # Manter como opcional se no modelo for blank=True, null=True
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Estado (Sede)"
    )

    class Meta:
        model = Organizacao
        # Definir os campos que o Admin da Org PODE editar
        # Excluir campos críticos como 'ativo', 'administrador_principal', 'data_criacao'
        fields = [
            'nome_fantasia', 'razao_social',
            'cnpj',
            'telefone', 'email',
            'cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado'
        ]
        widgets = {
            # Adicionar classes Bootstrap e máscaras se necessário
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}), # Adicionar máscara JS
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}), # Adicionar máscara JS
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}), # Adicionar máscara JS
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            # 'estado' já está definido acima com ChoiceField e Select widget
        }

class IgrejaEditForm(forms.ModelForm):
    class Meta:
        model = Igreja
        fields = [
            'nome_igreja', 'tipo_igreja', 'igreja_superior', 'data_fundacao',
            'cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'pais',
            'email', 'cnpj', 'telefone', 'celular', 'site',
            'pastor_local', 'pastor_regional',
            'moeda', 'observacoes', 'logo1', 'logo2',
            'conta_padrao_receitas', 'conta_padrao_despesas' # Adicionar os campos aqui
        ]
        widgets = {
            'data_fundacao': forms.DateInput(attrs={'type': 'date'}),
            # Adicione outros widgets se necessário
        }

    def __init__(self, *args, **kwargs):
        organizacao = kwargs.pop('organizacao', None)
        super().__init__(*args, **kwargs)

        if organizacao:
            # Filtrar igreja_superior para mostrar apenas igrejas da mesma organização
            self.fields['igreja_superior'].queryset = Igreja.objects.filter(organizacao=organizacao).exclude(pk=self.instance.pk if self.instance else None)
            
            # Filtrar contas padrão para mostrar apenas contas da mesma organização
            self.fields['conta_padrao_receitas'].queryset = ContaBancaria.objects.filter(organizacao=organizacao, ativa=True).order_by('nome_conta')
            self.fields['conta_padrao_despesas'].queryset = ContaBancaria.objects.filter(organizacao=organizacao, ativa=True).order_by('nome_conta')
        else:
            # Se não houver organização, esvaziar os querysets ou tratar como erro
            self.fields['igreja_superior'].queryset = Igreja.objects.none()
            self.fields['conta_padrao_receitas'].queryset = ContaBancaria.objects.none()
            self.fields['conta_padrao_despesas'].queryset = ContaBancaria.objects.none()

        # Adicionar classes CSS do Bootstrap aos campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.widgets.TextInput, forms.widgets.Textarea, forms.widgets.Select, forms.widgets.DateInput, forms.widgets.EmailInput, forms.widgets.URLInput, forms.widgets.NumberInput, forms.widgets.ClearableFileInput)):
                field.widget.attrs.update({'class': 'form-control form-control-sm'})
            elif isinstance(field.widget, forms.widgets.CheckboxInput):
                 field.widget.attrs.update({'class': 'form-check-input'})

                 
# Você pode adicionar outros formulários aqui conforme necessário,
# por exemplo, um formulário para editar o PerfilUsuario, etc.
