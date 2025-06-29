from django import forms
from .models import Aviso
from configuracao.models import Organizacao, Igreja
from django.contrib.auth import get_user_model
from django.utils import timezone
from secretaria.models import Membro, TipoPessoa, StatusPessoa
from datetime import date

User = get_user_model()

class AvisoForm(forms.ModelForm):
    """
    Formulário para criar e editar Avisos.
    """
    class Meta:
        model = Aviso
        fields = [
            'organizacao',
            'titulo',
            'conteudo',
            'autor',
            'igrejas_destino',
            'data_expiracao',
            'publicado',
        ]
        widgets = {
            'organizacao': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'autor': forms.Select(attrs={'class': 'form-select'}),
            'igrejas_destino': forms.SelectMultiple(attrs={'class': 'form-select'}), # Usar SelectMultiple para ManyToMany
            'data_expiracao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'publicado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # O campo 'organizacao' será filtrado na view ou no admin,
        # mas podemos garantir que o queryset inicial não seja muito amplo se necessário.
        # self.fields['organizacao'].queryset = Organizacao.objects.filter(...) # Exemplo de filtro
        self.fields['autor'].queryset = User.objects.filter(is_staff=True).order_by('first_name', 'last_name') # Exemplo: apenas staff pode ser autor
        self.fields['igrejas_destino'].queryset = Igreja.objects.all().order_by('nome_igreja') # Pode precisar filtrar por organização na view/form init se necessário
        self.fields['data_expiracao'].required = False # Tornar opcional explicitamente
        self.fields['autor'].required = False # Tornar opcional explicitamente (SET_NULL no modelo)
        self.fields['organizacao'].required = True # Tornar obrigatório explicitamente (CASCADE no modelo)

class EmailMassaForm(forms.Form):
    """
    Formulário para envio de e-mails em massa para membros.
    Permite selecionar destinatários por diversos critérios.
    """
    assunto = forms.CharField(
        label="Assunto do E-mail",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mensagem = forms.CharField(
        label="Mensagem",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
        help_text="Use HTML básico para formatação (ex: &lt;b&gt;negrito&lt;/b&gt;, &lt;br&gt; para quebra de linha)."
    )

    # Critérios de seleção de destinatários
    # Nota: Estes querysets serão filtrados no __init__ do formulário
    # para garantir que apenas dados da organização do usuário sejam exibidos.
    igrejas_destino = forms.ModelMultipleChoiceField(
        queryset=Igreja.objects.none(),
        label="Enviar para Igrejas Específicas",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        help_text="Selecione uma ou mais igrejas. Se nenhuma for selecionada, o e-mail será enviado para todos os membros da organização."
    )
    tipos_pessoa = forms.ModelMultipleChoiceField(
        queryset=TipoPessoa.objects.none(),
        label="Filtrar por Tipo de Pessoa",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        help_text="Ex: Membro, Visitante, Obreiro."
    )
    status_pessoa = forms.ModelMultipleChoiceField(
        queryset=StatusPessoa.objects.none(),
        label="Filtrar por Status de Pessoa",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        help_text="Ex: Ativo, Inativo, Em Disciplina."
    )
    apenas_ativos_para_relatorios = forms.BooleanField(
        label="Apenas Membros Ativos para Relatórios?",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Marque para enviar apenas para membros cujo status é considerado ativo para relatórios."
    )
    aniversariantes_do_mes = forms.BooleanField(
        label="Apenas Aniversariantes do Mês Atual?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Marque para enviar apenas para membros que fazem aniversário no mês atual."
    )

    def __init__(self, *args, **kwargs):
        organizacao = kwargs.pop('organizacao', None)
        super().__init__(*args, **kwargs)

        if organizacao:
            self.fields['igrejas_destino'].queryset = Igreja.objects.filter(organizacao=organizacao).order_by('nome_igreja')
            # Assumindo que TipoPessoa e StatusPessoa são globais ou filtrados de outra forma
            # Se forem por organização, você precisaria filtrar aqui:
            # self.fields['tipos_pessoa'].queryset = TipoPessoa.objects.filter(organizacao=organizacao).order_by('nome')
            # self.fields['status_pessoa'].queryset = StatusPessoa.objects.filter(organizacao=organizacao).order_by('nome')
            self.fields['tipos_pessoa'].queryset = TipoPessoa.objects.all().order_by('nome')
            self.fields['status_pessoa'].queryset = StatusPessoa.objects.all().order_by('nome')

    def clean(self):
        cleaned_data = super().clean()
        # Adicione validações adicionais aqui se necessário
        # Por exemplo, se nenhum critério de seleção for marcado, avisar o usuário.
        return cleaned_data
