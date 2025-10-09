from django import forms
from .models import Visitante

class VisitanteForm(forms.ModelForm):
    class Meta:
        model = Visitante
        fields = [
            'nome', 'apelido', 'telefone', 'email', 'origem',
            'status_acompanhamento', 'observacoes', 'responsavel'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'apelido': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 20}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'origem': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'status_acompanhamento': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}),
        }
