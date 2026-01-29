from django import forms
from django.forms import BaseFormSet, formset_factory
from .models import Aluno, Turma, Frequencia, Licao, Avaliacao, Classe, OfertaClasse, Departamento, DEPARTAMENTOS_SUGERIDOS

# Formulário para chamada de presença em lote
class ChamadaPresencaForm(forms.Form):
    aluno_id = forms.IntegerField(widget=forms.HiddenInput)
    nome = forms.CharField(label='Aluno', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control-plaintext'}))
    presente = forms.BooleanField(label='Presente', required=False, initial=True)
    trouxe_biblia = forms.BooleanField(label='Bíblia', required=False, initial=False)
    trouxe_revista = forms.BooleanField(label='Revista', required=False, initial=False)
    trouxe_visitante = forms.BooleanField(label='Visitante', required=False, initial=False)
    trouxe_oferta = forms.BooleanField(label='Oferta', required=False, initial=False)

ChamadaPresencaFormSet = formset_factory(ChamadaPresencaForm, extra=0)

class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = '__all__'


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = '__all__'

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra membros para mostrar apenas colaboradores com cargos de EBD ativos
        from secretaria.models import MembroCargo
        membros_ebd_ids = MembroCargo.objects.filter(
            cargo__is_ebd=True,
            data_fim__isnull=True
        ).values_list('membro_id', flat=True)
        if 'membros' in self.fields:
            self.fields['membros'].queryset = self.fields['membros'].queryset.filter(chave__in=membros_ebd_ids)

class FrequenciaForm(forms.ModelForm):
    class Meta:
        model = Frequencia
        fields = '__all__'

class LicaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from secretaria.models import Membro, MembroCargo
        # Filtra membros que possuem cargo EBD ativo
        membros_ebd_ids = MembroCargo.objects.filter(
            cargo__is_ebd=True,
            data_fim__isnull=True
        ).values_list('membro_id', flat=True)
        self.fields['professor'].queryset = Membro.objects.filter(chave__in=membros_ebd_ids)
        self.fields['professor'].label_from_instance = lambda obj: f"{obj}"  # Mostra nome completo do membro
    class Meta:
        model = Licao
        fields = ['turma', 'data', 'tema', 'descricao', 'material', 'observacoes', 'horario', 'status', 'professor']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
        }
    def clean_data(self):
        data = self.cleaned_data['data']
        # Garante que o campo data está no formato correto
        if data:
            return data.strftime('%Y-%m-%d')
        return data

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = '__all__'



class OfertaClasseForm(forms.ModelForm):
    class Meta:
        model = OfertaClasse
        fields = '__all__'

# Formulário para transferência de alunos
from .models import TransferenciaAluno

class TransferenciaAlunoForm(forms.ModelForm):
    class Meta:
        model = TransferenciaAluno
        fields = ['aluno', 'turma_destino', 'motivo']
        widgets = {
            'motivo': forms.TextInput(attrs={'placeholder': 'Motivo da transferência (opcional)'}),
        }


# Formulário para Departamento com sugestão de nomes
class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = '__all__'

    def get_suggested_names(self):
        return DEPARTAMENTOS_SUGERIDOS

class GerarCronogramaForm(forms.Form):
    turma = forms.ModelChoiceField(queryset=Turma.objects.all(), required=True)
    data_inicial = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    periodicidade = forms.ChoiceField(choices=[('semanal', 'Semanal'), ('quinzenal', 'Quinzenal'), ('mensal', 'Mensal')], required=True)
    material = forms.CharField(required=False, widget=forms.TextInput())
    observacoes = forms.CharField(widget=forms.Textarea, required=False)
    horario = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    status = forms.ChoiceField(choices=[('ativa', 'Ativa'), ('rascunho', 'Rascunho')], required=True)
    professor = forms.CharField(required=False, widget=forms.TextInput())
