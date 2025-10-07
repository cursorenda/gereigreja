from django import forms
from .models import PresencaVisitanteEvento, Membro
from eventos.models import Evento

class PresencaVisitanteEventoForm(forms.ModelForm):
    class Meta:
        model = PresencaVisitanteEvento
        fields = ['membro', 'evento']
        widgets = {
            'membro': forms.Select(attrs={'class': 'form-select'}),
            'evento': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exibe apenas eventos futuros ou do dia
        self.fields['evento'].queryset = Evento.objects.filter(data_inicio__date=forms.DateField().to_python(forms.DateField().widget.value_from_datadict(kwargs.get('data', {}), {}, 'data_inicio'))).order_by('-data_inicio')
