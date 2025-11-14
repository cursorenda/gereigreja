from django import forms
from .models import AcompanhamentoVisita

class AcompanhamentoVisitaForm(forms.ModelForm):
    data = forms.DateTimeField(
        label='Data da Visita',
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        required=True,
    )

    class Meta:
        model = AcompanhamentoVisita
        fields = ['data', 'tipo_contato', 'resultado', 'observacao']
        widgets = {
            'tipo_contato': forms.Select(attrs={'class': 'form-select'}),
            'resultado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils import timezone
        if not self.initial.get('data'):
            self.initial['data'] = timezone.now().replace(second=0, microsecond=0).isoformat(timespec='minutes')
