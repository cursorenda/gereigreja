# c:\Gereigreja\contas\forms.py
from django import forms
from django.contrib.auth.models import User, Group
from configuracao.models import Organizacao, Igreja # Importar Igreja
from .models import Convite

# --- FORMULÁRIO DE REGISTRO ---
class RegistroForm(forms.Form):
    """ Formulário para autocadastro de Usuário e Organização inicial """
    # Campos do Usuário
    primeiro_nome = forms.CharField(
        label="Seu Primeiro Nome",
        max_length=30,
        required=True, # Nome é obrigatório
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: João'})
    )
    ultimo_nome = forms.CharField(
        label="Seu Sobrenome",
        max_length=150,
        required=True, # Sobrenome é obrigatório
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Silva'})
    )
    email = forms.EmailField(
        label="Seu E-mail (será seu login)",
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: joao.silva@email.com'})
    )
    senha = forms.CharField(
        label="Senha",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirmar_senha = forms.CharField(
        label="Confirmar Senha",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    # Campos da Organização
    nome_fantasia_org = forms.CharField(
        label="Nome da Organização/Ministério",
        max_length=150,
        required=True, # Nome da organização é obrigatório
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Ministério Exemplo Central'})
    )
    # Adicionar outros campos opcionais da organização se desejar coletar no registro
    # Ex: telefone_org = forms.CharField(required=False, ...)

    # Validações
    def clean_email(self):
        """ Verifica se o email já está em uso. """
        email = self.cleaned_data.get('email')
        if email: # Só valida se o campo email passou na validação básica
            # Verifica se já existe usuário com este email (case-insensitive)
            if User.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("Este endereço de e-mail já está cadastrado.")
            # Verifica se já existe usuário com este username (case-insensitive)
            # (Estamos usando o email como username)
            if User.objects.filter(username__iexact=email).exists():
                raise forms.ValidationError("Este endereço de e-mail já está cadastrado como nome de usuário.")
        return email

    def clean_confirmar_senha(self):
        """ Verifica se as senhas coincidem. """
        senha = self.cleaned_data.get("senha")
        confirmar_senha = self.cleaned_data.get("confirmar_senha")
        # Só compara se ambos os campos foram preenchidos
        if senha and confirmar_senha and senha != confirmar_senha:
            raise forms.ValidationError("As senhas não coincidem.")
        return confirmar_senha


# --- NOVO FORMULÁRIO DE CONVITE ---
class ConviteForm(forms.Form):
    """ Formulário simples para enviar um convite por e-mail. """
    email_convidado = forms.EmailField(
        label="E-mail do Convidado",
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Digite o e-mail de quem deseja convidar'})
    )

    # Validação para verificar se já existe um convite pendente ou usuário na organização
    def __init__(self, *args, **kwargs):
        # Pega a organização passada pela view
        self.organizacao = kwargs.pop('organizacao', None)
        super().__init__(*args, **kwargs)

    def clean_email_convidado(self):
        email = self.cleaned_data.get('email_convidado')
        if email and self.organizacao:
            # 1. Verifica se já existe um usuário com este email NA MESMA organização
            if User.objects.filter(email__iexact=email, perfil__organizacao=self.organizacao).exists():
                raise forms.ValidationError("Este usuário já pertence a esta organização.")

            # 2. Verifica se já existe um convite PENDENTE para este email NA MESMA organização
            if Convite.objects.filter(email_convidado__iexact=email, organizacao=self.organizacao, status='pendente').exists():
                raise forms.ValidationError("Já existe um convite pendente para este e-mail nesta organização.")

            # 3. Opcional: Verificar se o email já existe no sistema (mesmo em outra org)?
            # if User.objects.filter(email__iexact=email).exists():
            #     # Poderia avisar, mas permitir o convite para associar à nova org
            #     pass

        return email
# --- FIM FORMULÁRIO DE CONVITE ---
    # Opcional: Validação para nome da organização (ex: verificar se já existe?)
    # def clean_nome_fantasia_org(self):
    #     nome = self.cleaned_data.get('nome_fantasia_org')
    #     if nome and Organizacao.objects.filter(nome_fantasia__iexact=nome).exists():
    #         raise forms.ValidationError("Já existe uma organização com este nome fantasia.")
    #     return nome
# --- FIM FORMULÁRIO DE REGISTRO ---

# Adicione outros forms do app 'contas' aqui se houver (ex: LoginForm)


# --- NOVO FORMULÁRIO PARA ACEITAR CONVITE (USUÁRIO NOVO) ---
class AceitarConviteSetPasswordForm(forms.Form):
    """ Formulário para usuário novo definir senha e nome ao aceitar convite. """
    primeiro_nome = forms.CharField(
        label="Seu Primeiro Nome",
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Maria'})
    )
    ultimo_nome = forms.CharField(
        label="Seu Sobrenome",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Souza'})
    )
    senha = forms.CharField(
        label="Escolha uma Senha",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirmar_senha = forms.CharField(
        label="Confirmar Senha",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean_confirmar_senha(self):
        """ Verifica se as senhas coincidem. """
        senha = self.cleaned_data.get("senha")
        confirmar_senha = self.cleaned_data.get("confirmar_senha")
        if senha and confirmar_senha and senha != confirmar_senha:
            raise forms.ValidationError("As senhas não coincidem.")
        # Poderia adicionar validação de força da senha aqui usando PasswordValidators
        return confirmar_senha
# --- FIM FORMULÁRIO ---

# --- FORMULÁRIO EDITAR PAPÉIS E IGREJAS (ATUALIZADO) ---
class EditarPapeisUsuarioForm(forms.Form):
    """ Formulário para selecionar os grupos (papéis) e igrejas permitidas de um usuário. """
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Papéis Atribuídos (Grupos)"
    )
    # --- NOVO CAMPO ---
    igrejas_permitidas = forms.ModelMultipleChoiceField(
        queryset=Igreja.objects.none(), # Queryset será filtrado no __init__
        widget=forms.CheckboxSelectMultiple,
        required=False, # Permite não selecionar nenhuma igreja específica
        label="Igrejas com Acesso Permitido",
        help_text="Selecione as igrejas que este usuário poderá gerenciar/visualizar. Se nenhum papel exigir acesso a igrejas específicas, ou se o acesso for para toda a organização (ex: Admin Org), deixe em branco."
    )
    # --- FIM NOVO CAMPO ---

    def __init__(self, *args, **kwargs):
        # Pega a organização passada pela view
        organizacao = kwargs.pop('organizacao', None)
        super().__init__(*args, **kwargs)

        # Filtra o queryset de igrejas_permitidas se a organização foi fornecida
        if organizacao:
            self.fields['igrejas_permitidas'].queryset = Igreja.objects.filter(
                organizacao=organizacao
            ).order_by('nome_igreja')
        else:
            # Se não houver organização, não mostra nenhuma igreja (segurança)
            self.fields['igrejas_permitidas'].queryset = Igreja.objects.none()

# --- FIM FORMULÁRIO ---