from django import forms
from .models import Visitante

class VisitanteForm(forms.ModelForm):
    class Meta:
        model = Visitante
        fields = [
            'nome', 'apelido', 'telefone', 'email', 'origem',
            'data_primeira_visita', 'status_acompanhamento',
            'observacoes', 'responsavel', 'igreja'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'apelido': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 20}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'origem': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'data_primeira_visita': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status_acompanhamento': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}),
            'igreja': forms.Select(attrs={'class': 'form-select'}),
        }
