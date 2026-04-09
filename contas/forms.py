# c:\Gereigreja\contas\forms.py
from django import forms
from django.db import models
from django.contrib.auth.models import User, Group
from configuracao.models import Ministerio, Igreja # Importar Igreja
from .models import Convite

# --- FORMULÁRIO DE REGISTRO ---
class RegistroForm(forms.Form):
    """ Formulário para autocadastro de Usuário e Ministério inicial """
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

    # Campos da Ministério
    nome_fantasia_org = forms.CharField(
        label="Nome do Ministério",
        max_length=150,
        required=True, # Nome do ministério é obrigatório
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Ministério Exemplo Central'})
    )
    # Adicionar outros campos opcionais do ministério se desejar coletar no registro
    # Ex: telefone_org = forms.CharField(required=False, ...)

    # Campo de consentimento LGPD
    aceito_termos = forms.BooleanField(
        required=True,
        label='',  # O label será customizado no template
        error_messages={
            'required': 'Você deve aceitar os Termos de Uso e a Política de Privacidade para continuar.'
        },
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'aceito_termos'
        })
    )

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

    # Validação para verificar se já existe um convite pendente ou usuário na ministério
    def __init__(self, *args, **kwargs):
        # Pega a ministério passada pela view
        self.ministerio = kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)

    def clean_email_convidado(self):
        email = self.cleaned_data.get('email_convidado')
        if email and self.ministerio:
            # 1. Verifica se já existe um usuário com este email NA MESMA ministério
            if User.objects.filter(email__iexact=email, perfil__ministerio=self.ministerio).exists():
                raise forms.ValidationError("Este usuário já pertence a esta ministério.")

            # 2. Verifica se já existe um convite PENDENTE para este email NA MESMA ministério
            if Convite.objects.filter(email_convidado__iexact=email, ministerio=self.ministerio, status='pendente').exists():
                raise forms.ValidationError("Já existe um convite pendente para este e-mail nesta ministério.")

            # 3. Opcional: Verificar se o email já existe no sistema (mesmo em outra org)?
            # if User.objects.filter(email__iexact=email).exists():
            #     # Poderia avisar, mas permitir o convite para associar à nova org
            #     pass

        return email
# --- FIM FORMULÁRIO DE CONVITE ---
    # Opcional: Validação para nome do ministério (ex: verificar se já existe?)
    # def clean_nome_fantasia_org(self):
    #     nome = self.cleaned_data.get('nome_fantasia_org')
    #     if nome and Ministerio.objects.filter(nome_fantasia__iexact=nome).exists():
    #         raise forms.ValidationError("Já existe uma ministério com este nome fantasia.")
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
        help_text="Selecione as igrejas que este usuário poderá gerenciar/visualizar. Se nenhum papel exigir acesso a igrejas específicas, ou se o acesso for para toda a ministério (ex: Admin Org), deixe em branco."
    )
    # --- FIM NOVO CAMPO ---

    def __init__(self, *args, **kwargs):
        # Pega a ministério passada pela view
        ministerio = kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)

        # Filtra o queryset de igrejas_permitidas se a ministério foi fornecida
        if ministerio:
            self.fields['igrejas_permitidas'].queryset = Igreja.objects.filter(
                ministerio=ministerio
            ).order_by('nome_igreja')
        else:
            # Se não houver ministério, não mostra nenhuma igreja (segurança)
            self.fields['igrejas_permitidas'].queryset = Igreja.objects.none()

# --- FIM FORMULÁRIO ---


# --- FORMULÁRIO PARA EDITAR PERFIL DO USUÁRIO (LGPD) ---
class EditarMeuPerfilForm(forms.Form):
    """
    Formulário para o usuário editar seus próprios dados pessoais.
    
    Inclui dados do User (Django) e PerfilUsuario.
    Campos: nome, sobrenome, email, telefone, whatsapp, foto.
    """
    primeiro_nome = forms.CharField(
        label="Primeiro Nome",
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu primeiro nome'
        })
    )
    
    ultimo_nome = forms.CharField(
        label="Sobrenome",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome'
        })
    )
    
    email = forms.EmailField(
        label="E-mail",
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com'
        }),
        help_text="Este e-mail será usado para login no sistema"
    )
    
    telefone_contato = forms.CharField(
        label="Telefone de Contato",
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(__) _____-____'
        })
    )
    
    whatsapp_contato = forms.CharField(
        label="WhatsApp",
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(__) _____-____'
        })
    )
    
    foto_perfil = forms.ImageField(
        label="Foto de Perfil",
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Formatos aceitos: JPG, PNG. Tamanho máximo: 5MB"
    )
    
    def clean_email(self):
        """
        Valida se o email já está em uso por outro usuário.
        """
        email = self.cleaned_data.get('email')
        user_id = self.initial.get('user_id')  # ID do usuário atual (passado na inicialização)
        
        if email:
            # Verifica se existe outro usuário com este email
            existing_user = User.objects.filter(email__iexact=email).exclude(id=user_id).first()
            if existing_user:
                raise forms.ValidationError('Este e-mail já está sendo usado por outro usuário.')
        
        return email
    
    def clean_foto_perfil(self):
        """
        Valida tamanho e tipo da foto de perfil.
        """
        foto = self.cleaned_data.get('foto_perfil')
        
        if foto:
            # Verifica tamanho (5MB = 5 * 1024 * 1024 bytes)
            if foto.size > 5 * 1024 * 1024:
                raise forms.ValidationError('A imagem deve ter no máximo 5MB.')
            
            # Verifica tipo de arquivo
            valid_types = ['image/jpeg', 'image/png', 'image/jpg']
            if foto.content_type not in valid_types:
                raise forms.ValidationError('Apenas arquivos JPG e PNG são permitidos.')
        
        return foto


class PermissionRequestForm(forms.Form):
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label='Permissao/Grupo Desejado',
        empty_label='Selecione o grupo de permissao',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    justificativa = forms.CharField(
        label='Justificativa',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Explique por que voce precisa desta permissao.',
            }
        ),
    )
    prioridade = forms.ChoiceField(
        label='Prioridade',
        choices=[
            ('baixa', 'Baixa - Pode aguardar'),
            ('media', 'Media - Necessario em breve'),
            ('alta', 'Alta - Necessario urgente'),
            ('urgente', 'Urgente - Bloqueio critico'),
        ],
        initial='media',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    igreja_contexto = forms.ModelChoiceField(
        queryset=Igreja.objects.none(),
        label='Igreja Contexto',
        required=False,
        empty_label='Nenhuma igreja especifica',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        ministerio = kwargs.pop('ministerio', None)
        igreja_ativa = kwargs.pop('igreja_ativa', None)
        super().__init__(*args, **kwargs)

        if user:
            grupos_usuario = user.groups.values_list('id', flat=True)
            self.fields['grupo'].queryset = Group.objects.exclude(id__in=grupos_usuario).order_by('name')

        if user and ministerio:
            from core.utils import get_igrejas_permitidas
            igrejas_permitidas = get_igrejas_permitidas(user, ministerio)
            if igreja_ativa:
                igreja_id = igreja_ativa.pk if hasattr(igreja_ativa, 'pk') else igreja_ativa
                self.fields['igreja_contexto'].queryset = Igreja.objects.filter(
                    models.Q(pk__in=igrejas_permitidas.values_list('pk', flat=True)) | models.Q(pk=igreja_id)
                ).filter(ministerio=ministerio).distinct()
                self.initial['igreja_contexto'] = igreja_id
            else:
                self.fields['igreja_contexto'].queryset = igrejas_permitidas


class PermissionRequestResponseForm(forms.Form):
    ACAO_CHOICES = [
        ('aprovar', 'Aprovar Solicitacao'),
        ('rejeitar', 'Rejeitar Solicitacao'),
    ]

    acao = forms.ChoiceField(
        label='Decisao',
        choices=ACAO_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    observacao = forms.CharField(
        label='Observacao',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Comentario da avaliacao',
            }
        ),
        help_text='Explique o motivo da decisao, especialmente em rejeicao.',
    )

    def clean(self):
        cleaned_data = super().clean()
        acao = cleaned_data.get('acao')
        observacao = cleaned_data.get('observacao', '')
        if acao == 'rejeitar' and len(observacao.strip()) < 10:
            raise forms.ValidationError('Forneca uma explicacao para a rejeicao (minimo 10 caracteres).')
        return cleaned_data
