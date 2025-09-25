
from django import forms
from django.forms import BaseFormSet, formset_factory
from .models import Aluno, Turma, Frequencia, Licao, Avaliacao, Classe, OfertaClasse, Departamento, DEPARTAMENTOS_SUGERIDOS

# Formulário para chamada de presença em lote
class ChamadaPresencaForm(forms.Form):
    aluno_id = forms.IntegerField(widget=forms.HiddenInput)
    nome = forms.CharField(label='Aluno', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control-plaintext'}))
    presente = forms.BooleanField(label='Presente', required=False, initial=True)

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

class FrequenciaForm(forms.ModelForm):
    class Meta:
        model = Frequencia
        fields = '__all__'

class LicaoForm(forms.ModelForm):
    class Meta:
        model = Licao
        fields = '__all__'

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
