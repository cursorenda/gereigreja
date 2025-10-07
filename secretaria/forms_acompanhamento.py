from django import forms
from .models import AcompanhamentoVisita

class AcompanhamentoVisitaForm(forms.ModelForm):
    class Meta:
        model = AcompanhamentoVisita
        fields = ['tipo_contato', 'resultado', 'observacao']  # Removido 'data'
        widgets = {
            'tipo_contato': forms.Select(attrs={'class': 'form-select'}),
            'resultado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
