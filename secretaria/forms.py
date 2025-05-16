# c:\Gereigreja\secretaria\forms.py
from django import forms
from .models import Membro, Tiposstatus
from configuracao.models import Igreja, Organizacao # Importar Igreja e Organizacao
# --- IMPORTAR UTILS DE PERMISSÃO ---
from .utils import is_admin_org # Para verificar se o usuário é admin da organização

class MembroForm(forms.ModelForm):
    # ... (campos genero, estado_civil, escolaridade como estão) ...
    genero = forms.ChoiceField(
        choices=[('M', 'Masculino'), ('F', 'Feminino')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    estado_civil = forms.ChoiceField(
        choices=[('Solteiro', 'Solteiro'), ('Casado', 'Casado'), ('Divorciado', 'Divorciado'), ('Amasiado', 'Amasiado'), ('Viuvo', 'Viuvo')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    escolaridade = forms.ChoiceField(
        choices=[('Ensino Fundamental Incompleto', 'Ensino Fundamental Incompleto'), ('Ensino Fundamental Completo', 'Ensino Fundamental Completo'), ('Ensino Médio Incompleto', 'Ensino Médio Incompleto'), ('Ensino Médio Completo', 'Ensino Médio Completo'), ('Ensino Superior Incompleto', 'Ensino Superior Incompleto'), ('Ensino Superior Completo', 'Ensino Superior Completo'), ('Pós-graduação', 'Pós-graduação'), ('Mestrado', 'Mestrado'), ('Sem Escolaridade', 'Sem Escolaridade'), ('Doutorado', 'Doutorado')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ModelChoiceField(
        queryset=Tiposstatus.objects.none(), 
        # Queryset inicial vazio, será filtrado no __init__
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Selecione o status",
        required=False # Tornar opcional se aplicável
    )
    # --- ADICIONAR CAMPO IGREJA ---
    igreja = forms.ModelChoiceField(
        queryset=Igreja.objects.none(), # Queryset inicial vazio, será filtrado no __init__
        widget=forms.Select(attrs={'class': 'form-select'}), # Usar form-select para consistência
        label="Igreja",
        empty_label="Selecione a igreja"
    )
    # --- FIM ADIÇÃO ---

    class Meta:
        model = Membro
        # --- ADICIONAR 'igreja' AOS FIELDS ---
        fields = [
            'igreja', # Adicionado aqui
            'nome', 'apelido', 'cpf', 'rg', 'naturalidade', 'nascimento', 'genero',
            'estado_civil', 'profissao', 'escolaridade', 'nome_pai', 'nome_mae',
            'cep', 'pais', 'estado', 'cidade', 'bairro_distrito', 'rua',
            'numero_casa', 'complemento', 'telefone', 'data_entrada', 'status',
            'conjuge', 'data_casamento'
        ]
        # --- FIM ADIÇÃO ---

        widgets = {
            # ... (widgets existentes) ...
            'nome': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'apelido': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 14}),
            'rg': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 20}),
            'naturalidade': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            # --- MODIFICAÇÃO AQUI ---
            # Especificar o formato que o widget DateInput deve usar ao renderizar o valor.
            # O input HTML type="date" espera 'YYYY-MM-DD'.
            'nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),            'profissao': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'nome_pai': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'nome_mae': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 9}),
            'pais': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'bairro_distrito': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'numero_casa': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 10}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 15}),
            'data_entrada': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'conjuge': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'data_casamento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
        }

    # --- ADICIONAR/MODIFICAR __INIT__ ---
    def __init__(self, *args, **kwargs):
        # Pega a organização passada pela view
        organizacao = kwargs.pop('organizacao', None) # Organização do usuário logado
        user = kwargs.pop('user', None) # Usuário logado
        allowed_churches = kwargs.pop('allowed_churches', None) # Igrejas permitidas para o usuário
        super().__init__(*args, **kwargs)

        # Filtra o queryset de 'igreja'
        if user and not is_admin_org(user) and allowed_churches is not None:
            # Se não for admin da organização, filtra pelas igrejas permitidas
            self.fields['igreja'].queryset = allowed_churches
        elif organizacao:
            # Se for admin da organização ou não houver filtro específico de allowed_churches,
            # mostra todas as igrejas da organização do usuário.
            self.fields['igreja'].queryset = Igreja.objects.filter(organizacao=organizacao).order_by('nome_igreja')
        else:
             # Se não houver organização (erro?), não mostra nenhuma igreja
             self.fields['igreja'].queryset = Igreja.objects.none()

       
        # Como Tiposstatus é global (não ligado à organização no models.py),
        # mostramos todos os status disponíveis.
        self.fields['status'].queryset = Tiposstatus.objects.all().order_by('status')
        # Ajustar required=False para campos não obrigatórios se necessário
        self.fields['apelido'].required = False
        self.fields['cpf'].required = False
        self.fields['rg'].required = False
        self.fields['naturalidade'].required = False
        self.fields['profissao'].required = False
        self.fields['nome_pai'].required = False
        self.fields['nome_mae'].required = False
        self.fields['complemento'].required = False
        self.fields['conjuge'].required = False
        self.fields['data_casamento'].required = False
        # Verifique outros campos conforme a definição do seu modelo Membro
    # --- FIM ADIÇÃO/MODIFICAÇÃO ---
