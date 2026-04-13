from django import forms
from django.db.models import Q
from django.forms import BaseFormSet, formset_factory
from .models import Aluno, Turma, Frequencia, Licao, Avaliacao, Classe, OfertaClasse, Departamento, DEPARTAMENTOS_SUGERIDOS, TransferenciaAluno


def _get_request_scoped_churches(request):
    if request is None or not getattr(request, 'user', None) or not request.user.is_authenticated:
        return None

    from core.utils import get_igrejas_permitidas, get_request_scoped_churches
    from configuracao.models import Igreja
    from contas.constants import SECRETARIA_EBD, user_has_permission_level_or_higher

    igrejas_permitidas = getattr(request, 'igrejas_permitidas', None)
    if igrejas_permitidas is None:
        perfil = getattr(request.user, 'perfil', None) or getattr(request.user, 'perfil_usuario', None)
        ministerio = getattr(perfil, 'ministerio', None)
        if ministerio:
            igrejas_permitidas = get_igrejas_permitidas(request.user, ministerio)
            if not igrejas_permitidas.exists() and user_has_permission_level_or_higher(request.user, SECRETARIA_EBD):
                igrejas_permitidas = Igreja.objects.filter(ministerio=ministerio)
        else:
            igreja_ativa = getattr(request, 'igreja_ativa', None)
            if igreja_ativa:
                return type(igreja_ativa)._default_manager.filter(pk=igreja_ativa.pk)
            return None

    return get_request_scoped_churches(request, igrejas_permitidas)

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
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        igrejas = _get_request_scoped_churches(request)
        if 'igreja' in self.fields and igrejas is not None:
            self.fields['igreja'].queryset = igrejas.order_by('nome_igreja')
            if igrejas.count() == 1 and not self.instance.pk:
                self.fields['igreja'].initial = igrejas.first()

    class Meta:
        model = Classe
        fields = '__all__'


class AlunoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        igrejas = _get_request_scoped_churches(request)
        if igrejas is not None and 'turma' in self.fields:
            self.fields['turma'].queryset = Turma.objects.filter(
                Q(igreja__in=igrejas) | Q(igreja__isnull=True, membros__igreja__in=igrejas)
            ).distinct().order_by('nome')

    class Meta:
        model = Aluno
        fields = ['nome', 'data_nascimento', 'turma', 'responsavel', 'telefone_responsavel', 'observacoes', 'ativo']

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Filtra membros para mostrar apenas colaboradores com cargos de EBD ativos
        from secretaria.models import MembroCargo
        membros_ebd_ids = MembroCargo.objects.filter(
            cargo__is_ebd=True,
            data_fim__isnull=True
        ).values_list('membro_id', flat=True)
        if 'membros' in self.fields:
            queryset = self.fields['membros'].queryset.filter(chave__in=membros_ebd_ids)
            igrejas = _get_request_scoped_churches(request)
            if igrejas is not None:
                queryset = queryset.filter(igreja__in=igrejas).distinct()
            self.fields['membros'].queryset = queryset.order_by('nome')

        igrejas = _get_request_scoped_churches(request)
        if igrejas is not None:
            if 'igreja' in self.fields:
                self.fields['igreja'].queryset = igrejas.order_by('nome_igreja')
                if igrejas.count() == 1 and not self.instance.pk:
                    self.fields['igreja'].initial = igrejas.first()

            if 'classe' in self.fields:
                self.fields['classe'].queryset = Classe.objects.filter(
                    Q(igreja__in=igrejas) | Q(igreja__isnull=True)
                ).distinct().order_by('nome')

class FrequenciaForm(forms.ModelForm):
    class Meta:
        model = Frequencia
        fields = '__all__'

class LicaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        from secretaria.models import Membro, MembroCargo
        # Filtra membros que possuem cargo EBD ativo
        membros_ebd_ids = MembroCargo.objects.filter(
            cargo__is_ebd=True,
            data_fim__isnull=True
        ).values_list('membro_id', flat=True)
        igrejas = _get_request_scoped_churches(request)
        professores = Membro.objects.filter(chave__in=membros_ebd_ids)
        turmas = Turma.objects.all()
        if igrejas is not None:
            professores = professores.filter(igreja__in=igrejas).distinct()
            turmas = turmas.filter(
                Q(igreja__in=igrejas) | Q(igreja__isnull=True, membros__igreja__in=igrejas)
            ).distinct()

        self.fields['professor'].queryset = professores.order_by('nome')
        if 'turma' in self.fields:
            self.fields['turma'].queryset = turmas.order_by('nome')
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
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        aluno_queryset = Aluno.objects.filter(ativo=True)
        if self.instance.pk and self.instance.aluno_id:
            aluno_queryset = Aluno.objects.filter(Q(ativo=True) | Q(pk=self.instance.aluno_id))

        igrejas = _get_request_scoped_churches(request)
        if igrejas is not None:
            if 'aluno' in self.fields:
                self.fields['aluno'].queryset = aluno_queryset.filter(
                    Q(turma__igreja__in=igrejas) | Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas)
                ).select_related('cadastro', 'turma').distinct().order_by('nome')
            if 'licao' in self.fields:
                self.fields['licao'].queryset = Licao.objects.filter(
                    Q(turma__igreja__in=igrejas) | Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas)
                ).distinct().order_by('-data', 'tema')

        if 'aluno' in self.fields:
            self.fields['aluno'].label_from_instance = lambda obj: f"{obj.cadastro.nome} - {obj.turma}{' (histórico)' if not obj.ativo else ''}"

    def clean(self):
        cleaned_data = super().clean()
        aluno = cleaned_data.get('aluno')
        licao = cleaned_data.get('licao')
        if not aluno or not licao or not aluno.cadastro_id:
            return cleaned_data

        matricula_referencia = aluno.cadastro.get_matricula_referencia(data_referencia=licao.data)
        if matricula_referencia is not None and matricula_referencia.pk != aluno.pk:
            raise forms.ValidationError(
                f'Selecione a matrícula ativa do cadastro para a data da lição. Referência esperada: {matricula_referencia.turma}.'
            )

        return cleaned_data

    class Meta:
        model = Avaliacao
        fields = '__all__'



class OfertaClasseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if 'classe' in self.fields:
            self.fields.pop('classe')

        igrejas = _get_request_scoped_churches(request)
        if igrejas is not None and 'turma' in self.fields:
            self.fields['turma'].queryset = Turma.objects.filter(
                Q(igreja__in=igrejas) | Q(igreja__isnull=True, membros__igreja__in=igrejas)
            ).distinct().order_by('nome')

    class Meta:
        model = OfertaClasse
        fields = ['turma', 'data', 'valor', 'observacao']

class TransferenciaAlunoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        igrejas = _get_request_scoped_churches(request)
        if igrejas is not None:
            if 'aluno' in self.fields:
                self.fields['aluno'].queryset = Aluno.objects.filter(
                    Q(turma__igreja__in=igrejas) | Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas)
                ).distinct().order_by('nome')
            if 'turma_destino' in self.fields:
                self.fields['turma_destino'].queryset = Turma.objects.filter(
                    Q(igreja__in=igrejas) | Q(igreja__isnull=True, membros__igreja__in=igrejas)
                ).distinct().order_by('nome')

    class Meta:
        model = TransferenciaAluno
        fields = ['turma_destino', 'motivo']
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

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        igrejas = _get_request_scoped_churches(request)
        if igrejas is not None:
            self.fields['turma'].queryset = Turma.objects.filter(
                Q(igreja__in=igrejas) | Q(igreja__isnull=True, membros__igreja__in=igrejas)
            ).distinct().order_by('nome')
