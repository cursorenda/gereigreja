
from django import forms
from .models import ConfiguracaoSistema

class ConfiguracaoNotificacoesForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSistema
        fields = [
            'notificar_eventos',
            'notificar_aniversarios',
            'notificar_pre_cadastro_secretario_pastor',
            'notificar_pre_cadastro_admin',
        ]
        widgets = {
            'notificar_eventos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_aniversarios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_pre_cadastro_secretario_pastor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_pre_cadastro_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'notificar_eventos': 'Enviar notificações de eventos?',
            'notificar_aniversarios': 'Enviar notificações de aniversários?',
            'notificar_pre_cadastro_secretario_pastor': 'Notificar Secretário/Pastor Local sobre auto-cadastro?',
            'notificar_pre_cadastro_admin': 'Notificar Admin Ministério sobre auto-cadastro?',
        }

from django import forms
from .models import ConfiguracaoSistema

class ConfiguracaoSistemaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSistema
        fields = [
            'notificar_eventos',
            'notificar_aniversarios',
            'notificar_pre_cadastro_secretario_pastor',
            'notificar_pre_cadastro_admin',
            'ebd_periodo',
            'ebd_dia_semana',
            'ebd_horario',
            'url_biblia_online',
            'url_harpa_crista',
        ]
        widgets = {
            'notificar_eventos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_aniversarios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_pre_cadastro_secretario_pastor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificar_pre_cadastro_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ebd_periodo': forms.Select(attrs={'class': 'form-select'}),
            'ebd_dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'ebd_horario': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'url_biblia_online': forms.URLInput(attrs={'class': 'form-control'}),
            'url_harpa_crista': forms.URLInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'notificar_eventos': 'Enviar notificações de eventos?',
            'notificar_aniversarios': 'Enviar notificações de aniversários?',
            'notificar_pre_cadastro_secretario_pastor': 'Notificar Secretário/Pastor Local sobre auto-cadastro?',
            'notificar_pre_cadastro_admin': 'Notificar Admin Ministério sobre auto-cadastro?',
            'ebd_periodo': 'Período da Escola Bíblica',
            'ebd_dia_semana': 'Dia padrão da EBD',
            'ebd_horario': 'Horário padrão da EBD',
            'url_biblia_online': 'URL — Bíblia Online',
            'url_harpa_crista': 'URL — Harpa Cristã',
        }


class ConfiguracaoEBDForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSistema
        fields = [
            'ebd_periodo',
            'ebd_dia_semana',
            'ebd_horario',
        ]
        widgets = {
            'ebd_periodo': forms.Select(attrs={'class': 'form-select'}),
            'ebd_dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'ebd_horario': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }


class ConfiguracaoPortalForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSistema
        fields = [
            'url_biblia_online',
            'url_harpa_crista',
        ]
        widgets = {
            'url_biblia_online': forms.URLInput(attrs={'class': 'form-control'}),
            'url_harpa_crista': forms.URLInput(attrs={'class': 'form-control'}),
        }
# c:\Gereigreja\configuracao\forms.py
from django import forms
from .models import ESTADO_CHOICES 
from .models import Ministerio, Igreja, PerfilUsuario, Plano, AssinaturaMinisterio, ModeloCartaRecomendacao

from django.contrib.auth.models import User # Modelo de usuário padrão
from financeiro.models import ContaBancaria # Importar ContaBancaria
from django.db import transaction # Para garantir atomicidade no registro
from django.db.models import Q
from django.contrib.auth.models import User # Mantido
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# --- Widget Customizado para Upload de Imagem ---
class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = 'configuracao/widgets/custom_clearable_file_input.html'
    # Você pode customizar os textos padrão se quiser (opcional):
    # initial_text = 'Logo atual:'
    # input_text = 'Alterar:'
    # clear_checkbox_label = 'Remover logo atual'



# --- FORMULÁRIO IGREJA CORRIGIDO E COMPLETO ---
class IgrejaForm(forms.ModelForm):
    """ Formulário para Criar/Editar Igrejas """
    # Definir igreja_superior aqui para filtrar dinamicamente se necessário
    # (A lógica de filtragem no admin.py pode ser adaptada para o __init__ do form)
    igreja_superior = forms.ModelChoiceField(
        queryset=Igreja.objects.none(), # Será filtrado no __init__
        required=False,
        label="Igreja Superior (Sede/Regional)",
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Selecione a Sede ou Regional à qual esta igreja está vinculada (se aplicável)."
    )
    conta_padrao_receitas = forms.ModelChoiceField(
        queryset=ContaBancaria.objects.none(), # Será filtrado no __init__
        required=False,
        label="Conta/Caixa Padrão para Receitas",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    conta_padrao_despesas = forms.ModelChoiceField(
        queryset=ContaBancaria.objects.none(), # Será filtrado no __init__
        required=False,
        label="Conta/Caixa Padrão para Despesas",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Igreja
        # Exclui 'ministerio' pois será definida na view
        exclude = ['ministerio']
        # Listar todos os campos do modelo unificado (exceto ministerio)
        fields = [
            'nome_igreja', 'tipo_igreja', 'igreja_superior', 'data_fundacao',
            'cep', 'rua', 'numero_casa', 'complemento', 'bairro_distrito', 'cidade', 'estado', 'pais',
            'email', 'cnpj', 'telefone', 'celular', 'site', 'conta_padrao_receitas', 'conta_padrao_despesas',
            'pastor_local', 'pastor_regional',
            'moeda', 'observacoes', 'logo1', 'logo2',
        ]
        widgets = {
            'nome_igreja': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_igreja': forms.Select(attrs={'class': 'form-select'}),
            # 'igreja_superior' já definido acima
            'data_fundacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'numero_casa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'bairro_distrito': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'estado': forms.Select(attrs={'class': 'form-select'}), # Modelo já tem choices
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'pastor_local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Pastor/Responsável'}),
            'pastor_regional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'moeda': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
            'logo1': forms.FileInput(attrs={'class': 'form-control'}),
            'logo2': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Pega a ministério passada pela view para filtrar igreja_superior
        ministerio = kwargs.pop('ministerio', None)
        # Pega a instância da igreja (se estiver editando)
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if ministerio:
            qs_igreja_superior = Igreja.objects.filter(ministerio=ministerio)
            
            if instance and instance.pk: # Editando uma igreja existente
                if instance.tipo_igreja in ['sede', 'independente']:
                    self.fields['igreja_superior'].queryset = Igreja.objects.none()
                    self.fields['igreja_superior'].widget.attrs['disabled'] = True
                    self.fields['igreja_superior'].required = False
                    self.initial['igreja_superior'] = None
                else:
                    # Para outros tipos, filtra para não mostrar a própria igreja
                    self.fields['igreja_superior'].queryset = qs_igreja_superior.exclude(pk=instance.pk)
            else: # Criando uma nova igreja
                self.fields['igreja_superior'].queryset = qs_igreja_superior


            # Filtra contas padrão para mostrar apenas as da igreja que está sendo editada/criada
            # Se for uma nova igreja (instance is None), o queryset de contas será vazio,
            # o que é correto, pois a igreja precisa ser salva antes de ter contas.
            if instance:
                self.fields['conta_padrao_receitas'].queryset = ContaBancaria.objects.filter(igreja=instance).order_by('nome_identificacao')
                self.fields['conta_padrao_despesas'].queryset = ContaBancaria.objects.filter(igreja=instance).order_by('nome_identificacao')
            else:
                self.fields['conta_padrao_receitas'].queryset = ContaBancaria.objects.none()
                self.fields['conta_padrao_despesas'].queryset = ContaBancaria.objects.none()
        

        else:
            # Se não houver ministério, não mostra nenhuma igreja superior nem contas
            self.fields['igreja_superior'].queryset = Igreja.objects.none()
            self.fields['conta_padrao_receitas'].queryset = ContaBancaria.objects.none()
            self.fields['conta_padrao_despesas'].queryset = ContaBancaria.objects.none()

        # Definir empty_label para igreja_superior
        self.fields['igreja_superior'].empty_label = "Nenhuma (Igreja Sede ou sem vínculo)"
        self.fields['conta_padrao_receitas'].empty_label = "Nenhuma Conta/Caixa Padrão"
        self.fields['conta_padrao_despesas'].empty_label = "Nenhuma Conta/Caixa Padrão"

    def clean(self):
        cleaned_data = super().clean()
        tipo_igreja = cleaned_data.get('tipo_igreja')
        igreja_superior = cleaned_data.get('igreja_superior')

        # Se o tipo for Sede ou Independente, igreja_superior deve ser None
        if tipo_igreja in ['sede', 'independente']:
            if igreja_superior is not None:
                cleaned_data['igreja_superior'] = None
                # Opcional: self.add_error('igreja_superior', 'Igrejas Sede/Independente não têm Igreja Superior.')
        return cleaned_data

# --- FORMULÁRIO PARA EDITAR DADOS DA MINISTÉRIO (PELO ADMIN DA ORG) ---
class MinisterioEditForm(forms.ModelForm):
    """ Formulário para o Admin do Minist. editar dados da própria ministério """
    modelo_carta_recomendacao = forms.ChoiceField(
        required=False,
        label='Modelo da Carta de Recomendacao',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    # Sobrescrever o campo estado para garantir o widget correto se necessário
    # Embora o modelo já tenha choices, definir explicitamente aqui é seguro
    estado = forms.ChoiceField(
        choices=[('', '---------')] + ESTADO_CHOICES, # Adiciona opção vazia
        required=False, # Manter como opcional se no modelo for blank=True, null=True
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Estado (Sede)"
    )

    class Meta:
        model = Ministerio
        fields = ['logo', 'nome_fantasia', 'razao_social', 'cnpj', 'telefone', 'email', 'modelo_carta_recomendacao', 'cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado']
        widgets = {
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'logo': CustomClearableFileInput(attrs={'class': 'form-control form-control-sm', 'id': 'id_logo'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ministerio = self.instance if getattr(self, 'instance', None) and self.instance.pk else None

        filtros_base = {'ativo': True}
        modelos_qs = ModeloCartaRecomendacao.objects.filter(**filtros_base).filter(
            Q(tipo=ModeloCartaRecomendacao.TIPO_PADRAO) |
            Q(tipo=ModeloCartaRecomendacao.TIPO_EXCLUSIVO, ministerio=ministerio)
        ).order_by('ordem', 'nome')

        choices = [(m.codigo, m.nome) for m in modelos_qs]
        if not choices:
            choices = [('padrao', 'Padrao do sistema')]

        valor_atual = getattr(self.instance, 'modelo_carta_recomendacao', '') or 'padrao'
        if valor_atual and valor_atual not in {codigo for codigo, _ in choices}:
            choices.insert(0, (valor_atual, f'{valor_atual} (nao disponivel)'))

        self.fields['modelo_carta_recomendacao'].choices = choices
        self.initial.setdefault('modelo_carta_recomendacao', valor_atual)

# Nota: A classe IgrejaEditForm abaixo parece ser uma duplicação de IgrejaForm.
# Se a intenção é ter um formulário de edição com lógica diferente, certifique-se
# de que as diferenças são intencionais. Caso contrário, você pode usar:
# IgrejaEditForm = IgrejaForm
#
# A lógica de filtragem para conta_padrao_receitas e conta_padrao_despesas
# no __init__ de IgrejaEditForm abaixo foi corrigida para usar igreja__ministerio,
# pois ContaBancaria não tem um campo 'ministerio' direto nem 'ativa' ou 'nome_conta'.
# Isso fará com que este formulário permita selecionar contas de QUALQUER igreja
# da mesma ministério, diferente do IgrejaForm acima que filtra pela própria igreja.
class IgrejaEditForm(forms.ModelForm):
     # Definir os campos de logo explicitamente para usar o widget customizado
    logo1 = forms.ImageField(
        widget=CustomClearableFileInput,
        required=False # Mantém como opcional
    )
    logo2 = forms.ImageField(
        widget=CustomClearableFileInput,
        required=False # Mantém como opcional
    )
    class Meta:
            model = Igreja
            fields = [
                'nome_igreja', 'tipo_igreja', 'igreja_superior', 'data_fundacao',
                'cep', 'rua', 'numero_casa', 'complemento', 'bairro_distrito', 'cidade', 'estado', 'pais',
                'email', 'cnpj', 'telefone', 'celular', 'site',
                'pastor_local', 'pastor_regional',
                'moeda', 'observacoes', 'logo1', 'logo2',
                'conta_padrao_receitas', 'conta_padrao_despesas'
            ]
            widgets = {
                'data_fundacao': forms.DateInput(attrs={'type': 'date'}),
                'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'numero_casa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'bairro_distrito': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'estado': forms.Select(attrs={'class': 'form-select'}),
                'pais': forms.TextInput(attrs={'class': 'form-control'}),
                'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'pastor_local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Pastor/Responsável'}),
                'pastor_regional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
                'moeda': forms.TextInput(attrs={'class': 'form-control'}),
                'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
                'logo1': forms.FileInput(attrs={'class': 'form-control'}),
                'logo2': forms.FileInput(attrs={'class': 'form-control'}),
            }

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        super().__init__(*args, **kwargs)

        if ministerio:
            qs_igreja_superior = Igreja.objects.filter(ministerio=ministerio)
            if self.instance and self.instance.pk: # Excluir a própria igreja se estiver editando
              
            
                if self.instance.tipo_igreja in ['sede', 'independente']:
                    self.fields['igreja_superior'].queryset = Igreja.objects.none()
                    self.fields['igreja_superior'].widget.attrs['disabled'] = True
                    self.fields['igreja_superior'].required = False
                    self.initial['igreja_superior'] = None
                else:
                    # Para outros tipos, filtra para não mostrar a própria igreja
                    self.fields['igreja_superior'].queryset = qs_igreja_superior.exclude(pk=self.instance.pk)
            else: # Criando uma nova igreja (embora este seja IgrejaEditForm, pode ser usado para criar)
                self.fields['igreja_superior'].queryset = qs_igreja_superior

            
            # Filtrar contas padrão para mostrar apenas contas de igrejas da mesma ministério
            # O modelo ContaBancaria tem 'igreja', e Igreja tem 'ministerio'.
            # O campo 'nome_identificacao' está em ContaBancaria.
            self.fields['conta_padrao_receitas'].queryset = ContaBancaria.objects.filter(igreja__ministerio=ministerio).order_by('nome_identificacao')
            self.fields['conta_padrao_despesas'].queryset = ContaBancaria.objects.filter(igreja__ministerio=ministerio).order_by('nome_identificacao')
        else:
            # Se não houver ministério, esvaziar os querysets ou tratar como erro
            self.fields['igreja_superior'].queryset = Igreja.objects.none()
            self.fields['conta_padrao_receitas'].queryset = ContaBancaria.objects.none()
            self.fields['conta_padrao_despesas'].queryset = ContaBancaria.objects.none()

        # Adicionar classes CSS do Bootstrap aos campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.widgets.TextInput, forms.widgets.Textarea, forms.widgets.Select, forms.widgets.DateInput, forms.widgets.EmailInput, forms.widgets.URLInput, forms.widgets.NumberInput, forms.widgets.ClearableFileInput)):
                field.widget.attrs.update({'class': 'form-control form-control-sm'})
            elif isinstance(field.widget, forms.widgets.CheckboxInput):
                 field.widget.attrs.update({'class': 'form-check-input'})

                 
    def clean(self):
        cleaned_data = super().clean()
        tipo_igreja = cleaned_data.get('tipo_igreja')
        igreja_superior = cleaned_data.get('igreja_superior')

        # Se o tipo for Sede ou Independente, igreja_superior deve ser None
        if tipo_igreja in ['sede', 'independente']:
            if igreja_superior is not None:
                cleaned_data['igreja_superior'] = None
                # Opcional: self.add_error('igreja_superior', 'Igrejas Sede/Independente não têm Igreja Superior.')
        return cleaned_data    

# Você pode adicionar outros formulários aqui conforme necessário,
# por exemplo, um formulário para editar o PerfilUsuario, etc.

# --- NOVOS FORMULÁRIOS PARA EDITAR PERFIL DO USUÁRIO ---
class UserEditForm(forms.ModelForm):
    """ Formulário para o usuário editar seus dados básicos (User model). """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # self.instance é o objeto User que está sendo editado
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este endereço de e-mail já está em uso por outro usuário.")
        return email
   
class PerfilUsuarioEditForm(forms.ModelForm):
    """ Formulário para o usuário editar seus dados do PerfilUsuario. """
    class Meta:
        model = PerfilUsuario
        fields = ['telefone_contato', 'whatsapp_contato', 'foto_perfil']
        widgets = {
            'telefone_contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
            'whatsapp_contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
            'foto_perfil': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar campos opcionais se eles são blank=True, null=True no modelo
        self.fields['telefone_contato'].required = False
        self.fields['whatsapp_contato'].required = False
        self.fields['foto_perfil'].required = False
# --- FIM NOVOS FORMULÁRIOS ---
