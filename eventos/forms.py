
from django import forms
from .models import Evento, ParticipacaoEvento

class EventoForm(forms.ModelForm):
	quantidade_dias = forms.IntegerField(
		min_value=1,
		initial=1,
		label="Quantidade de dias do evento",
		help_text="Informe quantos dias o evento dura. Para eventos de um dia, deixe como 1."
	)
	# clean removido: data_fim agora é sempre calculada automaticamente
	incluir_todos_membros = forms.BooleanField(
		required=False,
		label="Incluir todos os membros",
		help_text="Marque para incluir todos os membros da igreja como participantes esperados deste evento."
	)
	capa = forms.ImageField(required=False, label="Capa do Evento")
	tipos_participantes = forms.ModelMultipleChoiceField(
		queryset=None,
		required=False,
		label="Tipos de Pessoas Esperadas",
		widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
		help_text="Selecione os tipos de pessoas esperadas para este evento."
	)
	status_participantes = forms.ModelMultipleChoiceField(
		queryset=None,
		required=False,
		label="Status de Pessoas Esperadas",
		widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
		help_text="Selecione os status de pessoas esperadas para este evento."
	)
	cargo_participantes = forms.ModelMultipleChoiceField(
		queryset=None,
		required=False,
		label="Cargo de Pessoa Esperada",
		widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
		help_text="Selecione o cargo da pessoa esperada para este evento."
	)

	class Meta:
		model = Evento
		fields = [
			'igreja', 'titulo', 'descricao', 'tipo', 'local', 'responsavel',
			'data_inicio', 'quantidade_dias', 'hora_termino',
			# 'data_fim' removido do formulário do usuário
			'recorrente', 'frequencia', 'intervalo', 'dia_semana', 'semana_mes', 'mes_ano', 'data_fim_recorrencia',
			'capa',
			'tipos_participantes', 'status_participantes', 'cargo_participantes',
			'incluir_todos_membros',
		]
		widgets = {
			'igreja': forms.Select(attrs={'class': 'form-select'}),
			'titulo': forms.TextInput(attrs={'class': 'form-control'}),
			'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
			'tipo': forms.Select(attrs={'class': 'form-select'}),
			'local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Salão, Sala 1, Sala 2'}),
			'responsavel': forms.Select(attrs={'class': 'form-select'}),
			'data_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
			'hora_termino': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
			# 'data_fim' removido do widget do usuário
			'recorrente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
			'frequencia': forms.Select(attrs={'class': 'form-select'}),
			'intervalo': forms.NumberInput(attrs={'class': 'form-control'}),
			'dia_semana': forms.TextInput(attrs={'class': 'form-control'}),
			'semana_mes': forms.TextInput(attrs={'class': 'form-control'}),
			'mes_ano': forms.TextInput(attrs={'class': 'form-control'}),
			'data_fim_recorrencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
			'capa': forms.ClearableFileInput(attrs={'class': 'form-control'}),
		}

	DIAS_SEMANA_CHOICES = [
		("MO", "Segunda-feira"),
		("TU", "Terça-feira"),
		("WE", "Quarta-feira"),
		("TH", "Quinta-feira"),
		("FR", "Sexta-feira"),
		("SA", "Sábado"),
		("SU", "Domingo"),
	]
	dia_semana = forms.MultipleChoiceField(
		required=False,
		label="Dia(s) da Semana",
		choices=DIAS_SEMANA_CHOICES,
		widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
		help_text="Selecione um ou mais dias da semana."
	)

	SEMANAS_MES_CHOICES = [
		("1", "1ª semana"),
		("2", "2ª semana"),
		("3", "3ª semana"),
		("4", "4ª semana"),
		("5", "5ª semana (se houver)"),
		("-1", "Última semana do mês"),
	]
	semana_mes = forms.MultipleChoiceField(
		required=False,
		label="Semana(s) do Mês",
		choices=SEMANAS_MES_CHOICES,
		widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
		help_text="Selecione uma ou mais semanas do mês. '-1' significa a última semana."
	)

	MESES_ANO_CHOICES = [
		("1", "Janeiro"),
		("2", "Fevereiro"),
		("3", "Março"),
		("4", "Abril"),
		("5", "Maio"),
		("6", "Junho"),
		("7", "Julho"),
		("8", "Agosto"),
		("9", "Setembro"),
		("10", "Outubro"),
		("11", "Novembro"),
		("12", "Dezembro"),
	]
	mes_ano = forms.MultipleChoiceField(
		required=False,
		label="Mês(es) do Ano",
		choices=MESES_ANO_CHOICES,
		widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
		help_text="Selecione um ou mais meses do ano."
	)

	def __init__(self, *args, **kwargs):
		# Espera-se que o request seja passado em kwargs
		self.request = kwargs.pop('request', None)
		super().__init__(*args, **kwargs)
		from secretaria.models import TipoPessoa, StatusPessoa, Cargo
		from django.contrib.auth import get_user_model
		from django.utils import timezone
		self.fields['tipos_participantes'].queryset = TipoPessoa.objects.all()
		self.fields['status_participantes'].queryset = StatusPessoa.objects.all()
		self.fields['cargo_participantes'].queryset = Cargo.objects.all()
		self.fields['local'].help_text = 'Informe o ambiente exato (ex: Salão, Sala 1, Sala 2). Eventos em ambientes diferentes podem ocorrer no mesmo horário.'

		# Personaliza o label do campo responsavel para mostrar o nome completo
		if 'responsavel' in self.fields:
			User = get_user_model()
			self.fields['responsavel'].label_from_instance = lambda obj: f"{obj.get_full_name()} ({obj.email})" if obj.get_full_name() else obj.email

		# Se houver request e igreja_ativa, esconde o campo e define o valor inicial
		if self.request and hasattr(self.request, 'igreja_ativa') and self.request.igreja_ativa:
			self.fields['igreja'].initial = self.request.igreja_ativa.pk
			self.fields['igreja'].widget = forms.HiddenInput()
			self.fields['igreja'].queryset = type(self.request.igreja_ativa)._default_manager.filter(pk=self.request.igreja_ativa.pk)

		# Corrigir datas para o formato do input datetime-local, considerando timezone local
		instance = kwargs.get('instance')
		if instance:
			if instance.data_inicio:
				local_inicio = timezone.localtime(instance.data_inicio)
				self.initial['data_inicio'] = local_inicio.strftime('%Y-%m-%dT%H:%M')
			if instance.data_fim:
				local_fim = timezone.localtime(instance.data_fim)
				self.initial['data_fim'] = local_fim.strftime('%Y-%m-%dT%H:%M')

	def clean_igreja(self):
		# Garante que o valor de igreja seja sempre o da igreja_ativa
		igreja_field = self.cleaned_data.get('igreja')
		if self.request and hasattr(self.request, 'igreja_ativa') and self.request.igreja_ativa:
			return self.request.igreja_ativa
		return igreja_field

class ParticipacaoEventoForm(forms.ModelForm):
	class Meta:
		model = ParticipacaoEvento
		fields = [
			'evento', 'membro', 'convidado_nome', 'convidado_email', 'papel', 'status', 'observacoes'
		]

