
from django import forms
from django.contrib.auth import get_user_model
from .models import Evento, ParticipacaoEvento

User = get_user_model()

class EventoForm(forms.ModelForm):
	EVENTOS_NAO_CORRIQUEIROS_CHOICES = [
		('festa', 'Festa'),
		('cruzada', 'Cruzada'),
		('encontro', 'Encontro'),
	]

	# Campo responsável customizado para permitir controle do queryset
	responsavel = forms.ModelChoiceField(
		queryset=User.objects.none(),  # Inicializado vazio, será populado no __init__
		required=False,
		label="Responsável",
		widget=forms.Select(attrs={'class': 'form-select'}),
		help_text="Usuário responsável pelo evento (deve ser membro da igreja)"
	)
	
	# Nota: queryset será definido no __init__ após importar Membro
	convidados = forms.ModelMultipleChoiceField(
		queryset=None,  # Será definido no __init__ (precisa importar Membro primeiro)
		required=False,
		label="Convidados (membros/visitantes)",
		widget=forms.SelectMultiple(attrs={'class': 'form-select select2', 'data-placeholder': 'Digite para buscar e selecione...'}),
		help_text="Busque e selecione os convidados para este evento."
	)
	quantidade_dias = forms.IntegerField(
		min_value=1,
		initial=1,
		label="Quantidade de dias do evento",
		help_text="Informe quantos dias o evento dura. Para eventos de um dia, deixe como 1."
	)
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

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super().__init__(*args, **kwargs)
		from secretaria.models import TipoPessoa, StatusPessoa, Cargo, Membro
		from django.contrib.auth import get_user_model
		from django.utils import timezone
		from configuracao.models import Igreja
		
		User = get_user_model()
		
		# Inicializar querysets (filtro de responsáveis aplicado na view)
		self.fields['responsavel'].queryset = User.objects.none()
		self.fields['convidados'].queryset = Membro.objects.all()
		
		self.fields['tipos_participantes'].queryset = TipoPessoa.objects.all()
		self.fields['status_participantes'].queryset = StatusPessoa.objects.all()
		self.fields['local'].help_text = 'Informe o ambiente exato (ex: Salão, Sala 1, Sala 2). Eventos em ambientes diferentes podem ocorrer no mesmo horário.'
		
		# ====================================================================
		
		# Padroniza o campo igreja igual ao cadastro de membro
		if 'igreja' in self.fields:
			self.fields['igreja'].label_from_instance = lambda obj: obj.nome_igreja
			self.fields['igreja'].widget = forms.Select(attrs={'class': 'form-select'})
			self.fields['igreja'].empty_label = "Selecione a igreja"

	def clean(self):
		cleaned_data = super().clean()
		frequencia = cleaned_data.get('frequencia', 'nenhuma')
		
		# Se não for recorrente, limpar campos de recorrência
		if frequencia in ['nenhuma', '', None]:
			cleaned_data['dia_semana'] = ''
			cleaned_data['semana_mes'] = ''
			cleaned_data['mes_ano'] = ''
		else:
			# Apenas converter listas para string se frequência for diferente de 'nenhuma'
			for field in ["dia_semana", "semana_mes", "mes_ano"]:
				value = cleaned_data.get(field)
				if isinstance(value, list):
					cleaned_data[field] = ",".join(value)
				elif value is None:
					cleaned_data[field] = ''
		
		return cleaned_data
	
	def clean_dia_semana(self):
		"""Validação customizada para evitar erro quando campo vazio"""
		frequencia = self.data.get('frequencia', 'nenhuma')
		if frequencia in ['nenhuma', '', None]:
			return []  # Retornar lista vazia se não for recorrente
		
		value = self.cleaned_data.get('dia_semana', [])
		# Se for string vazia, retornar lista vazia
		if value == '' or value == ['']:
			return []
		return value
	
	def clean_semana_mes(self):
		"""Validação customizada para evitar erro quando campo vazio"""
		frequencia = self.data.get('frequencia', 'nenhuma')
		if frequencia in ['nenhuma', '', None]:
			return []
		
		value = self.cleaned_data.get('semana_mes', [])
		if value == '' or value == ['']:
			return []
		return value
	
	def clean_mes_ano(self):
		"""Validação customizada para evitar erro quando campo vazio"""
		frequencia = self.data.get('frequencia', 'nenhuma')
		if frequencia in ['nenhuma', '', None]:
			return []
		
		value = self.cleaned_data.get('mes_ano', [])
		if value == '' or value == ['']:
			return []
		return value

	class Meta:
		model = Evento
		fields = [
			'igreja', 'titulo', 'descricao', 'tipo', 'local', 'responsavel',
			'status_operacional', 'meta_publico', 'meta_arrecadacao', 'observacoes_internas',
			'conta_bancaria_evento',
			'data_inicio', 'quantidade_dias', 'hora_termino',
			# 'data_fim' removido do formulário do usuário
			'recorrente', 'frequencia', 'intervalo', 'dia_semana', 'semana_mes', 'mes_ano', 'data_fim_recorrencia',
			'capa',
			'tipos_participantes', 'status_participantes',
			'incluir_todos_membros',
		]
		widgets = {
			'igreja': forms.Select(attrs={'class': 'form-select'}),
			'titulo': forms.TextInput(attrs={'class': 'form-control'}),
			'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
			'tipo': forms.Select(attrs={'class': 'form-select'}),
			'local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Salão, Sala 1, Sala 2'}),
			'status_operacional': forms.Select(attrs={'class': 'form-select'}),
			'meta_publico': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
			'meta_arrecadacao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
			'observacoes_internas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
			'conta_bancaria_evento': forms.Select(attrs={'class': 'form-select'}),
			# 'responsavel' removido - definido como campo da classe
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
		self.somente_eventos_individuais = kwargs.pop('somente_eventos_individuais', False)
		super().__init__(*args, **kwargs)
		from financeiro.models import ContaBancaria
		from secretaria.models import TipoPessoa, StatusPessoa, Cargo
		from django.contrib.auth import get_user_model
		from django.utils import timezone
		self.fields['tipos_participantes'].queryset = TipoPessoa.objects.all()
		self.fields['status_participantes'].queryset = StatusPessoa.objects.all()
	# Removido: cargo_participantes não existe mais no modelo Evento
		self.fields['local'].help_text = 'Informe o ambiente exato (ex: Salão, Sala 1, Sala 2). Eventos em ambientes diferentes podem ocorrer no mesmo horário.'

		# Convidados: todos membros ativos e visitantes
		from secretaria.models import Membro
		self.fields['convidados'].queryset = Membro.objects.all().order_by('nome')
		self.fields['convidados'].widget.attrs['style'] = 'width: 100%'

		# Se edição, preencher convidados já vinculados
		instance = kwargs.get('instance')
		if instance and instance.pk:
			self.fields['convidados'].initial = instance.participacoes.values_list('membro', flat=True)

		# Personaliza o label do campo responsavel para mostrar o nome completo
		if 'responsavel' in self.fields:
			User = get_user_model()
			self.fields['responsavel'].label_from_instance = lambda obj: f"{obj.get_full_name()} ({obj.email})" if obj.get_full_name() else obj.email

		from configuracao.models import Igreja
		# Determina o ministério ativo. Se estivermos editando um evento que já tem
		# uma igreja associada, usamos o ministério dessa igreja para filtrar as
		# opções — assim a igreja salva sempre estará presente no queryset.
		ministerio_ativo = None
		instance = kwargs.get('instance')
		if instance and getattr(instance, 'igreja', None):
			ministerio_ativo = getattr(instance.igreja, 'ministerio', None)
		elif self.request and hasattr(self.request, 'igreja_ativa') and self.request.igreja_ativa:
			ministerio_ativo = getattr(self.request.igreja_ativa, 'ministerio', None)
		elif self.request and hasattr(self.request.user, 'perfil') and hasattr(self.request.user.perfil, 'ministerio'):
			ministerio_ativo = self.request.user.perfil.ministerio
		# Filtra igrejas do ministério ativo
		igrejas_queryset = Igreja.objects.none()
		if ministerio_ativo:
			igrejas_queryset = Igreja.objects.filter(ministerio=ministerio_ativo)
		# Se for edição, preferir a igreja já salva como inicial (garante que apareça)
		if instance and getattr(instance, 'igreja', None):
			self.fields['igreja'].initial = instance.igreja.pk
		# Caso não seja edição, se houver igreja ativa na request, usar como inicial
		elif self.request and hasattr(self.request, 'igreja_ativa') and self.request.igreja_ativa:
			self.fields['igreja'].initial = self.request.igreja_ativa.pk
		self.fields['igreja'].queryset = igrejas_queryset
		# Exibe apenas o nome da igreja no select
		if 'igreja' in self.fields:
			self.fields['igreja'].label_from_instance = lambda obj: obj.nome_igreja

		if 'conta_bancaria_evento' in self.fields:
			contas_qs = ContaBancaria.objects.none()
			if instance and getattr(instance, 'igreja', None):
				contas_qs = ContaBancaria.objects.filter(igreja=instance.igreja).order_by('nome_identificacao')
			elif self.request and hasattr(self.request, 'igreja_ativa') and self.request.igreja_ativa:
				contas_qs = ContaBancaria.objects.filter(igreja=self.request.igreja_ativa).order_by('nome_identificacao')
			elif ministerio_ativo:
				contas_qs = ContaBancaria.objects.filter(igreja__ministerio=ministerio_ativo).order_by('igreja__nome_igreja', 'nome_identificacao')
			self.fields['conta_bancaria_evento'].queryset = contas_qs
			self.fields['conta_bancaria_evento'].empty_label = 'Selecione o caixa/conta do evento (opcional)'

		if self.somente_eventos_individuais:
			self.fields['tipo'].choices = self.EVENTOS_NAO_CORRIQUEIROS_CHOICES
			self.fields['tipo'].help_text = 'Para Novo Evento, use apenas tipos não corriqueiros.'
			if 'recorrente' in self.fields:
				self.fields['recorrente'].initial = False
			for field_name, initial in [
				('frequencia', 'nenhuma'),
				('intervalo', 1),
				('dia_semana', []),
				('semana_mes', []),
				('mes_ano', []),
				('data_fim_recorrencia', None),
			]:
				if field_name in self.fields:
					self.fields[field_name].required = False
					self.fields[field_name].initial = initial
					self.fields[field_name].widget = forms.HiddenInput()

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
		# Permite que o valor submetido pelo formulário seja respeitado. Se nenhum
		# valor for enviado, como fallback retornamos a igreja ativa da request (se houver).
		igreja_field = self.cleaned_data.get('igreja')
		if igreja_field:
			return igreja_field
		if self.request and hasattr(self.request, 'igreja_ativa') and self.request.igreja_ativa:
			return self.request.igreja_ativa
		return igreja_field

	def clean(self):
		cleaned_data = super().clean()
		igreja = cleaned_data.get('igreja')
		conta_bancaria_evento = cleaned_data.get('conta_bancaria_evento')
		if igreja and conta_bancaria_evento and conta_bancaria_evento.igreja_id != igreja.id:
			self.add_error('conta_bancaria_evento', 'Selecione uma conta/caixa da mesma igreja do evento.')

		if self.somente_eventos_individuais:
			tipo = cleaned_data.get('tipo')
			tipos_permitidos = {codigo for codigo, _ in self.EVENTOS_NAO_CORRIQUEIROS_CHOICES}
			if tipo not in tipos_permitidos:
				self.add_error('tipo', 'No fluxo de Novo Evento, use apenas Festa, Cruzada ou Encontro.')
			cleaned_data['recorrente'] = False
			cleaned_data['frequencia'] = 'nenhuma'
			cleaned_data['intervalo'] = 1
			cleaned_data['dia_semana'] = ''
			cleaned_data['semana_mes'] = ''
			cleaned_data['mes_ano'] = ''
			cleaned_data['data_fim_recorrencia'] = None

		return cleaned_data

class ParticipacaoEventoForm(forms.ModelForm):
	class Meta:
		model = ParticipacaoEvento
		fields = [
			'evento', 'membro', 'convidado_nome', 'convidado_email', 'papel', 'status', 'observacoes'
		]


