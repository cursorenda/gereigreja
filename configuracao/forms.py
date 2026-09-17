
from django import forms
from .models import ConfiguracaoSistema

class ConfiguracaoNotificacoesForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSistema
        fields = [
            'notificar_eventos',
            'notificar_aniversarios',
            'notificar_pre_cadastro_secretario_pastor',
            'notificar_pre_cadastro_admin',
        ]
        widgets = {
            'notificar_eventos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_aniversarios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_pre_cadastro_secretario_pastor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_pre_cadastro_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'notificar_eventos': 'Enviar notificações de eventos?',
            'notificar_aniversarios': 'Enviar notificações de aniversários?',
            'notificar_pre_cadastro_secretario_pastor': 'Notificar Secretário/Pastor Local sobre auto-cadastro?',
            'notificar_pre_cadastro_admin': 'Notificar Admin Ministério sobre auto-cadastro?',
        }

from django import forms
from .models import ConfiguracaoSistema

class ConfiguracaoSistemaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSistema
        fields = [
            'notificar_eventos',
            'notificar_aniversarios',
            'notificar_pre_cadastro_secretario_pastor',
            'notificar_pre_cadastro_admin',
            'ebd_periodo',
            'ebd_dia_semana',
            'ebd_horario',
            'url_biblia_online',
            'url_harpa_crista',
        ]
        widgets = {
            'notificar_eventos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_aniversarios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_pre_cadastro_secretario_pastor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_pre_cadastro_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ebd_periodo': forms.Select(attrs={'class': 'form-select'}),
            'ebd_dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'ebd_horario': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'url_biblia_online': forms.URLInput(attrs={'class': 'form-control'}),
            'url_harpa_crista': forms.URLInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'notificar_eventos': 'Enviar notificações de eventos?',
            'notificar_aniversarios': 'Enviar notificações de aniversários?',
            'notificar_pre_cadastro_secretario_pastor': 'Notificar Secretário/Pastor Local sobre auto-cadastro?',
            'notificar_pre_cadastro_admin': 'Notificar Admin Ministério sobre auto-cadastro?',
            'ebd_periodo': 'Período da Escola Bíblica',
            'ebd_dia_semana': 'Dia padrão da EBD',
            'ebd_horario': 'Horário padrão da EBD',
            'url_biblia_online': 'URL — Bíblia Online',
            'url_harpa_crista': 'URL — Harpa Cristã',
        }


class ConfiguracaoEBDForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSistema
        fields = [
            'ebd_periodo',
            'ebd_dia_semana',
            'ebd_horario',
        ]
        widgets = {
            'ebd_periodo': forms.Select(attrs={'class': 'form-select'}),
            'ebd_dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'ebd_horario': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }


class ConfiguracaoPortalForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSistema
        fields = [
            'url_biblia_online',
            'url_harpa_crista',
        ]
        widgets = {
            'url_biblia_online': forms.URLInput(attrs={'class': 'form-control'}),
            'url_harpa_crista': forms.URLInput(attrs={'class': 'form-control'}),
        }
# c:\Gereigreja\configuracao\forms.py
from django import forms
from .models import ESTADO_CHOICES 
from .models import Ministerio, Igreja, PerfilUsuario, Plano, AssinaturaMinisterio, ModeloCartaRecomendacao, ProgramacaoPadraoIgreja, Departamento, DepartamentoCapacidade, DepartamentoMinisterial

from django.contrib.auth.models import User # Modelo de usuário padrão
from financeiro.models import ContaBancaria # Importar ContaBancaria
from django.db import transaction # Para garantir atomicidade no registro
from django.db.models import Q
from django.contrib.auth.models import User # Mantido
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# --- Widget Customizado para Upload de Imagem ---
class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = 'configuracao/widgets/custom_clearable_file_input.html'
    # Você pode customizar os textos padrão se quiser (opcional):
    # initial_text = 'Logo atual:'
    # input_text = 'Alterar:'
    # clear_checkbox_label = 'Remover logo atual'



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
    conta_padrao_financeiro = forms.ModelChoiceField(
        queryset=ContaBancaria.objects.none(), # Será filtrado no __init__
        required=False,
        label="Conta/Caixa Padrão Financeiro",
        help_text="Conta/Caixa padrão para receitas e despesas desta igreja.",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    conta_padrao_eventos = forms.ModelChoiceField(
        queryset=ContaBancaria.objects.none(), # Será filtrado no __init__
        required=False,
        label="Conta/Caixa Padrão para Eventos",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Igreja
        # Exclui 'ministerio' pois será definida na view
        exclude = ['ministerio']
        # Listar todos os campos do modelo unificado (exceto ministerio)
        fields = [
            'nome_igreja', 'tipo_igreja', 'igreja_superior', 'data_fundacao',
            'cep', 'rua', 'numero_casa', 'complemento', 'bairro_distrito', 'cidade', 'estado', 'pais',
            'email', 'cnpj', 'telefone', 'celular', 'site', 'conta_padrao_financeiro',
            'conta_padrao_eventos',
            'pastor_local', 'pastor_regional',
            'moeda', 'ebd_periodo', 'ebd_dia_semana', 'ebd_horario',
            'ebd_pontos_presente', 'ebd_pontos_biblia', 'ebd_pontos_revista', 'ebd_pontos_oferta', 'ebd_pontos_visitante',
            'observacoes', 'logo1', 'logo2',
        ]
        widgets = {
            'nome_igreja': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_igreja': forms.Select(attrs={'class': 'form-select'}),
            # 'igreja_superior' já definido acima
            'data_fundacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'numero_casa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'bairro_distrito': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'estado': forms.Select(attrs={'class': 'form-select'}), # Modelo já tem choices
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'pastor_local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Pastor/Responsável'}),
            'pastor_regional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'moeda': forms.TextInput(attrs={'class': 'form-control'}),
            'ebd_periodo': forms.Select(attrs={'class': 'form-select'}),
            'ebd_dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'ebd_horario': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'ebd_pontos_presente': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'ebd_pontos_biblia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'ebd_pontos_revista': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'ebd_pontos_oferta': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'ebd_pontos_visitante': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
            'logo1': forms.FileInput(attrs={'class': 'form-control'}),
            'logo2': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Pega a ministério passada pela view para filtrar igreja_superior
        ministerio = kwargs.pop('ministerio', None)
        # Pega a instância da igreja (se estiver editando)
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if ministerio:
            qs_igreja_superior = Igreja.objects.filter(ministerio=ministerio)
            
            if instance and instance.pk: # Editando uma igreja existente
                if instance.tipo_igreja in ['sede', 'independente']:
                    self.fields['igreja_superior'].queryset = Igreja.objects.none()
                    self.fields['igreja_superior'].widget.attrs['disabled'] = True
                    self.fields['igreja_superior'].required = False
                    self.initial['igreja_superior'] = None
                else:
                    # Para outros tipos, filtra para não mostrar a própria igreja
                    self.fields['igreja_superior'].queryset = qs_igreja_superior.exclude(pk=instance.pk)
            else: # Criando uma nova igreja
                self.fields['igreja_superior'].queryset = qs_igreja_superior


            # Filtra contas padrão para mostrar apenas as da igreja que está sendo editada/criada
            # Se for uma nova igreja (instance is None), o queryset de contas será vazio,
            # o que é correto, pois a igreja precisa ser salva antes de ter contas.
            if instance:
                contas_qs = ContaBancaria.objects.filter(igreja=instance).order_by('nome_identificacao')
                self.fields['conta_padrao_financeiro'].queryset = contas_qs
                self.fields['conta_padrao_eventos'].queryset = contas_qs
                conta_financeira_inicial = instance.conta_padrao_receitas or instance.conta_padrao_despesas
                if conta_financeira_inicial and not self.initial.get('conta_padrao_financeiro'):
                    self.initial['conta_padrao_financeiro'] = conta_financeira_inicial
            else:
                self.fields['conta_padrao_financeiro'].queryset = ContaBancaria.objects.none()
                self.fields['conta_padrao_eventos'].queryset = ContaBancaria.objects.none()
        

        else:
            # Se não houver ministério, não mostra nenhuma igreja superior nem contas
            self.fields['igreja_superior'].queryset = Igreja.objects.none()
            self.fields['conta_padrao_financeiro'].queryset = ContaBancaria.objects.none()
            self.fields['conta_padrao_eventos'].queryset = ContaBancaria.objects.none()

        # Definir empty_label para igreja_superior
        self.fields['igreja_superior'].empty_label = "Nenhuma (Igreja Sede ou sem vínculo)"
        self.fields['conta_padrao_financeiro'].empty_label = "Nenhuma Conta/Caixa Padrão"
        self.fields['conta_padrao_eventos'].empty_label = "Nenhuma Conta/Caixa Padrão"

    def clean(self):
        cleaned_data = super().clean()
        tipo_igreja = cleaned_data.get('tipo_igreja')
        igreja_superior = cleaned_data.get('igreja_superior')

        # Se o tipo for Sede ou Independente, igreja_superior deve ser None
        if tipo_igreja in ['sede', 'independente']:
            if igreja_superior is not None:
                cleaned_data['igreja_superior'] = None
                # Opcional: self.add_error('igreja_superior', 'Igrejas Sede/Independente não têm Igreja Superior.')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        conta_padrao_financeiro = self.cleaned_data.get('conta_padrao_financeiro')
        instance.conta_padrao_receitas = conta_padrao_financeiro
        instance.conta_padrao_despesas = conta_padrao_financeiro
        instance.conta_padrao_eventos = self.cleaned_data.get('conta_padrao_eventos')
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ProgramacaoPadraoIgrejaForm(forms.ModelForm):
    MESES_ANO_CHOICES = [
        ('', 'Selecione o mês'),
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    ]

    class Meta:
        model = ProgramacaoPadraoIgreja
        fields = [
            'nome',
            'tipo_evento',
            'frequencia',
            'dia_semana',
            'ocorrencia_mensal',
            'mes_ano',
            'intervalo_semanas',
            'hora_inicio',
            'hora_termino',
            'local',
            'descricao',
            'datas_excecao',
            'ativo',
            'ordem',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_evento': forms.Select(attrs={'class': 'form-select'}),
            'frequencia': forms.Select(attrs={'class': 'form-select'}),
            'dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'ocorrencia_mensal': forms.Select(attrs={'class': 'form-select'}),
            'mes_ano': forms.Select(attrs={'class': 'form-select'}),
            'intervalo_semanas': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '8'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_termino': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'datas_excecao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '2026-12-25\n05/01/2027'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        self.igreja = kwargs.pop('igreja', None)
        super().__init__(*args, **kwargs)

        self.bloquear_escola_dominical_programacao = False
        if self.igreja is not None:
            from escola_biblica.models import Turma

            tem_estrutura_ebd = Turma.objects.filter(igreja=self.igreja).exists() or Turma.objects.filter(classe__igreja=self.igreja).exists()
            self.bloquear_escola_dominical_programacao = tem_estrutura_ebd

        self.fields['frequencia'].label = 'Tipo de recorrência'
        self.fields['dia_semana'].label = 'Dia da semana'
        self.fields['ocorrencia_mensal'].label = 'Qual ocorrência no mês?'
        self.fields['mes_ano'].label = 'Em qual mês do ano?'
        self.fields['intervalo_semanas'].label = 'Repetição em semanas'

        if self.bloquear_escola_dominical_programacao:
            self.fields['tipo_evento'].help_text = (
                'Escola Dominical já é gerenciada automaticamente pela aba EBD para esta igreja. '
                'Use outros tipos aqui para evitar duplicidade de eventos.'
            )

        self.fields['mes_ano'].widget.choices = self.MESES_ANO_CHOICES
        self.fields['intervalo_semanas'].widget.attrs['placeholder'] = '1 = toda semana, 2 = quinzenal'
        self.fields['intervalo_semanas'].required = False

    def clean(self):
        cleaned_data = super().clean()
        frequencia = cleaned_data.get('frequencia')
        tipo_evento = cleaned_data.get('tipo_evento')
        ocorrencia = cleaned_data.get('ocorrencia_mensal')
        mes_ano = cleaned_data.get('mes_ano')
        intervalo_semanas = cleaned_data.get('intervalo_semanas')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_termino = cleaned_data.get('hora_termino')

        if self.bloquear_escola_dominical_programacao and tipo_evento == 'escola_dominical':
            self.add_error(
                'tipo_evento',
                'Escola Dominical já é controlada pela aba EBD desta igreja. Para evitar duplicidade, configure por lá.'
            )

        if frequencia == 'mensal_por_ocorrencia' and ocorrencia is None:
            self.add_error('ocorrencia_mensal', 'Selecione a ocorrência mensal para este tipo de agendamento.')

        if frequencia == 'anual_por_ocorrencia':
            if ocorrencia is None:
                self.add_error('ocorrencia_mensal', 'Selecione a ocorrência para recorrência anual.')
            if mes_ano is None:
                self.add_error('mes_ano', 'Selecione o mês para recorrência anual.')

        if frequencia == 'semanal':
            cleaned_data['ocorrencia_mensal'] = None
            cleaned_data['mes_ano'] = None
            cleaned_data['intervalo_semanas'] = intervalo_semanas or 1

        if frequencia == 'mensal_por_ocorrencia':
            cleaned_data['mes_ano'] = None
            cleaned_data['intervalo_semanas'] = 1

        if frequencia == 'anual_por_ocorrencia':
            cleaned_data['intervalo_semanas'] = 1

        if cleaned_data.get('intervalo_semanas') is None:
            cleaned_data['intervalo_semanas'] = 1

        if hora_inicio and hora_termino and hora_termino <= hora_inicio:
            self.add_error('hora_termino', 'A hora de término deve ser maior que a hora de início.')

        return cleaned_data


class DepartamentoMinisterialForm(forms.ModelForm):
    class Meta:
        model = DepartamentoMinisterial
        fields = ['codigo', 'nome', 'ativo', 'ordem']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: MISSOES'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Missões'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        self.ministerio = kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)

    def clean_codigo(self):
        codigo = (self.cleaned_data.get('codigo') or '').strip().upper().replace(' ', '_')
        if not codigo:
            raise ValidationError('Informe um código para o departamento ministerial.')

        if self.ministerio:
            qs = DepartamentoMinisterial.objects.filter(ministerio=self.ministerio, codigo=codigo)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('Já existe um departamento ministerial com este código.')
        return codigo

class DepartamentoForm(forms.ModelForm):
    capacidades = forms.MultipleChoiceField(
        choices=DepartamentoCapacidade.CAPACIDADE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Capacidades operacionais',
        help_text='Capacidades organizam a tela; não concedem permissões de acesso.',
    )

    class Meta:
        model = Departamento
        fields = [
            'codigo_interno',
            'nome_exibicao',
            'tipo_departamento',
            'ordem_exibicao',
            'ativo',
        ]
        widgets = {
            'codigo_interno': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: JOVENS'}),
            'nome_exibicao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Ministerio de Jovens'}),
            'tipo_departamento': forms.Select(attrs={'class': 'form-select'}),
            'ordem_exibicao': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.igreja = kwargs.pop('igreja', None)
        self.permitir_editar_codigo = kwargs.pop('permitir_editar_codigo', True)
        super().__init__(*args, **kwargs)
        if not self.permitir_editar_codigo and 'codigo_interno' in self.fields:
            self.fields['codigo_interno'].disabled = True
        if self.instance.pk:
            self.initial['capacidades'] = list(
                self.instance.capacidades.filter(ativa=True).values_list('capacidade', flat=True)
            )

    def clean_codigo_interno(self):
        codigo = (self.cleaned_data.get('codigo_interno') or '').strip().upper().replace(' ', '_')
        if not codigo:
            raise ValidationError('Informe um código interno para o departamento.')

        qs = Departamento.objects.filter(codigo_interno=codigo)
        if self.igreja:
            qs = qs.filter(igreja=self.igreja)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Já existe um departamento com este código nesta igreja.')
        return codigo

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.igreja and not instance.igreja_id:
            instance.igreja = self.igreja
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class DepartamentoCapacidadesForm(forms.Form):
    capacidades = forms.MultipleChoiceField(
        choices=DepartamentoCapacidade.CAPACIDADE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Capacidades operacionais',
    )


class DepartamentoVinculoForm(forms.Form):
    membro = forms.ModelChoiceField(queryset=None, label='Membro')
    cargo = forms.ModelChoiceField(queryset=None, required=False, label='Cargo (opcional)')
    data_inicio = forms.DateField(
        required=False,
        label='Data de inicio',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    def __init__(self, *args, **kwargs):
        igreja = kwargs.pop('igreja', None)
        super().__init__(*args, **kwargs)
        from secretaria.models import Cargo, Pessoa

        self.fields['membro'].queryset = (
            Pessoa.objects.filter(igreja=igreja).order_by('nome')
            if igreja is not None
            else Pessoa.objects.none()
        )
        self.fields['cargo'].queryset = Cargo.objects.order_by('nome')
        self.fields['membro'].widget.attrs['class'] = 'form-select'
        self.fields['cargo'].widget.attrs['class'] = 'form-select'

# --- FORMULÁRIO PARA EDITAR DADOS DA MINISTÉRIO (PELO ADMIN DA ORG) ---
class MinisterioEditForm(forms.ModelForm):
    """ Formulário para o Admin do Minist. editar dados da própria ministério """
    modelo_carta_recomendacao = forms.ChoiceField(
        required=False,
        label='Modelo da Carta de Recomendacao',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    # Sobrescrever o campo estado para garantir o widget correto se necessário
    # Embora o modelo já tenha choices, definir explicitamente aqui é seguro
    estado = forms.ChoiceField(
        choices=[('', '---------')] + ESTADO_CHOICES, # Adiciona opção vazia
        required=False, # Manter como opcional se no modelo for blank=True, null=True
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Estado (Sede)"
    )

    class Meta:
        model = Ministerio
        fields = ['logo', 'nome_fantasia', 'razao_social', 'cnpj', 'telefone', 'email', 'modelo_carta_recomendacao', 'cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado']
        widgets = {
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'logo': CustomClearableFileInput(attrs={'class': 'form-control form-control-sm', 'id': 'id_logo'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ministerio = self.instance if getattr(self, 'instance', None) and self.instance.pk else None

        filtros_base = {'ativo': True}
        modelos_qs = ModeloCartaRecomendacao.objects.filter(**filtros_base).filter(
            Q(tipo=ModeloCartaRecomendacao.TIPO_PADRAO) |
            Q(tipo=ModeloCartaRecomendacao.TIPO_EXCLUSIVO, ministerio=ministerio)
        ).order_by('ordem', 'nome')

        choices = [(m.codigo, m.nome) for m in modelos_qs]
        if not choices:
            choices = [('padrao', 'Padrao do sistema')]

        valor_atual = getattr(self.instance, 'modelo_carta_recomendacao', '') or 'padrao'
        if valor_atual and valor_atual not in {codigo for codigo, _ in choices}:
            choices.insert(0, (valor_atual, f'{valor_atual} (nao disponivel)'))

        self.fields['modelo_carta_recomendacao'].choices = choices
        self.initial.setdefault('modelo_carta_recomendacao', valor_atual)


class MinisterioLogosForm(forms.ModelForm):
    class Meta:
        model = Ministerio
        fields = [
            'logo_png',
            'logo_pequeno',
            'logo_grande',
            'logo_marketing_extra_1',
            'logo_marketing_extra_2',
        ]
        widgets = {
            'logo_png': CustomClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
            'logo_pequeno': CustomClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
            'logo_grande': CustomClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
            'logo_marketing_extra_1': CustomClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
            'logo_marketing_extra_2': CustomClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
        }


class MinisterioCarteirinhaPoliticaForm(forms.ModelForm):
    class Meta:
        model = Ministerio
        fields = ['carteirinha_permitir_secretaria_local']
        widgets = {
            'carteirinha_permitir_secretaria_local': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'carteirinha_permitir_secretaria_local': 'Permitir que secretarias locais gerem/imprimam carteirinhas',
        }

# Nota: A classe IgrejaEditForm abaixo parece ser uma duplicação de IgrejaForm.
# Se a intenção é ter um formulário de edição com lógica diferente, certifique-se
# de que as diferenças são intencionais. Caso contrário, você pode usar:
# IgrejaEditForm = IgrejaForm
#
# A lógica de filtragem para conta_padrao_receitas e conta_padrao_despesas
# no __init__ de IgrejaEditForm abaixo foi corrigida para usar igreja__ministerio,
# pois ContaBancaria não tem um campo 'ministerio' direto nem 'ativa' ou 'nome_conta'.
# Isso fará com que este formulário permita selecionar contas de QUALQUER igreja
# da mesma ministério, diferente do IgrejaForm acima que filtra pela própria igreja.
class IgrejaEditForm(forms.ModelForm):
     # Definir os campos de logo explicitamente para usar o widget customizado
    logo1 = forms.ImageField(
        widget=CustomClearableFileInput,
        required=False # Mantém como opcional
    )
    logo2 = forms.ImageField(
        widget=CustomClearableFileInput,
        required=False # Mantém como opcional
    )
    conta_padrao_financeiro = forms.ModelChoiceField(
        queryset=ContaBancaria.objects.none(),
        required=False,
        label="Conta/Caixa Padrão Financeiro",
        help_text="Conta/Caixa padrão para receitas e despesas desta igreja.",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    conta_padrao_eventos = forms.ModelChoiceField(
        queryset=ContaBancaria.objects.none(),
        required=False,
        label="Conta/Caixa Padrão para Eventos",
        help_text="Conta/Caixa usada automaticamente nas entradas e saídas de eventos desta igreja.",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
            model = Igreja
            fields = [
                'nome_igreja', 'tipo_igreja', 'igreja_superior', 'data_fundacao',
                'cep', 'rua', 'numero_casa', 'complemento', 'bairro_distrito', 'cidade', 'estado', 'pais',
                'email', 'cnpj', 'telefone', 'celular', 'site',
                'pastor_local', 'pastor_regional',
                'moeda', 'ebd_periodo', 'ebd_dia_semana', 'ebd_horario',
                'ebd_pontos_presente', 'ebd_pontos_biblia', 'ebd_pontos_revista', 'ebd_pontos_oferta', 'ebd_pontos_visitante',
                'observacoes', 'logo1', 'logo2',
                'conta_padrao_financeiro', 'conta_padrao_eventos'
            ]
            widgets = {
                'data_fundacao': forms.DateInput(attrs={'type': 'date'}),
                'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'numero_casa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'bairro_distrito': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'estado': forms.Select(attrs={'class': 'form-select'}),
                'pais': forms.TextInput(attrs={'class': 'form-control'}),
                'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'pastor_local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Pastor/Responsável'}),
                'pastor_regional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'moeda': forms.TextInput(attrs={'class': 'form-control'}),
                'ebd_periodo': forms.Select(attrs={'class': 'form-select'}),
                'ebd_dia_semana': forms.Select(attrs={'class': 'form-select'}),
                'ebd_horario': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
                'ebd_pontos_presente': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
                'ebd_pontos_biblia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
                'ebd_pontos_revista': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
                'ebd_pontos_oferta': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
                'ebd_pontos_visitante': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
                'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
                'logo1': forms.FileInput(attrs={'class': 'form-control'}),
                'logo2': forms.FileInput(attrs={'class': 'form-control'}),
            }

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)

        if ministerio:
            qs_igreja_superior = Igreja.objects.filter(ministerio=ministerio)
            if self.instance and self.instance.pk: # Excluir a própria igreja se estiver editando
              
            
                if self.instance.tipo_igreja in ['sede', 'independente']:
                    self.fields['igreja_superior'].queryset = Igreja.objects.none()
                    self.fields['igreja_superior'].widget.attrs['disabled'] = True
                    self.fields['igreja_superior'].required = False
                    self.initial['igreja_superior'] = None
                else:
                    # Para outros tipos, filtra para não mostrar a própria igreja
                    self.fields['igreja_superior'].queryset = qs_igreja_superior.exclude(pk=self.instance.pk)
            else: # Criando uma nova igreja (embora este seja IgrejaEditForm, pode ser usado para criar)
                self.fields['igreja_superior'].queryset = qs_igreja_superior

            
            # Filtrar contas padrão para mostrar apenas contas de igrejas da mesma ministério
            # O modelo ContaBancaria tem 'igreja', e Igreja tem 'ministerio'.
            # O campo 'nome_identificacao' está em ContaBancaria.
            contas_qs = ContaBancaria.objects.filter(igreja__ministerio=ministerio).order_by('nome_identificacao')
            self.fields['conta_padrao_financeiro'].queryset = contas_qs
            self.fields['conta_padrao_eventos'].queryset = contas_qs

            conta_financeira_inicial = self.instance.conta_padrao_receitas or self.instance.conta_padrao_despesas
            if conta_financeira_inicial and not self.initial.get('conta_padrao_financeiro'):
                self.initial['conta_padrao_financeiro'] = conta_financeira_inicial
        else:
            # Se não houver ministério, esvaziar os querysets ou tratar como erro
            self.fields['igreja_superior'].queryset = Igreja.objects.none()
            self.fields['conta_padrao_financeiro'].queryset = ContaBancaria.objects.none()
            self.fields['conta_padrao_eventos'].queryset = ContaBancaria.objects.none()

        # Adicionar classes CSS do Bootstrap aos campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.widgets.TextInput, forms.widgets.Textarea, forms.widgets.Select, forms.widgets.DateInput, forms.widgets.EmailInput, forms.widgets.URLInput, forms.widgets.NumberInput, forms.widgets.ClearableFileInput)):
                field.widget.attrs.update({'class': 'form-control form-control-sm'})
            elif isinstance(field.widget, forms.widgets.CheckboxInput):
                 field.widget.attrs.update({'class': 'form-check-input'})

                 
    def clean(self):
        cleaned_data = super().clean()
        tipo_igreja = cleaned_data.get('tipo_igreja')
        igreja_superior = cleaned_data.get('igreja_superior')

        # Se o tipo for Sede ou Independente, igreja_superior deve ser None
        if tipo_igreja in ['sede', 'independente']:
            if igreja_superior is not None:
                cleaned_data['igreja_superior'] = None
                # Opcional: self.add_error('igreja_superior', 'Igrejas Sede/Independente não têm Igreja Superior.')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        conta_padrao_financeiro = self.cleaned_data.get('conta_padrao_financeiro')
        instance.conta_padrao_receitas = conta_padrao_financeiro
        instance.conta_padrao_despesas = conta_padrao_financeiro
        instance.conta_padrao_eventos = self.cleaned_data.get('conta_padrao_eventos')
        if commit:
            instance.save()
            self.save_m2m()
        return instance

# Você pode adicionar outros formulários aqui conforme necessário,
# por exemplo, um formulário para editar o PerfilUsuario, etc.

# --- NOVOS FORMULÁRIOS PARA EDITAR PERFIL DO USUÁRIO ---
class UserEditForm(forms.ModelForm):
    """ Formulário para o usuário editar seus dados básicos (User model). """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # self.instance é o objeto User que está sendo editado
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este endereço de e-mail já está em uso por outro usuário.")
        return email
   
class PerfilUsuarioEditForm(forms.ModelForm):
    """ Formulário para o usuário editar seus dados do PerfilUsuario. """
    class Meta:
        model = PerfilUsuario
        fields = ['telefone_contato', 'whatsapp_contato', 'foto_perfil']
        widgets = {
            'telefone_contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
            'whatsapp_contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
            'foto_perfil': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar campos opcionais se eles são blank=True, null=True no modelo
        self.fields['telefone_contato'].required = False
        self.fields['whatsapp_contato'].required = False
        self.fields['foto_perfil'].required = False
# --- FIM NOVOS FORMULÁRIOS ---
