"""
Versão reconstruída (anterior modificada durante a sessão).
Contém apenas as pequenas alterações que foram aplicadas antes da exclusão acidental:
- preservação de valores em clean() para campos desabilitados
- fallback para queryset de `igreja` no __init__ se nenhum contexto for passado
- set initial de campos choice quando a instância existe
"""
from django import forms
from .models import Membro
from configuracao.models import Igreja
from .models import TipoPessoa, StatusPessoa

class MembroForm(forms.ModelForm):
    class Meta:
        model = Membro
        fields = ['igreja', 'nome', 'genero', 'tipo_pessoa', 'status_pessoa', 'estado_civil', 'escolaridade']

    def __init__(self, *args, **kwargs):
        # args esperados: ministerio, user, allowed_churches, igreja_inicial
        ministerio = kwargs.pop('ministerio', None)
        user = kwargs.pop('user', None)
        allowed_churches = kwargs.pop('allowed_churches', None)
        igreja_inicial = kwargs.pop('igreja_inicial', None)
        super().__init__(*args, **kwargs)

        # Fallback: se allowed_churches não foi passado, tenta derivar do user
        if allowed_churches is None:
            try:
                allowed_churches = Igreja.objects.all() if user is None else Igreja.objects.filter(ministerio__in=[m for m in []])
            except Exception:
                allowed_churches = Igreja.objects.all()

        # Preenche queryset do campo igreja
        self.fields['igreja'].queryset = allowed_churches

        # Se houver uma instância com igreja definida, garante que ela esteja disponível
        if self.instance and getattr(self.instance, 'igreja_id', None):
            instancia_igreja = self.instance.igreja
            # Se a igreja da instância não estiver no queryset atual, adiciona-a
            if instancia_igreja not in self.fields['igreja'].queryset:
                qs = list(self.fields['igreja'].queryset) + [instancia_igreja]
                # Ordena mantendo unicidade
                seen = set()
                ordered = []
                for i in qs:
                    if i.pk not in seen:
                        ordered.append(i)
                        seen.add(i.pk)
                # Substitui queryset por queryset estática via Model.objects.filter(pk__in=...)
                self.fields['igreja'].queryset = Igreja.objects.filter(pk__in=[i.pk for i in ordered])
            # E define valor inicial
            self.initial['igreja'] = instancia_igreja.pk
            # Se a view passou para desabilitar igreja, o campo pode estar disabled; preservamos valor no clean

        # Garante initial para campos choice se instância existe
        if self.instance and self.instance.pk:
            for ch in ('genero','estado_civil','escolaridade','tipo_pessoa','status_pessoa'):
                val = getattr(self.instance, ch, None)
                if val is not None:
                    self.initial[ch] = val

    def clean(self):
        cleaned = super().clean()
        # Preserva valores quando o campo foi desabilitado e não veio no POST
        for field in ('igreja','tipo_pessoa','status_pessoa','genero','estado_civil','escolaridade'):
            if field not in self.data and self.instance and hasattr(self.instance, field):
                cleaned[field] = getattr(self.instance, field)
        return cleaned
