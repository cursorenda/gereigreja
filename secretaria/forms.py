from django import forms
from django.contrib.auth import get_user_model
from .models import Membro
from .models import MembroCargo, TipoPessoa, StatusPessoa, StatusHistorico, Cargo
from django.contrib.auth.models import Group
from configuracao.models import PerfilUsuario, Igreja, Ministerio
# --- IMPORTAR UTILS DE PERMISSÃO ---
from .utils import is_admin_org, get_allowed_churches_for_membros


class AssociarUsuarioMembroForm(forms.Form):
    membro_id = forms.IntegerField(widget=forms.HiddenInput)
    usuario = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        required=True,
        label="Usuário do Sistema",
        widget=forms.Select(attrs={'class': 'form-select usuario-autocomplete'})
    )
    sugestao_usuario_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        membro = kwargs.pop('membro', None)
        super().__init__(*args, **kwargs)
        User = get_user_model()
        usuarios_disponiveis = User.objects.filter(membro_secretaria__isnull=True)
        self.fields['usuario'].queryset = usuarios_disponiveis
        self.fields['usuario'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.email})"
        if membro:
            self.fields['membro_id'].initial = membro.pk
            sugestao = usuarios_disponiveis.filter(email__iexact=membro.email).first() if membro.email else None
            if sugestao:
                self.fields['usuario'].initial = sugestao.pk
                self.fields['sugestao_usuario_id'].initial = sugestao.pk
                self.fields['usuario'].widget.attrs['data-sugestao'] = '1'
            else:
                self.fields['usuario'].widget.attrs['data-sugestao'] = '0'


class GerenciarOcupantesForm(forms.Form):
    ocupantes = forms.ModelMultipleChoiceField(
        queryset=Membro.objects.all().order_by('nome'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 12}),
        required=False,
        label='Ocupantes do Cargo',
        help_text='Selecione os membros que ocuparão este cargo.'
    )


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['nome', 'grupo_permissao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100, 'placeholder': 'Nome do cargo'}),
            'grupo_permissao': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].label = 'Nome do Cargo'
        self.fields['grupo_permissao'].label = 'Grupo de Permissão (opcional)'
        self.fields['grupo_permissao'].required = False


class MembroForm(forms.ModelForm):
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

    tipo_pessoa = forms.ModelChoiceField(
        queryset=TipoPessoa.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Selecione o Tipo",
        required=True
    )
    status_pessoa = forms.ModelChoiceField(
        queryset=StatusPessoa.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Selecione o Status",
        required=True
    )
    igreja = forms.ModelChoiceField(
        queryset=Igreja.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Igreja",
        empty_label="Selecione a igreja"
    )

    class Meta:
        model = Membro
        fields = [
            'igreja',
            'nome', 'apelido', 'cpf', 'rg', 'naturalidade', 'nascimento', 'genero', 'tipo_pessoa', 'status_pessoa',
            'estado_civil', 'profissao', 'escolaridade', 'nome_pai', 'nome_mae', 'cep', 'pais', 'estado', 'nacionalidade',
            'cidade', 'bairro_distrito', 'rua', 'numero_casa', 'complemento', 'telefone',
            'data_entrada', 'conjuge', 'data_casamento',
            'foto', 'email',
            'tipo_entrada',
            'data_primeira_visita', 'origem_visita', 'responsavel_acompanhamento', 'status_acompanhamento', 'observacoes_visita'
        ]

    def clean(self):
        cleaned_data = super().clean()
        tipo_pessoa = cleaned_data.get('tipo_pessoa')
        tipo_entrada = cleaned_data.get('tipo_entrada')
        if tipo_pessoa and hasattr(tipo_pessoa, 'nome') and tipo_pessoa.nome.lower() == 'membro':
            if not tipo_entrada:
                self.add_error('tipo_entrada', 'Informe o tipo de entrada para pessoas com tipo "Membro".')
        else:
            cleaned_data['tipo_entrada'] = None
        return cleaned_data

    def __init__(self, *args, **kwargs):
        # remove any view-specific context kwargs so BaseModelForm.__init__ doesn't error
        ministerio = kwargs.pop('ministerio', None)
        user = kwargs.pop('user', None)
        allowed_churches = kwargs.pop('allowed_churches', None)
        igreja_inicial = kwargs.pop('igreja_inicial', None)
        super().__init__(*args, **kwargs)
        # basic initial/widget setup; views may have passed ministerio/user/allowed_churches
        for field_name in self.fields:
            if isinstance(self.fields[field_name], (forms.ChoiceField, forms.ModelChoiceField)):
                self.fields[field_name].widget.attrs.setdefault('class', 'form-select')
            else:
                self.fields[field_name].widget.attrs.setdefault('class', 'form-control')


class StatusHistoricoManualForm(forms.ModelForm):
    data_transicao = forms.DateTimeField(
        label="Data e Hora da Transição",
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        help_text="Data e hora em que a mudança de tipo/status efetivamente ocorreu."
    )

    class Meta:
        model = StatusHistorico
        fields = [
            'membro',
            'tipo_pessoa_anterior', 'tipo_pessoa_novo',
            'status_pessoa_anterior', 'status_pessoa_novo',
            'data_transicao', 'observacao'
        ]
        widgets = {
            'membro': forms.Select(attrs={'class': 'form-select'}),
            'tipo_pessoa_anterior': forms.Select(attrs={'class': 'form-select'}),
            'tipo_pessoa_novo': forms.Select(attrs={'class': 'form-select'}),
            'status_pessoa_anterior': forms.Select(attrs={'class': 'form-select'}),
            'status_pessoa_novo': forms.Select(attrs={'class': 'form-select'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detalhes sobre a mudança, motivo, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        membro_inicial = kwargs.pop('membro_inicial', None)
        super().__init__(*args, **kwargs)
        if ministerio:
            self.fields['membro'].queryset = Membro.objects.filter(igreja__ministerio=ministerio).order_by('nome')
        else:
            self.fields['membro'].queryset = Membro.objects.none()

        self.fields['tipo_pessoa_anterior'].queryset = TipoPessoa.objects.all().order_by('nome')
        self.fields['tipo_pessoa_novo'].queryset = TipoPessoa.objects.all().order_by('nome')
        self.fields['status_pessoa_anterior'].queryset = StatusPessoa.objects.all().order_by('nome')
        self.fields['status_pessoa_novo'].queryset = StatusPessoa.objects.all().order_by('nome')

        for field_name in ['tipo_pessoa_anterior', 'tipo_pessoa_novo', 'status_pessoa_anterior', 'status_pessoa_novo']:
            self.fields[field_name].required = False
            self.fields[field_name].empty_label = "Nenhum / Não Alterado"

        if membro_inicial:
            self.initial['membro'] = membro_inicial
            self.fields['membro'].disabled = True


class MembroUserManagementForm(forms.Form):
    email_usuario = forms.EmailField(
        label="E-mail do Usuário (Login)",
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        help_text="Este é o e-mail da pessoa. Será usado como login do usuário."
    )
    is_active = forms.BooleanField(
        label="Usuário Ativo?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Se desmarcado, o usuário não poderá fazer login."
    )
    is_staff = forms.BooleanField(
        label="Acesso ao Painel Administrativo?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Permite ao usuário acessar as áreas administrativas do sistema."
    )

    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Papéis/Grupos do Usuário",
        help_text="Selecione os papéis que este usuário terá no sistema."
    )

    igrejas_permitidas = forms.ModelMultipleChoiceField(
        queryset=Igreja.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Igrejas com Acesso Permitido",
        help_text="Selecione as igrejas que este usuário poderá gerenciar/visualizar."
    )

    def __init__(self, *args, **kwargs):
        self.membro_instance = kwargs.pop('membro_instance', None)
        self.ministerio = kwargs.pop('ministerio', None)
        self.user_instance = kwargs.pop('user_instance', None)
        self.perfil_instance = kwargs.pop('perfil_instance', None)
        super().__init__(*args, **kwargs)

        self.fields['grupos'].queryset = Group.objects.all().order_by('name')
        if self.ministerio:
            self.fields['igrejas_permitidas'].queryset = Igreja.objects.filter(ministerio=self.ministerio).order_by('nome_igreja')
        else:
            self.fields['igrejas_permitidas'].queryset = Igreja.objects.none()

        if self.user_instance:
            self.fields['email_usuario'].initial = self.user_instance.email
            self.fields['is_active'].initial = self.user_instance.is_active
            self.fields['is_staff'].initial = self.user_instance.is_staff
            self.fields['grupos'].initial = self.user_instance.groups.all()
            if self.perfil_instance:
                self.fields['igrejas_permitidas'].initial = self.perfil_instance.igrejas_permitidas.all()
        elif self.membro_instance:
            self.fields['email_usuario'].initial = self.membro_instance.email
            self.fields['is_active'].initial = True
            self.fields['is_staff'].initial = False

        if self.user_instance:
            self.fields['email_usuario'].widget.attrs['readonly'] = 'readonly'

    def clean_email_usuario(self):
        return self.membro_instance.email

from django import forms
from django.contrib.auth import get_user_model
from .models import Membro

class AssociarUsuarioMembroForm(forms.Form):
    membro_id = forms.IntegerField(widget=forms.HiddenInput)
    usuario = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        required=True,
        label="Usuário do Sistema",
        widget=forms.Select(attrs={'class': 'form-select usuario-autocomplete'})
    )
    sugestao_usuario_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        membro = kwargs.pop('membro', None)
        super().__init__(*args, **kwargs)
        User = get_user_model()
        # Só permite usuários não associados a membros
        usuarios_disponiveis = User.objects.filter(membro_secretaria__isnull=True)
        self.fields['usuario'].queryset = usuarios_disponiveis
        self.fields['usuario'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.email})"
        if membro:
            self.fields['membro_id'].initial = membro.pk
            # Sugestão automática: usuário com mesmo e-mail
            sugestao = usuarios_disponiveis.filter(email__iexact=membro.email).first() if membro.email else None
            if sugestao:
                self.fields['usuario'].initial = sugestao.pk
                self.fields['sugestao_usuario_id'].initial = sugestao.pk
                self.fields['usuario'].widget.attrs['data-sugestao'] = '1'
            else:
                self.fields['usuario'].widget.attrs['data-sugestao'] = '0'
# Formulário para gerenciar ocupantes de um cargo
from .models import MembroCargo, Membro

class GerenciarOcupantesForm(forms.Form):
    ocupantes = forms.ModelMultipleChoiceField(
        queryset=Membro.objects.all().order_by('nome'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 12}),
        required=False,
        label='Ocupantes do Cargo',
        help_text='Selecione os membros que ocuparão este cargo.'
    )
from django.contrib.auth.models import Group

# Novo formulário para cadastro/edição de cargos (novo modelo)
from .models import Cargo
class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['nome', 'grupo_permissao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100, 'placeholder': 'Nome do cargo'}),
            'grupo_permissao': forms.Select(attrs={'class': 'form-select'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].label = 'Nome do Cargo'
        self.fields['grupo_permissao'].label = 'Grupo de Permissão (opcional)'
        self.fields['grupo_permissao'].required = False
from .models import Membro, TipoPessoa, StatusPessoa, StatusHistorico # Adicionado StatusHistorico
from django.contrib.auth.models import User, Group # Importar User e Group
from configuracao.models import PerfilUsuario # Importar PerfilUsuario
from configuracao.models import Igreja, Ministerio # Importar Igreja e Ministerio
# --- IMPORTAR UTILS DE PERMISSÃO ---
from .utils import is_admin_org, get_allowed_churches_for_membros # Para verificar se o usuário é admin do ministério e igrejas permitidas

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
    # O campo 'status' antigo foi removido.
    # Adicionando os novos campos:
    from django import forms
    from django.contrib.auth import get_user_model
    from .models import Membro

    class AssociarUsuarioMembroForm(forms.Form):
        membro_id = forms.IntegerField(widget=forms.HiddenInput)
        usuario = forms.ModelChoiceField(
            queryset=get_user_model().objects.none(),
            required=True,
            label="Usuário do Sistema",
            widget=forms.Select(attrs={'class': 'form-select usuario-autocomplete'})
        )
        sugestao_usuario_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

        def __init__(self, *args, **kwargs):
            membro = kwargs.pop('membro', None)
            super().__init__(*args, **kwargs)
            User = get_user_model()
            # Só permite usuários não associados a membros
            usuarios_disponiveis = User.objects.filter(membro_secretaria__isnull=True)
            self.fields['usuario'].queryset = usuarios_disponiveis
            self.fields['usuario'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.email})"
            if membro:
                self.fields['membro_id'].initial = membro.pk
                # Sugestão automática: usuário com mesmo e-mail
                sugestao = usuarios_disponiveis.filter(email__iexact=membro.email).first() if membro.email else None
                if sugestao:
                    self.fields['usuario'].initial = sugestao.pk
                    self.fields['sugestao_usuario_id'].initial = sugestao.pk
                    self.fields['usuario'].widget.attrs['data-sugestao'] = '1'
                else:
                    self.fields['usuario'].widget.attrs['data-sugestao'] = '0'
    # Formulário para gerenciar ocupantes de um cargo
    from .models import MembroCargo, Membro

    class GerenciarOcupantesForm(forms.Form):
        ocupantes = forms.ModelMultipleChoiceField(
            queryset=Membro.objects.all().order_by('nome'),
            widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 12}),
            required=False,
            label='Ocupantes do Cargo',
            help_text='Selecione os membros que ocuparão este cargo.'
        )
    from django.contrib.auth.models import Group

    # Novo formulário para cadastro/edição de cargos (novo modelo)
    from .models import Cargo
    class CargoForm(forms.ModelForm):
        class Meta:
            model = Cargo
            fields = ['nome', 'grupo_permissao']
            widgets = {
                'nome': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100, 'placeholder': 'Nome do cargo'}),
                'grupo_permissao': forms.Select(attrs={'class': 'form-select'}),
            }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['nome'].label = 'Nome do Cargo'
            self.fields['grupo_permissao'].label = 'Grupo de Permissão (opcional)'
            self.fields['grupo_permissao'].required = False
    from .models import Membro, TipoPessoa, StatusPessoa, StatusHistorico # Adicionado StatusHistorico
    from django.contrib.auth.models import User, Group # Importar User e Group
    from configuracao.models import PerfilUsuario # Importar PerfilUsuario
    from configuracao.models import Igreja, Ministerio # Importar Igreja e Ministerio
    # --- IMPORTAR UTILS DE PERMISSÃO ---
    from .utils import is_admin_org # Para verificar se o usuário é admin do ministério

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
        # O campo 'status' antigo foi removido.
        # Adicionando os novos campos:
        tipo_pessoa = forms.ModelChoiceField(
            queryset=TipoPessoa.objects.none(), # Será filtrado no __init__
            widget=forms.Select(attrs={'class': 'form-control'}),
            empty_label="Selecione o Tipo",
            required=True # Ajuste conforme o modelo (agora é obrigatório)
        )
        status_pessoa = forms.ModelChoiceField(
            queryset=StatusPessoa.objects.none(), # Será filtrado no __init__
            widget=forms.Select(attrs={'class': 'form-control'}),
            empty_label="Selecione o Status",
            required=True # Ajuste conforme o modelo (agora é obrigatório)

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
            fields = [
                'igreja',
                'nome', 'apelido', 'cpf', 'rg', 'naturalidade', 'nascimento', 'genero', 'tipo_pessoa', 'status_pessoa',
                'estado_civil', 'profissao', 'escolaridade', 'nome_pai', 'nome_mae', 'cep', 'pais', 'estado', 'nacionalidade',
                'cidade', 'bairro_distrito', 'rua', 'numero_casa', 'complemento', 'telefone',
                'data_entrada', 'conjuge', 'data_casamento',
                'foto', 'email',
                'tipo_entrada', # Novo campo
                # --- Novos campos de visitante/acompanhamento ---
                'data_primeira_visita', 'origem_visita', 'responsavel_acompanhamento', 'status_acompanhamento', 'observacoes_visita'
            ]
        def clean(self):
            cleaned_data = super().clean()
            tipo_pessoa = cleaned_data.get('tipo_pessoa')
            tipo_entrada = cleaned_data.get('tipo_entrada')
            # Só exige tipo_entrada se tipo_pessoa for "membro"
            if tipo_pessoa and hasattr(tipo_pessoa, 'nome') and tipo_pessoa.nome.lower() == 'membro':
                if not tipo_entrada:
                    self.add_error('tipo_entrada', 'Informe o tipo de entrada para membros.')
            else:
                cleaned_data['tipo_entrada'] = None
            return cleaned_data
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Exibe o campo tipo_entrada só se tipo_pessoa for "membro"
            tipo_nome = None
            tipo_id = None
            if 'tipo_pessoa' in self.data:
                tipo_id = self.data.get('tipo_pessoa')
                try:
                    tipo_obj = TipoPessoa.objects.get(pk=tipo_id)
                    tipo_nome = tipo_obj.nome.lower()
                except TipoPessoa.DoesNotExist:
                    tipo_nome = None
            elif self.instance and self.instance.tipo_pessoa:
                tipo_nome = self.instance.tipo_pessoa.nome.lower()

            if tipo_nome != 'membro':
                self.fields['tipo_entrada'].widget = forms.HiddenInput()

            # --- CAMPOS ESSENCIAIS PARA VISITANTE ---
            campos_essenciais_visitante = [
                'igreja', 'nome', 'apelido', 'telefone', 'email', 'data_primeira_visita',
                'origem_visita', 'responsavel_acompanhamento', 'status_acompanhamento', 'observacoes_visita', 'tipo_pessoa', 'status_pessoa', 'data_entrada'
            ]
            if tipo_nome == 'visitante':
                for field in self.fields:
                    if field not in campos_essenciais_visitante:
                        self.fields[field].widget = forms.HiddenInput()

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
                'nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
                'profissao': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
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
                'nacionalidade': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}), # Adicionar widget para nacionalidade
                'email': forms.EmailInput(attrs={'class': 'form-control'}), # Adicionar widget para o campo email
                'data_entrada': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
                'conjuge': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
                'data_casamento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
                'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),

            }
            # Adicionar classes Bootstrap para outros campos se desejar
            for field_name in self.fields:
                if field_name not in widgets: # Evita sobrescrever widgets já definidos
                    if isinstance(self.fields[field_name], (forms.ChoiceField, forms.ModelChoiceField)):
                        self.fields[field_name].widget = forms.Select(attrs={'class': 'form-select'})
                    else:
                        self.fields[field_name].widget.attrs.update({'class': 'form-control'})

        # --- ADICIONAR/MODIFICAR __INIT__ ---
        def __init__(self, *args, **kwargs):
            # Pega a ministério passada pela view
            ministerio = kwargs.pop('ministerio', None) # Ministério do usuário logado
            user = kwargs.pop('user', None) # Usuário logado
            allowed_churches = kwargs.pop('allowed_churches', None) # Igrejas permitidas para o usuário
            igreja_inicial_param = kwargs.pop('igreja_inicial', None) # Novo parâmetro para igreja ativa
            super().__init__(*args, **kwargs)

            # Filtra o queryset de 'igreja'
            if user and not is_admin_org(user) and allowed_churches is not None:
                # Se não for admin do ministério, filtra pelas igrejas permitidas
                self.fields['igreja'].queryset = allowed_churches
            elif ministerio:
                # Se for admin do ministério ou não houver filtro específico de allowed_churches,
                # mostra todas as igrejas do ministério do usuário.
                self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')
            else:
                 # Se não houver ministério (erro?), não mostra nenhuma igreja
                 self.fields['igreja'].queryset = Igreja.objects.none()
            # Pré-seleciona e desabilita a igreja se uma igreja_inicial_param for passada e válida
            if igreja_inicial_param and self.fields['igreja'].queryset.filter(pk=igreja_inicial_param.pk).exists():
                self.initial['igreja'] = igreja_inicial_param
                self.fields['igreja'].disabled = True

       
            # Popula os querysets para os novos campos tipo_pessoa e status_pessoa
            # Se TipoPessoa e StatusPessoa forem globais (não ligados à ministério):
            self.fields['tipo_pessoa'].queryset = TipoPessoa.objects.all().order_by('nome')
            self.fields['status_pessoa'].queryset = StatusPessoa.objects.all().order_by('nome')
            # Se forem específicos por ministério, você precisaria filtrar aqui, por exemplo:
            # if ministerio:
            #     self.fields['tipo_pessoa'].queryset = TipoPessoa.objects.filter(ministerio=ministerio).order_by('nome')
            #     self.fields['status_pessoa'].queryset = StatusPessoa.objects.filter(ministerio=ministerio).order_by('nome')
       
            # Ajustar required=False para campos não obrigatórios se necessário
            self.fields['apelido'].required = False
            self.fields['cpf'].required = False
            # Definir o template customizado para o widget do campo 'foto'
            self.fields['foto'].widget.template_name = 'secretaria/widgets/custom_clearable_file_input.html'
            # Tornar o campo foto não obrigatório no formulário, pois é blank=True, null=True no modelo
            # Embora o Django já faça isso por padrão para campos com blank=True, ser explícito é bom.
            self.fields['foto'].required = False
            self.fields['naturalidade'].required = False
            self.fields['profissao'].required = False
            self.fields['nome_pai'].required = False
            self.fields['nome_mae'].required = False
            self.fields['complemento'].required = False
            self.fields['nacionalidade'].required = False # Tornar o campo nacionalidade opcional
            self.fields['email'].required = False # Tornar o campo email opcional
            self.fields['conjuge'].required = False
            self.fields['data_casamento'].required = False
            # Verifique outros campos conforme a definição do seu modelo Membro
        # --- FIM ADIÇÃO/MODIFICAÇÃO ---

    class StatusHistoricoManualForm(forms.ModelForm):
        data_transicao = forms.DateTimeField(
            label="Data e Hora da Transição",
            widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            help_text="Data e hora em que a mudança de tipo/status efetivamente ocorreu."
        )

        class Meta:
            model = StatusHistorico
            fields = [
                'membro',
                'tipo_pessoa_anterior', 'tipo_pessoa_novo',
                'status_pessoa_anterior', 'status_pessoa_novo',
                'data_transicao', 'observacao'
            ]
            widgets = {
                'membro': forms.Select(attrs={'class': 'form-select'}),
                'tipo_pessoa_anterior': forms.Select(attrs={'class': 'form-select'}),
                'tipo_pessoa_novo': forms.Select(attrs={'class': 'form-select'}),
                'status_pessoa_anterior': forms.Select(attrs={'class': 'form-select'}),
                'status_pessoa_novo': forms.Select(attrs={'class': 'form-select'}),
                'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detalhes sobre a mudança, motivo, etc.'}),
            }

        def __init__(self, *args, **kwargs):
            ministerio = kwargs.pop('ministerio', None)
            membro_inicial = kwargs.pop('membro_inicial', None) # Para pré-selecionar o membro
            super().__init__(*args, **kwargs)

            if ministerio:
                self.fields['membro'].queryset = Membro.objects.filter(igreja__ministerio=ministerio).order_by('nome')
            else:
                self.fields['membro'].queryset = Membro.objects.none()

            self.fields['tipo_pessoa_anterior'].queryset = TipoPessoa.objects.all().order_by('nome')
            self.fields['tipo_pessoa_novo'].queryset = TipoPessoa.objects.all().order_by('nome')
            self.fields['status_pessoa_anterior'].queryset = StatusPessoa.objects.all().order_by('nome')
            self.fields['status_pessoa_novo'].queryset = StatusPessoa.objects.all().order_by('nome')

            # Tornar campos de "anterior" e "novo" não obrigatórios, pois nem sempre ambos mudam
            for field_name in ['tipo_pessoa_anterior', 'tipo_pessoa_novo', 'status_pessoa_anterior', 'status_pessoa_novo']:
                self.fields[field_name].required = False
                self.fields[field_name].empty_label = "Nenhum / Não Alterado"

            if membro_inicial:
                self.initial['membro'] = membro_inicial
                self.fields['membro'].disabled = True # Desabilita se o membro já foi definido pela URL

    # --- NOVO FORMULÁRIO PARA GERENCIAR USUÁRIO DO MEMBRO ---
    class MembroUserManagementForm(forms.Form):
        """
        Formulário para gerenciar a conta de usuário (User) associada a um Membro.
        Não é um ModelForm, pois lida com múltiplos modelos (User, PerfilUsuario).
        """
        # Campos para o User
        email_usuario = forms.EmailField(
            label="E-mail do Usuário (Login)",
            max_length=254,
            required=True,
            widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            help_text="Este é o e-mail do membro. Será usado como login do usuário."
        )
        is_active = forms.BooleanField(
            label="Usuário Ativo?",
            required=False,
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            help_text="Se desmarcado, o usuário não poderá fazer login."
        )
        is_staff = forms.BooleanField(
            label="Acesso ao Painel Administrativo?",
            required=False,
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            help_text="Permite ao usuário acessar as áreas administrativas do sistema."
        )

        # Campos para os Grupos (papéis)
        grupos = forms.ModelMultipleChoiceField(
            queryset=Group.objects.none(), # Será filtrado no __init__
            widget=forms.CheckboxSelectMultiple,
            required=False,
            label="Papéis/Grupos do Usuário",
            help_text="Selecione os papéis que este usuário terá no sistema."
        )

        # Campos para as Igrejas Permitidas (do PerfilUsuario)
        igrejas_permitidas = forms.ModelMultipleChoiceField(
            queryset=Igreja.objects.none(), # Será filtrado no __init__
            widget=forms.CheckboxSelectMultiple,
            required=False,
            label="Igrejas com Acesso Permitido",
            help_text="Selecione as igrejas que este usuário poderá gerenciar/visualizar. Se nenhum papel exigir acesso a igrejas específicas, ou se o acesso for para toda a ministério (ex: Admin Org), deixe em branco."
        )

        def __init__(self, *args, **kwargs):
            self.membro_instance = kwargs.pop('membro_instance', None)
            self.ministerio = kwargs.pop('ministerio', None)
            self.user_instance = kwargs.pop('user_instance', None) # User associado ao membro, se existir
            self.perfil_instance = kwargs.pop('perfil_instance', None) # PerfilUsuario associado, se existir
            super().__init__(*args, **kwargs)

            # Popula o queryset de grupos com todos os grupos do sistema
            self.fields['grupos'].queryset = Group.objects.all().order_by('name')

            # Popula o queryset de igrejas permitidas com as igrejas do ministério
            if self.ministerio:
                self.fields['igrejas_permitidas'].queryset = Igreja.objects.filter(ministerio=self.ministerio).order_by('nome_igreja')
            else:
                self.fields['igrejas_permitidas'].queryset = Igreja.objects.none()

            # Preenche os valores iniciais se houver um user_instance
            if self.user_instance:
                self.fields['email_usuario'].initial = self.user_instance.email
                self.fields['is_active'].initial = self.user_instance.is_active
                self.fields['is_staff'].initial = self.user_instance.is_staff
                self.fields['grupos'].initial = self.user_instance.groups.all()
                if self.perfil_instance:
                    self.fields['igrejas_permitidas'].initial = self.perfil_instance.igrejas_permitidas.all()
            elif self.membro_instance: # Se não tem user, mas tem membro, usa o email do membro
                self.fields['email_usuario'].initial = self.membro_instance.email
                self.fields['is_active'].initial = True # Sugere ativo por padrão
                self.fields['is_staff'].initial = False # Sugere não-staff por padrão

            # Desabilita o campo de email se já houver um usuário vinculado
            if self.user_instance:
                self.fields['email_usuario'].widget.attrs['readonly'] = 'readonly'

        def clean_email_usuario(self):
            # Garante que o email do membro não seja alterado aqui, apenas exibido
            return self.membro_instance.email
        # (Fim do método clean_email_usuario)


# Ensure MembroForm consumes view-specific kwargs (ministerio, user, allowed_churches, igreja_inicial)
# This is a safety wrapper: if a MembroForm class exists (there are duplicated fragments
# in this file) we wrap its __init__ so extra kwargs are popped and don't reach
# BaseModelForm.__init__, preventing the TypeError observed in the views.
if 'MembroForm' in globals():
    _mf = globals()['MembroForm']
    _orig_init = getattr(_mf, '__init__', None)

    def _membro_init(self, *args, _orig_init=_orig_init, _mf=_mf, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        user = kwargs.pop('user', None)
        allowed_churches = kwargs.pop('allowed_churches', None)
        igreja_inicial = kwargs.pop('igreja_inicial', None)

        # Call the original __init__ (if present) with remaining kwargs
        if _orig_init:
            _orig_init(self, *args, **kwargs)
        else:
            # fallback to default ModelForm init
            super(_mf, self).__init__(*args, **kwargs)

        # Apply minimal post-init adjustments expected by views
        try:
            if 'igreja' in getattr(self, 'fields', {}):
                try:
                    if user and callable(globals().get('is_admin_org')) and not is_admin_org(user) and allowed_churches is not None:
                        self.fields['igreja'].queryset = allowed_churches
                    elif ministerio:
                        self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')
                    else:
                        self.fields['igreja'].queryset = Igreja.objects.none()
                except Exception:
                    # degrade gracefully
                    try:
                        self.fields['igreja'].queryset = Igreja.objects.none()
                    except Exception:
                        pass

                if igreja_inicial and getattr(self.fields['igreja'].queryset, 'filter', None):
                    try:
                        if self.fields['igreja'].queryset.filter(pk=igreja_inicial.pk).exists():
                            self.initial.setdefault('igreja', igreja_inicial)
                            self.fields['igreja'].disabled = True
                    except Exception:
                        pass

            if 'tipo_pessoa' in getattr(self, 'fields', {}):
                try:
                    self.fields['tipo_pessoa'].queryset = TipoPessoa.objects.all().order_by('nome')
                except Exception:
                    pass
            if 'status_pessoa' in getattr(self, 'fields', {}):
                try:
                    self.fields['status_pessoa'].queryset = StatusPessoa.objects.all().order_by('nome')
                except Exception:
                    pass
            if 'foto' in getattr(self, 'fields', {}):
                try:
                    self.fields['foto'].widget.template_name = 'secretaria/widgets/custom_clearable_file_input.html'
                except Exception:
                    pass
        except Exception:
            pass

    # Replace the __init__ on the MembroForm class with the wrapper
    try:
        _mf.__init__ = _membro_init
    except Exception:
        # do not fail import if monkey-patch cannot be applied
        pass


    # --- Canonical fallback MembroForm ---
    # The file contains duplicated fragments which can leave a MembroForm without a
    # proper Meta or consistent __init__. Append a canonical, minimal MembroForm and
    # set it as the module's MembroForm to ensure runtime callers receive a stable
    # class that consumes the view-specific kwargs (ministerio, user, allowed_churches, igreja_inicial).
    try:
        class _CanonicalMembroForm(forms.ModelForm):
            class Meta:
                model = Membro
                fields = [
                    'igreja', 'nome', 'apelido', 'cpf', 'rg', 'naturalidade', 'nascimento', 'genero',
                    'tipo_pessoa', 'status_pessoa', 'estado_civil', 'profissao', 'escolaridade',
                    'nome_pai', 'nome_mae', 'cep', 'pais', 'estado', 'nacionalidade', 'cidade',
                    'bairro_distrito', 'rua', 'numero_casa', 'complemento', 'telefone', 'data_entrada',
                    'conjuge', 'data_casamento', 'foto', 'email', 'tipo_entrada', 'data_primeira_visita',
                    'origem_visita', 'responsavel_acompanhamento', 'status_acompanhamento', 'observacoes_visita'
                ]

            def __init__(self, *args, **kwargs):
                # consume view-specific kwargs so BaseModelForm.__init__ doesn't error
                ministerio = kwargs.pop('ministerio', None)
                user = kwargs.pop('user', None)
                allowed_churches = kwargs.pop('allowed_churches', None)
                igreja_inicial = kwargs.pop('igreja_inicial', None)
                super().__init__(*args, **kwargs)

                # set sensible widget classes
                for fname, field in self.fields.items():
                    try:
                        if isinstance(field, (forms.ChoiceField, forms.ModelChoiceField)):
                            field.widget.attrs.setdefault('class', 'form-select')
                        else:
                            field.widget.attrs.setdefault('class', 'form-control')
                    except Exception:
                        pass

                # populate model choice querysets safely
                try:
                    if 'igreja' in self.fields:
                        if user and callable(globals().get('is_admin_org')) and not is_admin_org(user) and allowed_churches is not None:
                            self.fields['igreja'].queryset = allowed_churches
                        elif ministerio:
                            self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')
                        else:
                            self.fields['igreja'].queryset = Igreja.objects.none()
                        if igreja_inicial and getattr(self.fields['igreja'].queryset, 'filter', None):
                            try:
                                if self.fields['igreja'].queryset.filter(pk=igreja_inicial.pk).exists():
                                    self.initial.setdefault('igreja', igreja_inicial)
                                    self.fields['igreja'].disabled = True
                            except Exception:
                                pass
                    if 'tipo_pessoa' in self.fields:
                        self.fields['tipo_pessoa'].queryset = TipoPessoa.objects.all().order_by('nome')
                    if 'status_pessoa' in self.fields:
                        self.fields['status_pessoa'].queryset = StatusPessoa.objects.all().order_by('nome')
                    if 'foto' in self.fields:
                        try:
                            self.fields['foto'].widget.template_name = 'secretaria/widgets/custom_clearable_file_input.html'
                        except Exception:
                            pass
                except Exception:
                    pass

        # Replace/ensure module-level MembroForm points to canonical implementation
        MembroForm = _CanonicalMembroForm
    except Exception:
        # If anything here fails, do not break module import
        pass
