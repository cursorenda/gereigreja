from django import forms
from .models import InteracaoVisitante

class InteracaoVisitanteForm(forms.ModelForm):
    class Meta:
        model = InteracaoVisitante
        fields = ['visitante', 'data_interacao', 'tipo_interacao', 'descricao', 'responsavel']
        widgets = {
            'visitante': forms.Select(attrs={'class': 'form-select'}),
            'data_interacao': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'tipo_interacao': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}),
        }
