from django import forms
from .models import TransferenciaMembro

class TransferenciaMembroForm(forms.ModelForm):
    class Meta:
        model = TransferenciaMembro
        fields = [
            'membro',
            'igreja_origem',
            'igreja_destino',
            'motivo',
            'status',
        ]
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom logic for filtering fields or permissions can be added here
