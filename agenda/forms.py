from django import forms
from .models import AgendaEvento

class AgendaEventoForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
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

	class Meta:
		model = AgendaEvento
		fields = [
			'titulo', 'descricao', 'tipo', 'local', 'responsavel',
			'data_inicio', 'data_fim',
			'recorrente', 'frequencia', 'intervalo', 'dia_semana', 'semana_mes', 'mes_ano', 'data_fim_recorrencia'
		]
		widgets = {
			'data_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
			'data_fim': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
		}
