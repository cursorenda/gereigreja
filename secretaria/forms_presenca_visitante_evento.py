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
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Exibe apenas eventos futuros ou do dia, e da igreja ativa
        qs = Evento.objects.all()
        if self.request and hasattr(self.request, 'igreja_ativa') and self.request.igreja_ativa:
            qs = qs.filter(igreja=self.request.igreja_ativa)
        from django.utils import timezone
        hoje = timezone.localdate()
        qs = qs.filter(data_inicio__date__gte=hoje).order_by('data_inicio')
        self.fields['evento'].queryset = qs
