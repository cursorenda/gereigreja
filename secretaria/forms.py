# c:\Gereigreja\secretaria\forms.py
from django import forms
from .models import Membro, TipoPessoa, StatusPessoa, StatusHistorico # Adicionado StatusHistorico
from django.contrib.auth.models import User, Group # Importar User e Group
from configuracao.models import PerfilUsuario # Importar PerfilUsuario
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
        # --- ADICIONAR 'igreja' AOS FIELDS ---
        fields = [
            'igreja', # Adicionado aqui
            'nome', 'apelido', 'cpf', 'rg', 'naturalidade', 'nascimento', 'genero', 'tipo_pessoa', 'status_pessoa', # Adicionados novos campos
            'estado_civil', 'profissao', 'escolaridade', 'nome_pai', 'nome_mae', 'cep', 'pais', 'estado', 'nacionalidade', # Adicionado nacionalidade
            'cidade', 'bairro_distrito', 'rua', 'numero_casa', 'complemento', 'telefone', 
            'data_entrada', 'conjuge', 'data_casamento', # Removido 'status' antigo
            'foto', 'email'  # Adicionar o novo campo de foto e o email

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
            'nacionalidade': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}), # Adicionar widget para nacionalidade
            'email': forms.EmailInput(attrs={'class': 'form-control'}), # Adicionar widget para o campo email
            'data_entrada': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'conjuge': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'data_casamento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),

        }
        # Adicionar classes Bootstrap para outros campos se desejar
        for field_name in fields:
            if field_name not in widgets: # Evita sobrescrever widgets já definidos
                if isinstance(Membro._meta.get_field(field_name), (forms.fields.ChoiceField, forms.ModelChoiceField)):
                    widgets[field_name] = forms.Select(attrs={'class': 'form-select'})
                else:
                    widgets[field_name] = forms.TextInput(attrs={'class': 'form-control'})

    # --- ADICIONAR/MODIFICAR __INIT__ ---
    def __init__(self, *args, **kwargs):
        # Pega a organização passada pela view
        organizacao = kwargs.pop('organizacao', None) # Organização do usuário logado
        user = kwargs.pop('user', None) # Usuário logado
        allowed_churches = kwargs.pop('allowed_churches', None) # Igrejas permitidas para o usuário
        igreja_inicial_param = kwargs.pop('igreja_inicial', None) # Novo parâmetro para igreja ativa
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
        # Pré-seleciona e desabilita a igreja se uma igreja_inicial_param for passada e válida
        if igreja_inicial_param and self.fields['igreja'].queryset.filter(pk=igreja_inicial_param.pk).exists():
            self.initial['igreja'] = igreja_inicial_param
            self.fields['igreja'].disabled = True

       
        # Popula os querysets para os novos campos tipo_pessoa e status_pessoa
        # Se TipoPessoa e StatusPessoa forem globais (não ligados à organização):
        self.fields['tipo_pessoa'].queryset = TipoPessoa.objects.all().order_by('nome')
        self.fields['status_pessoa'].queryset = StatusPessoa.objects.all().order_by('nome')
        # Se forem específicos por organização, você precisaria filtrar aqui, por exemplo:
        # if organizacao:
        #     self.fields['tipo_pessoa'].queryset = TipoPessoa.objects.filter(organizacao=organizacao).order_by('nome')
        #     self.fields['status_pessoa'].queryset = StatusPessoa.objects.filter(organizacao=organizacao).order_by('nome')
       
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
        organizacao = kwargs.pop('organizacao', None)
        membro_inicial = kwargs.pop('membro_inicial', None) # Para pré-selecionar o membro
        super().__init__(*args, **kwargs)

        if organizacao:
            self.fields['membro'].queryset = Membro.objects.filter(igreja__organizacao=organizacao).order_by('nome')
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
        help_text="Selecione as igrejas que este usuário poderá gerenciar/visualizar. Se nenhum papel exigir acesso a igrejas específicas, ou se o acesso for para toda a organização (ex: Admin Org), deixe em branco."
    )

    def __init__(self, *args, **kwargs):
        self.membro_instance = kwargs.pop('membro_instance', None)
        self.organizacao = kwargs.pop('organizacao', None)
        self.user_instance = kwargs.pop('user_instance', None) # User associado ao membro, se existir
        self.perfil_instance = kwargs.pop('perfil_instance', None) # PerfilUsuario associado, se existir
        super().__init__(*args, **kwargs)

        # Popula o queryset de grupos com todos os grupos do sistema
        self.fields['grupos'].queryset = Group.objects.all().order_by('name')

        # Popula o queryset de igrejas permitidas com as igrejas da organização
        if self.organizacao:
            self.fields['igrejas_permitidas'].queryset = Igreja.objects.filter(organizacao=self.organizacao).order_by('nome_igreja')
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
