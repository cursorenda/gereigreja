from django import forms
from .models import MembroCargo, Membro, Cargo

class MembroCargoForm(forms.ModelForm):
    # Apenas UI: alterar rótulo visível de 'Membro' para 'Pessoa' (nome do campo e valores preservados)
    membro = forms.ModelChoiceField(queryset=Membro.objects.all(), label="Pessoa")
    cargo = forms.ModelChoiceField(queryset=Cargo.objects.all(), label="Cargo")
    data_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Data de início")
    data_fim = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Data de término", required=False)

    class Meta:
        model = MembroCargo
        fields = ["membro", "cargo", "data_inicio", "data_fim"]
