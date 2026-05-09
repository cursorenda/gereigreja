from django import forms
from .models import Aviso, WhatsAppConfiguracao, WhatsAppConfiguracaoGlobal
from configuracao.models import Ministerio, Igreja
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
            'ministerio',
            'titulo',
            'conteudo',
            'autor',
            'igrejas_destino',
            'data_expiracao',
            'publicado',
        ]
        widgets = {
            'ministerio': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'autor': forms.Select(attrs={'class': 'form-select'}),
            'igrejas_destino': forms.SelectMultiple(attrs={'class': 'form-select'}), # Usar SelectMultiple para ManyToMany
            'data_expiracao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'publicado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)

        if ministerio is not None:
            self.fields['ministerio'].queryset = Ministerio.objects.filter(pk=ministerio.pk)
            self.fields['ministerio'].initial = ministerio
            self.fields['igrejas_destino'].queryset = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')
        else:
            self.fields['igrejas_destino'].queryset = Igreja.objects.all().order_by('nome_igreja')

        self.fields['autor'].queryset = User.objects.filter(is_staff=True).order_by('first_name', 'last_name') # Exemplo: apenas staff pode ser autor
        self.fields['data_expiracao'].required = False # Tornar opcional explicitamente
        self.fields['autor'].required = False # Tornar opcional explicitamente (SET_NULL no modelo)
        self.fields['ministerio'].required = True # Tornar obrigatório explicitamente (CASCADE no modelo)

class EmailMassaForm(forms.Form):
    """
    Formulário para envio de e-mails em massa para pessoas.
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
    # para garantir que apenas dados do ministério do usuário sejam exibidos.
    igrejas_destino = forms.ModelMultipleChoiceField(
        queryset=Igreja.objects.none(),
        label="Enviar para Igrejas Específicas",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
    help_text="Selecione uma ou mais igrejas. Se nenhuma for selecionada, o e-mail será enviado para todas as pessoas do ministério."
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
    label="Apenas Pessoas Ativas para Relatórios?",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    help_text="Marque para enviar apenas para pessoas cujo status é considerado ativo para relatórios."
    )
    aniversariantes_do_mes = forms.BooleanField(
        label="Apenas Aniversariantes do Mês Atual?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    help_text="Marque para enviar apenas para pessoas que fazem aniversário no mês atual."
    )

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)

        if ministerio:
            self.fields['igrejas_destino'].queryset = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')
            # Assumindo que TipoPessoa e StatusPessoa são globais ou filtrados de outra forma
            # Se forem por ministério, você precisaria filtrar aqui:
            # self.fields['tipos_pessoa'].queryset = TipoPessoa.objects.filter(ministerio=ministerio).order_by('nome')
            # self.fields['status_pessoa'].queryset = StatusPessoa.objects.filter(ministerio=ministerio).order_by('nome')
            self.fields['tipos_pessoa'].queryset = TipoPessoa.objects.all().order_by('nome')
            self.fields['status_pessoa'].queryset = StatusPessoa.objects.all().order_by('nome')


class WhatsAppConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = WhatsAppConfiguracao
        fields = [
            'igreja',
            'ativo',
            'numero_envio',
            'remetente_nome',
            'session_name',
            'waha_base_url',
            'waha_api_key',
            'webhook_token',
            'auto_aniversariantes',
            'auto_novos_membros',
            'auto_contribuicoes',
            'auto_lembrete_eventos',
        ]
        widgets = {
            'igreja': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'numero_envio': forms.TextInput(attrs={'class': 'form-control'}),
            'remetente_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'session_name': forms.TextInput(attrs={'class': 'form-control'}),
            'waha_base_url': forms.URLInput(attrs={'class': 'form-control'}),
            'waha_api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'webhook_token': forms.TextInput(attrs={'class': 'form-control'}),
            'auto_aniversariantes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_novos_membros': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_contribuicoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_lembrete_eventos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)
        if ministerio:
            self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')


class WhatsAppMassaForm(forms.Form):
    mensagem = forms.CharField(
        label='Mensagem WhatsApp',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        help_text='Use variaveis: {nome}, {igreja}, {ministerio}',
    )
    tipos_pessoa = forms.ModelMultipleChoiceField(
        queryset=TipoPessoa.objects.none(),
        label='Filtrar por Tipo de Pessoa',
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
    )
    status_pessoa = forms.ModelMultipleChoiceField(
        queryset=StatusPessoa.objects.none(),
        label='Filtrar por Status da Pessoa',
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
    )
    aniversariantes_do_mes = forms.BooleanField(
        label='Apenas aniversariantes do mes',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    somente_com_celular = forms.BooleanField(
        label='Somente pessoas com celular preenchido',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)
        self.fields['tipos_pessoa'].queryset = TipoPessoa.objects.all().order_by('nome')
        self.fields['status_pessoa'].queryset = StatusPessoa.objects.all().order_by('nome')

class WhatsAppConfiguracaoGlobalForm(forms.ModelForm):
    """Form simplificado: o admin do ministerio so ativa/desativa.
    URL e API Key sao gerenciadas pela equipe tecnica via variaveis de ambiente.
    """
    class Meta:
        model = WhatsAppConfiguracaoGlobal
        fields = ['ativo']
        widgets = {
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'ativo': 'Ativar WhatsApp para todas as congregacoes do ministerio',
        }
        help_texts = {
            'ativo': 'Quando ativo, cada congregacao pode se conectar escaneando um QR code.',
        }


class WhatsAppConfiguracaoSimplificadaForm(forms.ModelForm):
    class Meta:
        model = WhatsAppConfiguracao
        fields = [
            'ativo',
            'numero_envio',
            'remetente_nome',
            'auto_aniversariantes',
            'auto_novos_membros',
            'auto_contribuicoes',
            'auto_lembrete_eventos',
        ]
        widgets = {
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'numero_envio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 11999887766'}),
            'remetente_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Igreja Sede'}),
            'auto_aniversariantes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_novos_membros': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_contribuicoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_lembrete_eventos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'numero_envio': 'Numero do WhatsApp desta congregacao (somente digitos, com DDD).',
            'remetente_nome': 'Nome que aparecera nas mensagens automaticas.',
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)
