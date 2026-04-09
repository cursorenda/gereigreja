from django import forms
from django.core.exceptions import ValidationError

from configuracao.models import Igreja

from .models import Membro, TransferenciaMembro


class TransferenciaMembroForm(forms.ModelForm):
    class Meta:
        model = TransferenciaMembro
        fields = ['membro', 'igreja_destino', 'motivo', 'observacao']
        widgets = {
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, membro=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.membro_forcado = membro

        self.fields['membro'].queryset = Membro.objects.select_related('igreja').order_by('nome')
        self.fields['membro'].widget.attrs.update({'class': 'form-select'})
        self.fields['igreja_destino'].queryset = Igreja.objects.none()
        self.fields['igreja_destino'].widget.attrs.update({'class': 'form-select'})

        if membro is not None:
            self.fields['membro'].queryset = Membro.objects.filter(pk=membro.pk)
            self.fields['membro'].initial = membro.pk
            self.fields['membro'].required = False
            self.fields['membro'].disabled = True
            self.fields['igreja_destino'].queryset = Igreja.objects.filter(
                ministerio=membro.igreja.ministerio
            ).exclude(pk=membro.igreja_id).order_by('nome_igreja')

    def clean(self):
        cleaned_data = super().clean()

        membro = self.membro_forcado or cleaned_data.get('membro')
        igreja_destino = cleaned_data.get('igreja_destino')

        if not membro:
            raise ValidationError('Selecione o membro para transferência.')

        if not igreja_destino:
            raise ValidationError('Selecione a igreja de destino.')

        if membro.igreja_id == igreja_destino.id:
            raise ValidationError('A igreja de destino deve ser diferente da igreja atual do membro.')

        if membro.igreja.ministerio_id != igreja_destino.ministerio_id:
            raise ValidationError('A transferência só pode ocorrer entre igrejas do mesmo ministério.')

        if TransferenciaMembro.objects.filter(
            membro=membro,
            status=TransferenciaMembro.STATUS_AGUARDANDO,
        ).exists():
            raise ValidationError('Já existe uma transferência pendente para este membro.')

        cleaned_data['membro'] = membro
        return cleaned_data
