from django import forms
from .models import VisitaGrupoCasa
from .models import GrupoCasa
from django.utils import timezone
import datetime


class VisitaGrupoCasaForm(forms.ModelForm):
    marcar_todos = forms.BooleanField(required=False, initial=True, label='Marcar todos os membros como visitados')
    # Permitir escolher data e hora da visita (padrão: agora), com widget datetime-local
    data = forms.DateTimeField(required=True, label='Data e Hora da Visita',
                               widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))

    class Meta:
        model = VisitaGrupoCasa
        fields = ['data', 'tipo', 'resultado', 'observacao']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'resultado': forms.TextInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # label amigável
        self.fields['tipo'].label = 'Tipo de contato'
        self.fields['resultado'].label = 'Resultado'
        self.fields['observacao'].label = 'Observação'
        # data label
        self.fields['data'].label = 'Data e Hora da Visita'
        # inicializar campo datetime-local com formato que o widget espera
        try:
            now = timezone.localtime(timezone.now())
            self.fields['data'].initial = now.strftime('%Y-%m-%dT%H:%M')
        except Exception:
            pass

    def save(self, commit=True):
        """Override para aceitar data (date) e gravar um DateTime no modelo (mantendo hora atual)."""
        instancia = super(VisitaGrupoCasaForm, self).save(commit=False)
        # cleaned_data['data'] is a naive datetime parsed from the datetime-local input
        data_dt = self.cleaned_data.get('data')
        if data_dt:
            try:
                # make timezone-aware using current timezone
                data_dt = timezone.make_aware(data_dt, timezone.get_current_timezone())
            except Exception:
                pass
            instancia.data = data_dt
        if commit:
            instancia.save()
        return instancia


class GrupoCasaForm(forms.ModelForm):
    class Meta:
        model = GrupoCasa
        fields = ['nome', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep', 'referencia']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'referencia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # labels em PT-BR
        # Tornar o nome obrigatório no formulário (sem alterar o modelo agora)
        self.fields['nome'].label = 'Nome do Grupo / Responsável'
        self.fields['nome'].required = True
        self.fields['rua'].label = 'Rua'
        self.fields['numero'].label = 'Número'
        self.fields['complemento'].label = 'Complemento'
        self.fields['bairro'].label = 'Bairro'
        self.fields['cidade'].label = 'Cidade'
        self.fields['estado'].label = 'Estado'
        self.fields['cep'].label = 'CEP'
        self.fields['referencia'].label = 'Referência / Observações'
