from django import forms
from .models import (
    AutomacaoAniversariantes,
    Aviso,
    WhatsAppConfiguracao,
    WhatsAppConfiguracaoGlobal,
)
from configuracao.models import Ministerio, Igreja
from django.contrib.auth import get_user_model
from django.utils import timezone
from secretaria.models import Membro, TipoPessoa, StatusPessoa
from datetime import date
from django.db.models import Q
from .selectors import (
    filtrar_status_whatsapp_para_tipos,
    status_queryset_whatsapp_por_tipos,
    tipos_exigem_status_restrito_whatsapp,
)

User = get_user_model()


def _tipos_pessoa_excluir_obsoleto(qs):
    return qs.exclude(
        Q(nome__iexact='obreiro')
        | Q(nome__iexact='obreira')
        | Q(nome__iexact='obreiros')
        | Q(nome__iexact='obreiras')
    )


def _tipos_pessoa_por_ministerio(ministerio):
    tipos_ids = (
        Membro.objects.filter(igreja__ministerio=ministerio, tipo_pessoa__isnull=False)
        .values_list('tipo_pessoa_id', flat=True)
        .distinct()
    )
    qs = _tipos_pessoa_excluir_obsoleto(TipoPessoa.objects.filter(pk__in=tipos_ids).order_by('nome'))

    # Fallback para ambientes novos, mantendo exclusão do tipo obsoleto.
    if not qs.exists():
        qs = _tipos_pessoa_excluir_obsoleto(TipoPessoa.objects.all().order_by('nome'))
    return qs


def _graus_eclesiasticos_por_ministerio(ministerio):
    escolhas_base = dict(getattr(Membro, 'GRAU_ECLESIASTICO_CHOICES', []))
    graus_ids = (
        Membro.objects.filter(igreja__ministerio=ministerio)
        .exclude(grau_eclesiastico__isnull=True)
        .exclude(grau_eclesiastico='')
        .values_list('grau_eclesiastico', flat=True)
        .distinct()
    )

    escolhas = [(valor, escolhas_base.get(valor, valor)) for valor in graus_ids if valor in escolhas_base]

    # Fallback para ambientes sem dados ainda.
    if not escolhas:
        escolhas = list(getattr(Membro, 'GRAU_ECLESIASTICO_CHOICES', []))
    return escolhas

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
    help_text="Ex: Membro, Visitante, Novo Convertido."
    )
    graus_eclesiasticos = forms.MultipleChoiceField(
        choices=[],
        label="Filtrar por Grau Eclesiástico",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        help_text="Ex: Diácono, Presbítero, Pastor."
    )
    status_pessoa = forms.ModelMultipleChoiceField(
        queryset=StatusPessoa.objects.none(),
        label="Filtrar por Status de Pessoa",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        help_text="Ex: Ativo, Inativo, Em Disciplina."
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
            self.fields['tipos_pessoa'].queryset = _tipos_pessoa_por_ministerio(ministerio)
            self.fields['graus_eclesiasticos'].choices = _graus_eclesiasticos_por_ministerio(ministerio)
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
            'auto_contribuicoes_template',
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
            'auto_contribuicoes_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'auto_lembrete_eventos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.ministerio = kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)
        if self.ministerio:
            self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=self.ministerio).order_by('nome_igreja')

    def clean_igreja(self):
        igreja = self.cleaned_data['igreja']
        if self.ministerio and igreja.ministerio_id != self.ministerio.id:
            raise forms.ValidationError('A igreja selecionada não pertence ao ministério atual.')
        return igreja


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
    graus_eclesiasticos = forms.MultipleChoiceField(
        choices=[],
        label='Filtrar por Grau Eclesiástico',
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
        tipos_selecionados = TipoPessoa.objects.none()

        if ministerio:
            tipos_qs = _tipos_pessoa_por_ministerio(ministerio)
            self.fields['tipos_pessoa'].queryset = tipos_qs
            self.fields['graus_eclesiasticos'].choices = _graus_eclesiasticos_por_ministerio(ministerio)
        else:
            tipos_qs = _tipos_pessoa_excluir_obsoleto(TipoPessoa.objects.all().order_by('nome'))
            self.fields['tipos_pessoa'].queryset = tipos_qs
            self.fields['graus_eclesiasticos'].choices = list(getattr(Membro, 'GRAU_ECLESIASTICO_CHOICES', []))

        if self.is_bound:
            tipos_ids = [
                int(valor)
                for valor in self.data.getlist('tipos_pessoa')
                if str(valor).isdigit()
            ]
            if tipos_ids:
                tipos_selecionados = tipos_qs.filter(pk__in=tipos_ids)

        self.fields['status_pessoa'].queryset = status_queryset_whatsapp_por_tipos(tipos_selecionados)

    def clean(self):
        cleaned_data = super().clean()
        tipos_pessoa = cleaned_data.get('tipos_pessoa')
        status_pessoa = cleaned_data.get('status_pessoa')

        if status_pessoa is None:
            return cleaned_data

        status_permitidos = filtrar_status_whatsapp_para_tipos(status_pessoa, tipos_pessoa)
        if status_permitidos.count() != status_pessoa.count():
            self.add_error(
                'status_pessoa',
                'Para tipos diferentes de Membro, use apenas status Ativo e Inativo.',
            )
            cleaned_data['status_pessoa'] = status_permitidos

        if tipos_exigem_status_restrito_whatsapp(tipos_pessoa):
            self.fields['status_pessoa'].help_text = (
                'Com tipo nao-membro, apenas Ativo/Inativo ficam disponiveis para envio WhatsApp.'
            )

        return cleaned_data

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
            'auto_contribuicoes_template',
            'auto_lembrete_eventos',
        ]
        widgets = {
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'numero_envio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 11999887766'}),
            'remetente_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Igreja Sede'}),
            'auto_aniversariantes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_novos_membros': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_contribuicoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_contribuicoes_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'auto_lembrete_eventos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'numero_envio': 'Numero do WhatsApp desta congregacao (somente digitos, com DDD).',
            'remetente_nome': 'Nome que aparecera nas mensagens automaticas.',
            'auto_contribuicoes_template': 'Variaveis: {nome}, {primeiro_nome}, {igreja}, {ministerio}, {valor}.',
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)


class AutomacaoAniversariantesForm(forms.ModelForm):
    class Meta:
        model = AutomacaoAniversariantes
        fields = [
            'whatsapp_ativo',
            'whatsapp_horario_envio',
            'whatsapp_template',
            'email_ativo',
            'email_horario_envio',
            'email_assunto_template',
            'email_mensagem_template',
            'followup_visitantes_ativo',
            'followup_visitantes_dias_apos',
            'followup_visitantes_template',
            'lembrete_eventos_ativo',
            'lembrete_eventos_template',
        ]
        widgets = {
            'whatsapp_ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'whatsapp_horario_envio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'whatsapp_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'email_ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_horario_envio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'email_assunto_template': forms.TextInput(attrs={'class': 'form-control'}),
            'email_mensagem_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 7}),
            'followup_visitantes_ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'followup_visitantes_dias_apos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 30}),
            'followup_visitantes_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'lembrete_eventos_ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'lembrete_eventos_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        help_texts = {
            'whatsapp_template': 'Variaveis disponiveis: {nome}, {primeiro_nome}, {igreja}, {ministerio}, {data_aniversario}.',
            'email_assunto_template': 'Ex.: Feliz aniversario, {primeiro_nome}!',
            'email_mensagem_template': 'Aceita HTML simples. Variaveis: {nome}, {primeiro_nome}, {igreja}, {ministerio}, {data_aniversario}.',
            'followup_visitantes_dias_apos': 'Quantidade de dias apos a primeira visita para envio da mensagem.',
            'followup_visitantes_template': 'Variaveis: {nome}, {primeiro_nome}, {igreja}, {ministerio}.',
            'lembrete_eventos_template': 'Variaveis: {quando}, {evento}, {hora}, {igreja}, {ministerio}.',
        }
