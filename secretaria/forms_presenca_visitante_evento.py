from django import forms
from .models import PresencaVisitanteEvento, Membro
from eventos.models import Evento
from django.db.models import Q

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
        # Por padrão, mostrar eventos dos próximos dias (>= hoje).
        # Porém, se o formulário estiver recebendo um valor de 'evento' (via POST ou initial),
        # garantir que esse evento específico permaneça disponível no queryset para validação,
        # mesmo que seja anterior a hoje (caso o usuário esteja abrindo um evento passado).
        evento_val = None
        try:
            # Priorizar valor enviado via POST
            if self.request and self.request.method == 'POST':
                evento_val = self.request.POST.get('evento') or self.request.POST.get('evento_id')
            # Caso contrário, verificar initial fornecido
            if not evento_val and 'evento' in self.initial:
                evento_val = self.initial.get('evento')
        except Exception:
            evento_val = None
        if evento_val:
            try:
                evento_pk = int(evento_val)
            except Exception:
                evento_pk = None
            if evento_pk:
                qs = qs.filter(Q(data_inicio__date__gte=hoje) | Q(pk=evento_pk)).order_by('data_inicio')
            else:
                qs = qs.filter(data_inicio__date__gte=hoje).order_by('data_inicio')
        else:
            qs = qs.filter(data_inicio__date__gte=hoje).order_by('data_inicio')
        self.fields['evento'].queryset = qs
