from django import forms
from .models import AgendaEvento

class AgendaEventoForm(forms.ModelForm):
	class Meta:
		model = AgendaEvento
		fields = [
			'igreja', 'titulo', 'descricao', 'tipo', 'local', 'responsavel',
			'data_inicio', 'data_fim',
			'recorrente', 'frequencia', 'intervalo', 'dia_semana', 'semana_mes', 'mes_ano', 'data_fim_recorrencia'
		]
		widgets = {
			'igreja': forms.HiddenInput(),
			'data_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
			'data_fim': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
		}

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super().__init__(*args, **kwargs)
		
		# Aplicar classes CSS
		for field_name, field in self.fields.items():
			if field.widget.__class__.__name__ == 'CheckboxInput':
				field.widget.attrs['class'] = 'form-check-input'
			elif field.widget.__class__.__name__ == 'Select':
				field.widget.attrs['class'] = 'form-select'
			elif field.widget.__class__.__name__ == 'Textarea':
				field.widget.attrs['class'] = 'form-control'
				field.widget.attrs['rows'] = 2
			else:
				field.widget.attrs['class'] = 'form-control'
		
		# Preencher igreja automaticamente
		if self.request and hasattr(self.request, 'igreja_ativa') and self.request.igreja_ativa:
			self.fields['igreja'].initial = self.request.igreja_ativa.pk
			self.fields['igreja'].queryset = type(self.request.igreja_ativa)._default_manager.filter(pk=self.request.igreja_ativa.pk)
		
		# Inicializar queryset de responsáveis vazio (será aplicado filtro na view)
		from django.contrib.auth import get_user_model
		User = get_user_model()
		self.fields['responsavel'].queryset = User.objects.none()

	def clean_igreja(self):
		igreja_field = self.cleaned_data.get('igreja')
		if self.request and hasattr(self.request, 'igreja_ativa') and self.request.igreja_ativa:
			return self.request.igreja_ativa
		return igreja_field
