# --- IMPORTS NECESSÁRIOS PARA O FORMULÁRIO DE ALTERAÇÃO EM MASSA ---
from django import forms
from .models import StatusPessoa, TipoPessoa, Tag, Cargo
# --- Formulário para Alteração em Massa de Pessoas ---
class PessoaBulkEditForm(forms.Form):
    # Campos de endereço para edição em massa
    bairro_distrito = forms.CharField(
        required=False,
        label='Bairro/Distrito',
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50})
    )
    cidade = forms.CharField(
        required=False,
        label='Cidade',
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50})
    )
    estado = forms.CharField(
        required=False,
        label='Estado',
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50})
    )
    pais = forms.CharField(
        required=False,
        label='País',
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50})
    )
    cep = forms.CharField(
        required=False,
        label='CEP',
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 9, 'placeholder': '00000-000'})
    )
    status_pessoa = forms.ModelChoiceField(
        queryset=StatusPessoa.objects.all(),
        required=False,
        label='Status',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tipo_pessoa = forms.ModelChoiceField(
        queryset=TipoPessoa.objects.exclude(nome__iexact='obreiro').order_by('nome'),
        required=False,
        label='Tipo de Pessoa',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('nome'),
        required=False,
        label='Tags',
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6})
    )

    data_mudanca_tipo = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Data da mudança de tipo'
    )
    data_mudanca_status = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Data da mudança de status'
    )
    sub_status_inativo = forms.ChoiceField(
        choices=[
            ('', '---------'),
            ('FALECIDO', 'Falecido'),
            ('MUDOU', 'Mudou (outro ministério ou denominação)'),
            ('TRANSFERIDO', 'Transferido (outra congregação do mesmo ministério)'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Sub status (se inativo)'
    )
    observacoes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Observações'
    )

# --- IMPORTS ADICIONAIS ---
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Membro, Pessoa
from .models import MembroCargo, TipoPessoa, StatusPessoa, StatusHistorico, Cargo
from django.contrib.auth.models import Group
from configuracao.models import PerfilUsuario, Igreja, Ministerio
from configuracao.services_assinatura import contar_pessoas_ativas, ministerio_pode_adicionar_pessoa_ativa, obter_limite_pessoas_ativas
# --- IMPORTAR UTILS DE PERMISSÃO ---
from .utils import is_admin_org, get_allowed_churches_for_membros
from .models import Tag
import re
import unicodedata


# --- FUNÇÕES DE VALIDAÇÃO ---
def validar_cpf(cpf):
    """
    Valida CPF brasileiro usando algoritmo de dígito verificador.
    Aceita CPF com ou sem pontuação.
    """
    # Remove pontuação
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        raise ValidationError('CPF deve ter 11 dígitos.')
    
    # Verifica se todos os dígitos são iguais (CPF inválido)
    if cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido (todos os dígitos iguais).')
    
    # Valida primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[9]):
        raise ValidationError('CPF inválido (primeiro dígito verificador incorreto).')
    
    # Valida segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[10]):
        raise ValidationError('CPF inválido (segundo dígito verificador incorreto).')
    
    return cpf  # Retorna CPF apenas com números



class AssociarUsuarioMembroForm(forms.Form):
    membro_id = forms.IntegerField(widget=forms.HiddenInput)
    usuario = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        required=True,
        label="Usuário do Sistema",
        widget=forms.Select(attrs={'class': 'form-select usuario-autocomplete'})
    )
    sugestao_usuario_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        membro = kwargs.pop('membro', None)
        super().__init__(*args, **kwargs)
        User = get_user_model()
        usuarios_disponiveis = User.objects.filter(
            membro_secretaria__isnull=True,
            is_active=True,
            is_superuser=False,
            is_staff=False,
            perfil__isnull=False
        ).distinct()
        if membro and membro.igreja and hasattr(membro.igreja, 'ministerio'):
            ministerio = membro.igreja.ministerio
            igreja = membro.igreja
            usuarios_disponiveis = usuarios_disponiveis.filter(
                perfil__ministerio=ministerio,
                perfil__igrejas_permitidas=igreja
            ).distinct()
        self.fields['usuario'].queryset = usuarios_disponiveis
        self.fields['usuario'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.email})"
        if membro:
            self.fields['membro_id'].initial = membro.pk
            sugestao = usuarios_disponiveis.filter(email__iexact=membro.email).first() if membro.email else None
            if sugestao:
                self.fields['usuario'].initial = sugestao.pk
                self.fields['sugestao_usuario_id'].initial = sugestao.pk
                self.fields['usuario'].widget.attrs['data-sugestao'] = '1'
            else:
                self.fields['usuario'].widget.attrs['data-sugestao'] = '0'


class GerenciarOcupantesForm(forms.Form):
    ocupantes = forms.ModelMultipleChoiceField(
        queryset=Membro.objects.all().order_by('nome'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 12}),
        required=False,
        label='Ocupantes do Cargo',
        # Apenas UI: trocar o texto para usar 'pessoas' em vez de 'membros'
        help_text='Selecione as pessoas que ocuparão este cargo.'
    )


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['nome', 'grupo_permissao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100, 'placeholder': 'Nome do cargo'}),
            'grupo_permissao': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].label = 'Nome do Cargo'
        self.fields['grupo_permissao'].label = 'Grupo de Permissão (opcional)'
        self.fields['grupo_permissao'].required = False



# --- MembroForm unificado ---
class MembroForm(forms.ModelForm):
    PREMIUM_ETAPAS_HEADER = '[Cadastro Premium - Etapas]'
    PREMIUM_ETAPAS_FOOTER = '[/Cadastro Premium - Etapas]'
    PREMIUM_ETAPAS_LABELS = {
        'data_batismo': 'Data do Batismo',
        'numero_credencial': 'N. da Credencial',
        'data_consagracao': 'Data da Consagracao',
        'convencao': 'Convencao',
        'observacoes_ministeriais': 'Observacoes Ministeriais',
    }
    PREMIUM_ETAPAS_LABEL_TO_KEY = {
        'data do batismo': 'data_batismo',
        'n. da credencial': 'numero_credencial',
        'data da consagracao': 'data_consagracao',
        'convencao': 'convencao',
        'observacoes ministeriais': 'observacoes_ministeriais',
    }

    # DEBUG: Mostra igrejas disponíveis e igreja do membro (mover para __init__ se necessário)
    sub_status_inativo = forms.ChoiceField(
        choices=[
            ('', '---------'),
            ('FALECIDO', 'Falecido'),
            ('MUDOU', 'Mudou (outro ministério ou denominação)'),
            ('TRANSFERIDO', 'Transferido (outra congregação do mesmo ministério)'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Sub status (se inativo)',
        help_text='Preencha apenas se o status for inativo.'
    )
    # Campos para data customizada de mudança de tipo/status
    data_mudanca_tipo = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Data da mudança de tipo',
        help_text='Data em que a mudança de tipo ocorreu (se diferente de hoje).'
    )
    data_mudanca_status = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Data da mudança de status',
        help_text='Data em que a mudança de status ocorreu (se diferente de hoje).'
    )
    genero = forms.ChoiceField(
        choices=[('M', 'Masculino'), ('F', 'Feminino')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    estado_civil = forms.ChoiceField(
        choices=[('Solteiro', 'Solteiro'), ('Casado', 'Casado'), ('Divorciado', 'Divorciado'), ('Amasiado', 'Amasiado'), ('Viuvo', 'Viuvo')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    escolaridade = forms.ChoiceField(
        choices=[('Ensino Fundamental Incompleto', 'Ensino Fundamental Incompleto'), ('Ensino Fundamental Completo', 'Ensino Fundamental Completo'), ('Ensino Médio Incompleto', 'Ensino Médio Incompleto'), ('Ensino Médio Completo', 'Ensino Médio Completo'), ('Ensino Superior Incompleto', 'Ensino Superior Incompleto'), ('Ensino Superior Completo', 'Ensino Superior Completo'), ('Pós-graduação', 'Pós-graduação'), ('Mestrado', 'Mestrado'), ('Sem Escolaridade', 'Sem Escolaridade'), ('Doutorado', 'Doutorado')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
        # self.fields['status_pessoa'].required = False
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('nome'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
        label='Tags',
        help_text='Segure Ctrl para selecionar múltiplas tags'
    )
    data_batismo = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Data do Batismo'
    )
    numero_credencial = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numero da credencial'}),
        label='Numero da Credencial'
    )
    data_consagracao = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Data da Consagracao'
    )
    convencao = forms.CharField(
        required=False,
        max_length=120,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Convencao / jurisdicao'}),
        label='Convencao'
    )
    observacoes_ministeriais = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observacoes ministeriais'}),
        label='Observacoes Ministeriais'
    )

    @classmethod
    def extract_premium_etapas_metadata(cls, observacoes_text):
        parsed = {
            'data_batismo': '',
            'numero_credencial': '',
            'data_consagracao': '',
            'convencao': '',
            'observacoes_ministeriais': '',
        }
        if not observacoes_text:
            return parsed

        lines = str(observacoes_text).splitlines()
        in_block = False
        for raw_line in lines:
            line = (raw_line or '').strip()
            if not in_block:
                if line == cls.PREMIUM_ETAPAS_HEADER:
                    in_block = True
                continue

            if line == cls.PREMIUM_ETAPAS_FOOTER:
                break

            # Suporta bloco legado sem rodape: interrompe ao entrar em outro marcador.
            if line.startswith('[') and line.endswith(']') and line != cls.PREMIUM_ETAPAS_HEADER:
                break

            if ':' not in line:
                continue

            label, value = line.split(':', 1)
            key = cls.PREMIUM_ETAPAS_LABEL_TO_KEY.get(label.strip().lower())
            if key:
                parsed[key] = value.strip()

        return parsed

    @classmethod
    def upsert_premium_etapas_metadata(cls, observacoes_text, metadata):
        current_text = str(observacoes_text or '')
        lines = current_text.splitlines()
        cleaned_lines = []
        i = 0
        while i < len(lines):
            line = (lines[i] or '').strip()
            if line == cls.PREMIUM_ETAPAS_HEADER:
                i += 1
                while i < len(lines):
                    inner = (lines[i] or '').strip()
                    if inner == cls.PREMIUM_ETAPAS_FOOTER:
                        i += 1
                        break
                    if inner.startswith('[') and inner.endswith(']') and inner != cls.PREMIUM_ETAPAS_HEADER:
                        break
                    i += 1
                continue
            cleaned_lines.append(lines[i])
            i += 1

        base_text = '\n'.join(cleaned_lines).strip()
        block_lines = []
        for key, label in cls.PREMIUM_ETAPAS_LABELS.items():
            value = metadata.get(key) if metadata else None
            if value in (None, ''):
                continue
            block_lines.append(f'{label}: {value}')

        if not block_lines:
            return base_text

        premium_block = '\n'.join(
            [cls.PREMIUM_ETAPAS_HEADER] + block_lines + [cls.PREMIUM_ETAPAS_FOOTER]
        )
        if base_text:
            return f'{base_text}\n\n{premium_block}'
        return premium_block

    class Meta:
        model = Pessoa
        fields = [
            'igreja',
            'nome', 'apelido', 'cpf', 'rg', 'naturalidade', 'nascimento', 'genero', 'tipo_pessoa', 'status_pessoa',
            'sub_status_inativo',
            'grau_eclesiastico',
            'estado_civil', 'profissao', 'escolaridade', 'nome_pai', 'nome_mae', 'cep', 'pais', 'estado', 'nacionalidade',
            'cidade', 'bairro_distrito', 'rua', 'numero_casa', 'complemento', 'telefone', 'celular',
            'data_entrada', 'conjuge', 'data_casamento',
            'foto', 'email',
            'tipo_entrada',
            'data_primeira_visita', 'origem_visita', 'responsavel_acompanhamento', 'status_acompanhamento', 'observacoes_visita',
            'tags'
        ]
        widgets = {
                'observacoes_visita': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'style': 'height:30px; min-height:30px; max-height:30px; resize:none;'}),
            }

    def __init__(self, *args, **kwargs):
        auto_cadastro = kwargs.pop('auto_cadastro', False)
        ministerio = kwargs.pop('ministerio', None)
        user = kwargs.pop('user', None)
        allowed_churches = kwargs.pop('allowed_churches', None)
        igreja_inicial = kwargs.pop('igreja_inicial', None)
        super().__init__(*args, **kwargs)
        self.ministerio = ministerio
        if auto_cadastro:
            self.fields.pop('igreja', None)
            self.fields.pop('tipo_pessoa', None)
            self.fields.pop('status_pessoa', None)
            # Evita KeyError: retorna imediatamente se campos removidos
            return
        # Widgets/classes
        for field_name in self.fields:
            if isinstance(self.fields[field_name], (forms.ChoiceField, forms.ModelChoiceField)):
                self.fields[field_name].widget.attrs.setdefault('class', 'form-select')
            else:
                self.fields[field_name].widget.attrs.setdefault('class', 'form-control')
        # Querysets dinâmicos
        # Placeholders para campos de contato
        if 'telefone' in self.fields:
            self.fields['telefone'].widget.attrs['placeholder'] = '(99) 9999-9999'
        if 'celular' in self.fields:
            self.fields['celular'].widget.attrs['placeholder'] = '(99) 99999-9999'
        if 'email' in self.fields:
            self.fields['email'].widget.attrs['placeholder'] = 'email@exemplo.com'
        if 'nome' in self.fields:
            self.fields['nome'].label = 'Nome Completo'
        if 'tags' in self.fields:
            self.fields['tags'].queryset = Tag.objects.all().order_by('nome')
        if 'tipo_pessoa' in self.fields:
            self.fields['tipo_pessoa'].queryset = TipoPessoa.objects.exclude(nome__iexact='obreiro').order_by('nome')
        if 'status_pessoa' in self.fields:
            self.fields['status_pessoa'].queryset = StatusPessoa.objects.filter(nome__in=["Ativo", "Desligado", "Em Disciplina", "Inativo"]).order_by('nome')
        if 'grau_eclesiastico' in self.fields:
            self.fields['grau_eclesiastico'].required = False
            self.fields['grau_eclesiastico'].initial = self.instance.grau_eclesiastico if getattr(self.instance, 'pk', None) else 'membro_comum'
        # Preenche o queryset do campo igreja conforme o perfil do usuário
        import logging
        logger = logging.getLogger("django")
        if 'igreja' in self.fields:
            if user:
                if is_admin_org(user):
                    ministerio = getattr(user.perfil, 'ministerio', None) if hasattr(user, 'perfil') else None
                    if ministerio:
                        self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')
                    else:
                        self.fields['igreja'].queryset = Igreja.objects.none()
                    logger.info(f"[MembroForm] Usuário admin. Igrejas disponíveis: {[i.nome_igreja for i in self.fields['igreja'].queryset]}")
                elif allowed_churches is not None:
                    self.fields['igreja'].queryset = allowed_churches
                    logger.info(f"[MembroForm] Igrejas permitidas para usuário comum: {[i.nome_igreja for i in self.fields['igreja'].queryset]}")
                else:
                    self.fields['igreja'].queryset = Igreja.objects.none()
                    logger.info(f"[MembroForm] Nenhuma igreja disponível para usuário comum.")
            elif ministerio:
                self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')
                logger.info(f"[MembroForm] Igrejas do ministério (sem usuário): {[i.nome_igreja for i in self.fields['igreja'].queryset]}")
        if 'igreja' in self.fields:
            logger.info(f"[MembroForm] igreja_inicial: {igreja_inicial}")
            logger.info(f"[MembroForm] queryset final igreja: {[i.nome_igreja for i in self.fields['igreja'].queryset]}")
            # Garante que igreja_inicial sempre esteja no queryset
            if igreja_inicial and not self.fields['igreja'].queryset.filter(pk=igreja_inicial.pk).exists():
                from django.db.models import Q
                self.fields['igreja'].queryset = Igreja.objects.filter(
                    Q(pk=igreja_inicial.pk) | Q(pk__in=self.fields['igreja'].queryset.values_list('pk', flat=True))
                )
            # Seleciona igreja_inicial se fornecida
            if igreja_inicial:
                self.initial['igreja'] = igreja_inicial.pk
                self.fields['igreja'].initial = igreja_inicial.pk
        # Garante que a igreja do membro sempre apareça no select durante edição
        if self.instance and self.instance.pk and getattr(self.instance, 'igreja', None):
            igreja_membro = self.instance.igreja
            if igreja_membro and not self.fields['igreja'].queryset.filter(pk=igreja_membro.pk).exists():
                from django.db.models import Q
                self.fields['igreja'].queryset = Igreja.objects.filter(
                    Q(pk=igreja_membro.pk) | Q(pk__in=self.fields['igreja'].queryset.values_list('pk', flat=True))
                )
        # Só desabilita o campo igreja no cadastro (GET sem instance)
        if not args or (len(args) > 0 and not args[0]):  # GET
            if not self.instance or not self.instance.pk:
                self.fields['igreja'].disabled = True

        if self.instance and self.instance.pk and not self.is_bound:
            premium_data = self.extract_premium_etapas_metadata(getattr(self.instance, 'observacoes_visita', ''))
            for key, value in premium_data.items():
                if key in self.fields and value and key not in self.initial:
                    self.initial[key] = value

    def clean_cpf(self):
        """Valida CPF se fornecido."""
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            try:
                # Remove pontuação e valida
                cpf_limpo = validar_cpf(cpf)
                # Formata para armazenar com pontuação
                return f'{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}'
            except ValidationError as e:
                raise ValidationError(e.message)
        return cpf


    @staticmethod
    def _smart_title_token(token):
        """Aplica capitalização inteligente preservando hífen e apóstrofo."""
        token = (token or '').strip()
        if not token:
            return ''

        for sep in ('-', "'"):
            if sep in token:
                return sep.join(MembroForm._smart_title_token(part) for part in token.split(sep))

        return token[:1].upper() + token[1:].lower()


    @staticmethod
    def _normalize_person_name(value):
        """Normaliza espaços e aplica formatação profissional para nomes."""
        if not value:
            return value

        value = unicodedata.normalize('NFC', str(value).strip())
        value = re.sub(r'\s+', ' ', value)
        if not value:
            return value

        lower_particles = {'da', 'de', 'do', 'das', 'dos', 'e'}
        tokens = value.split(' ')
        normalized_tokens = []

        for idx, token in enumerate(tokens):
            token_clean = token.strip()
            if not token_clean:
                continue
            token_lower = token_clean.lower()

            if idx > 0 and token_lower in lower_particles:
                normalized_tokens.append(token_lower)
            else:
                normalized_tokens.append(MembroForm._smart_title_token(token_lower))

        return ' '.join(normalized_tokens)
    
    def clean_email(self):
        """Valida formato de email."""
        email = self.cleaned_data.get('email')
        if email:
            # Django já valida EmailField, mas vamos ser mais rigorosos
            email = email.strip().lower()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError('Email inválido. Use o formato: nome@exemplo.com')
        return email

    def clean_nome(self):
        """Padroniza o nome completo sem remover acentos."""
        nome = self.cleaned_data.get('nome')
        nome = self._normalize_person_name(nome)
        if nome and len(nome) < 3:
            raise ValidationError('Informe um nome completo valido com pelo menos 3 caracteres.')
        return nome

    def clean_apelido(self):
        """Padroniza apelido para manter consistência visual."""
        apelido = self.cleaned_data.get('apelido')
        if not apelido:
            return apelido
        return self._normalize_person_name(apelido)
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_pessoa = cleaned_data.get('tipo_pessoa')
        tipo_entrada = cleaned_data.get('tipo_entrada')
        grau_eclesiastico = cleaned_data.get('grau_eclesiastico')
        status_pessoa = cleaned_data.get('status_pessoa')
        sub_status_inativo = cleaned_data.get('sub_status_inativo')
        if tipo_pessoa and hasattr(tipo_pessoa, 'nome') and tipo_pessoa.nome.lower() == 'membro':
            if not tipo_entrada:
                self.add_error('tipo_entrada', 'Informe o tipo de entrada para pessoas com tipo "Membro".')
            if not grau_eclesiastico:
                cleaned_data['grau_eclesiastico'] = 'membro_comum'
        else:
            cleaned_data['tipo_entrada'] = None
            cleaned_data['grau_eclesiastico'] = None

        # Validação do sub status
        if status_pessoa and hasattr(status_pessoa, 'nome') and status_pessoa.nome.strip().lower() == 'inativo':
            if not sub_status_inativo:
                self.add_error('sub_status_inativo', 'Preencha o sub status quando o status for Inativo.')
            elif sub_status_inativo not in ['FALECIDO', 'MUDOU', 'TRANSFERIDO']:
                self.add_error('sub_status_inativo', 'Escolha um sub status válido: Falecido, Mudou ou Transferido.')

        status_destino_ativo = bool(
            status_pessoa and hasattr(status_pessoa, 'nome') and status_pessoa.nome.strip().lower() == 'ativo'
        )
        status_atual_ativo = bool(
            self.instance and self.instance.pk and self.instance.status_pessoa and
            getattr(self.instance.status_pessoa, 'nome', '').strip().lower() == 'ativo'
        )
        if self.ministerio and status_destino_ativo and not status_atual_ativo:
            if not ministerio_pode_adicionar_pessoa_ativa(self.ministerio):
                limite = obter_limite_pessoas_ativas(self.ministerio)
                total_ativos = contar_pessoas_ativas(self.ministerio)
                self.add_error(
                    'status_pessoa',
                    f'Limite de pessoas ativas do plano atingido ({total_ativos}/{limite}). Faça upgrade para ativar mais pessoas.'
                )

        tipo_nome = (getattr(tipo_pessoa, 'nome', '') or '').strip().lower()
        grau = cleaned_data.get('grau_eclesiastico')
        if tipo_nome != 'membro':
            cleaned_data['data_batismo'] = None
            cleaned_data['numero_credencial'] = ''
            cleaned_data['data_consagracao'] = None
            cleaned_data['convencao'] = ''
            cleaned_data['observacoes_ministeriais'] = ''
        elif grau == 'membro_comum':
            cleaned_data['numero_credencial'] = ''
            cleaned_data['data_consagracao'] = None
            cleaned_data['convencao'] = ''
            cleaned_data['observacoes_ministeriais'] = ''

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
            tags = self.cleaned_data.get('tags')
            if tags is not None:
                instance.tags.set(tags)
        return instance


class StatusHistoricoManualForm(forms.ModelForm):
    data_transicao = forms.DateTimeField(
        label="Data e Hora da Transição",
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        help_text="Data e hora em que a mudança de tipo/status efetivamente ocorreu."
    )

    class Meta:
        model = StatusHistorico
        fields = [
            'membro',
            'tipo_pessoa_anterior', 'tipo_pessoa_novo',
            'status_pessoa_anterior', 'status_pessoa_novo',
            'data_transicao', 'observacao'
        ]
        widgets = {
            'membro': forms.Select(attrs={'class': 'form-select'}),
            'tipo_pessoa_anterior': forms.Select(attrs={'class': 'form-select'}),
            'tipo_pessoa_novo': forms.Select(attrs={'class': 'form-select'}),
            'status_pessoa_anterior': forms.Select(attrs={'class': 'form-select'}),
            'status_pessoa_novo': forms.Select(attrs={'class': 'form-select'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detalhes sobre a mudança, motivo, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        membro_inicial = kwargs.pop('membro_inicial', None)
        super().__init__(*args, **kwargs)
        if ministerio:
            self.fields['membro'].queryset = Membro.objects.filter(igreja__ministerio=ministerio).order_by('nome')
        else:
            self.fields['membro'].queryset = Membro.objects.none()

        self.fields['tipo_pessoa_anterior'].queryset = TipoPessoa.objects.all().order_by('nome')
        self.fields['tipo_pessoa_novo'].queryset = TipoPessoa.objects.all().order_by('nome')
        self.fields['status_pessoa_anterior'].queryset = StatusPessoa.objects.all().order_by('nome')
        self.fields['status_pessoa_novo'].queryset = StatusPessoa.objects.all().order_by('nome')

        for field_name in ['tipo_pessoa_anterior', 'tipo_pessoa_novo', 'status_pessoa_anterior', 'status_pessoa_novo']:
            self.fields[field_name].required = False
            self.fields[field_name].empty_label = "Nenhum / Não Alterado"

        if membro_inicial:
            self.initial['membro'] = membro_inicial
            self.fields['membro'].disabled = True
        # Apenas UI: garantir que o rótulo exibido para o campo 'membro' seja 'Pessoa'
        try:
            if 'membro' in self.fields:
                self.fields['membro'].label = 'Pessoa'
        except Exception:
            # não interrompe a inicialização do formulário em caso de comportamento inesperado
            pass


class MembroUserManagementForm(forms.Form):
    email_usuario = forms.EmailField(
        label="E-mail do Usuário (Login)",
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        help_text="Este é o e-mail da pessoa. Será usado como login do usuário."
    )
    is_active = forms.BooleanField(
        label="Usuário Ativo?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Se desmarcado, o usuário não poderá fazer login."
    )
    is_staff = forms.BooleanField(
        label="Acesso ao Painel Administrativo?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Permite ao usuário acessar as áreas administrativas do sistema."
    )

    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Papéis/Grupos do Usuário",
        help_text="Selecione os papéis que este usuário terá no sistema."
    )

    igrejas_permitidas = forms.ModelMultipleChoiceField(
        queryset=Igreja.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Igrejas com Acesso Permitido",
        help_text="Selecione as igrejas que este usuário poderá gerenciar/visualizar."
    )

    def __init__(self, *args, **kwargs):
        self.membro_instance = kwargs.pop('membro_instance', None)
        self.ministerio = kwargs.pop('ministerio', None)
        self.user_instance = kwargs.pop('user_instance', None)
        self.perfil_instance = kwargs.pop('perfil_instance', None)
        super().__init__(*args, **kwargs)

        self.fields['grupos'].queryset = Group.objects.all().order_by('name')
        if self.ministerio:
            self.fields['igrejas_permitidas'].queryset = Igreja.objects.filter(ministerio=self.ministerio).order_by('nome_igreja')
        else:
            self.fields['igrejas_permitidas'].queryset = Igreja.objects.none()

        if self.user_instance:
            self.fields['email_usuario'].initial = self.user_instance.email
            self.fields['is_active'].initial = self.user_instance.is_active
            self.fields['is_staff'].initial = self.user_instance.is_staff
            self.fields['grupos'].initial = self.user_instance.groups.all()
            if self.perfil_instance:
                self.fields['igrejas_permitidas'].initial = self.perfil_instance.igrejas_permitidas.all()
        elif self.membro_instance:
            self.fields['email_usuario'].initial = self.membro_instance.email
            self.fields['is_active'].initial = True
            self.fields['is_staff'].initial = False

        if self.user_instance:
            self.fields['email_usuario'].widget.attrs['readonly'] = 'readonly'

    def clean_email_usuario(self):
        return self.membro_instance.email

from django import forms
from django.contrib.auth import get_user_model
from .models import Membro

# --- BLOCO ANTIGO DE ASSOCIARUSUARIOMEMBROFORM (NÃO UTILIZAR MAIS) ---
# class AssociarUsuarioMembroForm(forms.Form):
#     membro_id = forms.IntegerField(widget=forms.HiddenInput)
#     usuario = forms.ModelChoiceField(
#         queryset=get_user_model().objects.none(),
#         required=True,
#         label="Usuário do Sistema",
#         widget=forms.Select(attrs={'class': 'form-select usuario-autocomplete'})
#     )
#     sugestao_usuario_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
#
#     def __init__(self, *args, **kwargs):
#         membro = kwargs.pop('membro', None)
#         super().__init__(*args, **kwargs)
#         User = get_user_model()
#         # Só permite usuários não associados a membros
#         usuarios_disponiveis = User.objects.filter(membro_secretaria__isnull=True)
#         self.fields['usuario'].queryset = usuarios_disponiveis
#         self.fields['usuario'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.email})"
#         if membro:
#             self.fields['membro_id'].initial = membro.pk
#             # Sugestão automática: usuário com mesmo e-mail
#             sugestao = usuarios_disponiveis.filter(email__iexact=membro.email).first() if membro.email else None
#             if sugestao:
#                 self.fields['usuario'].initial = sugestao.pk
#                 self.fields['sugestao_usuario_id'].initial = sugestao.pk
#                 self.fields['usuario'].widget.attrs['data-sugestao'] = '1'
#             else:
#                 self.fields['usuario'].widget.attrs['data-sugestao'] = '0'
# Formulário para gerenciar ocupantes de um cargo
from .models import MembroCargo, Membro

class GerenciarOcupantesForm(forms.Form):
    ocupantes = forms.ModelMultipleChoiceField(
        queryset=Membro.objects.all().order_by('nome'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 12}),
        required=False,
        label='Ocupantes do Cargo',
        help_text='Selecione os membros que ocuparão este cargo.'
    )
from django.contrib.auth.models import Group

# Novo formulário para cadastro/edição de cargos (novo modelo)
from .models import Cargo
class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['nome', 'grupo_permissao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100, 'placeholder': 'Nome do cargo'}),
            'grupo_permissao': forms.Select(attrs={'class': 'form-select'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].label = 'Nome do Cargo'
        self.fields['grupo_permissao'].label = 'Grupo de Permissão (opcional)'
        self.fields['grupo_permissao'].required = False
from .models import Membro, TipoPessoa, StatusPessoa, StatusHistorico # Adicionado StatusHistorico
from django.contrib.auth.models import User, Group # Importar User e Group
from configuracao.models import PerfilUsuario # Importar PerfilUsuario
from configuracao.models import Igreja, Ministerio # Importar Igreja e Ministerio
# --- IMPORTAR UTILS DE PERMISSÃO ---
from .utils import is_admin_org, get_allowed_churches_for_membros # Para verificar se o usuário é admin do ministério e igrejas permitidas



# Ensure MembroForm consumes view-specific kwargs (ministerio, user, allowed_churches, igreja_inicial)
# This is a safety wrapper: if a MembroForm class exists (there are duplicated fragments
# in this file) we wrap its __init__ so extra kwargs are popped and don't reach
# BaseModelForm.__init__, preventing the TypeError observed in the views.
if 'MembroForm' in globals():
    _mf = globals()['MembroForm']
    _orig_init = getattr(_mf, '__init__', None)

    def _membro_init(self, *args, _orig_init=_orig_init, _mf=_mf, **kwargs):
        ministerio = kwargs.pop('ministerio', None)
        user = kwargs.pop('user', None)
        allowed_churches = kwargs.pop('allowed_churches', None)
        igreja_inicial = kwargs.pop('igreja_inicial', None)

        # Call the original __init__ (if present) with remaining kwargs
        if _orig_init:
            _orig_init(self, *args, **kwargs)
        else:
            # fallback to default ModelForm init
            super(_mf, self).__init__(*args, **kwargs)

        # Apply minimal post-init adjustments expected by views
        try:
            if 'igreja' in getattr(self, 'fields', {}):
                try:
                    if user and callable(globals().get('is_admin_org')) and not is_admin_org(user) and allowed_churches is not None:
                        self.fields['igreja'].queryset = allowed_churches
                    elif ministerio:
                        self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')
                    else:
                        self.fields['igreja'].queryset = Igreja.objects.none()
                except Exception:
                    # degrade gracefully
                    try:
                        self.fields['igreja'].queryset = Igreja.objects.none()
                    except Exception:
                        pass

                if igreja_inicial and getattr(self.fields['igreja'].queryset, 'filter', None):
                    try:
                        if self.fields['igreja'].queryset.filter(pk=igreja_inicial.pk).exists():
                            self.initial.setdefault('igreja', igreja_inicial)
                            self.fields['igreja'].disabled = True
                    except Exception:
                        pass

            if 'tipo_pessoa' in getattr(self, 'fields', {}):
                try:
                    self.fields['tipo_pessoa'].queryset = TipoPessoa.objects.exclude(nome__iexact='obreiro').order_by('nome')
                except Exception:
                    pass
            if 'status_pessoa' in getattr(self, 'fields', {}):
                try:
                    self.fields['status_pessoa'].queryset = StatusPessoa.objects.all().order_by('nome')
                except Exception:
                    pass
            if 'foto' in getattr(self, 'fields', {}):
                try:
                    self.fields['foto'].widget.template_name = 'secretaria/widgets/custom_clearable_file_input.html'
                except Exception:
                    pass
        except Exception:
            pass

    # Replace the __init__ on the MembroForm class with the wrapper
    try:
        _mf.__init__ = _membro_init
    except Exception:
        # do not fail import if monkey-patch cannot be applied
        pass


    # --- Canonical fallback MembroForm ---
    # The file contains duplicated fragments which can leave a MembroForm without a
    # proper Meta or consistent __init__. Append a canonical, minimal MembroForm and
    # set it as the module's MembroForm to ensure runtime callers receive a stable
    # class that consumes the view-specific kwargs (ministerio, user, allowed_churches, igreja_inicial).
    try:
        class _CanonicalMembroForm(forms.ModelForm):
            class Meta:
                model = Membro
                fields = [
                    'igreja', 'nome', 'apelido', 'cpf', 'rg', 'naturalidade', 'nascimento', 'genero',
                    'tipo_pessoa', 'status_pessoa', 'estado_civil', 'profissao', 'escolaridade',
                    'nome_pai', 'nome_mae', 'cep', 'pais', 'estado', 'nacionalidade', 'cidade',
                    'bairro_distrito', 'rua', 'numero_casa', 'complemento', 'telefone', 'data_entrada',
                    'conjuge', 'data_casamento', 'foto', 'email', 'tipo_entrada', 'data_primeira_visita',
                    'origem_visita', 'responsavel_acompanhamento', 'status_acompanhamento', 'observacoes_visita'
                ]

            def __init__(self, *args, **kwargs):
                # consume view-specific kwargs so BaseModelForm.__init__ doesn't error
                ministerio = kwargs.pop('ministerio', None)
                user = kwargs.pop('user', None)
                allowed_churches = kwargs.pop('allowed_churches', None)
                igreja_inicial = kwargs.pop('igreja_inicial', None)
                super().__init__(*args, **kwargs)

                # set sensible widget classes
                for fname, field in self.fields.items():
                    try:
                        if isinstance(field, (forms.ChoiceField, forms.ModelChoiceField)):
                            field.widget.attrs.setdefault('class', 'form-select')
                        else:
                            field.widget.attrs.setdefault('class', 'form-control')
                    except Exception:
                        pass

                # populate model choice querysets safely
                try:
                    if 'igreja' in self.fields:
                        if user and callable(globals().get('is_admin_org')) and not is_admin_org(user) and allowed_churches is not None:
                            self.fields['igreja'].queryset = allowed_churches
                        elif ministerio:
                            self.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')
                        else:
                            self.fields['igreja'].queryset = Igreja.objects.none()
                        if igreja_inicial and getattr(self.fields['igreja'].queryset, 'filter', None):
                            try:
                                if self.fields['igreja'].queryset.filter(pk=igreja_inicial.pk).exists():
                                    self.initial.setdefault('igreja', igreja_inicial)
                                    self.fields['igreja'].disabled = True
                            except Exception:
                                pass
                    if 'tipo_pessoa' in self.fields:
                        self.fields['tipo_pessoa'].queryset = TipoPessoa.objects.exclude(nome__iexact='obreiro').order_by('nome')
                    if 'status_pessoa' in self.fields:
                        self.fields['status_pessoa'].queryset = StatusPessoa.objects.all().order_by('nome')
                    if 'foto' in self.fields:
                        try:
                            self.fields['foto'].widget.template_name = 'secretaria/widgets/custom_clearable_file_input.html'
                        except Exception:
                            pass
                except Exception:
                    pass

    except Exception:
        # If anything here fails, do not break module import
        pass

from django import forms
from .models import Tag

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['nome', 'cor', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da tag', 'style': 'max-width: 180px; display: inline-block;'}),
            'cor': forms.TextInput(attrs={'type': 'color', 'class': 'form-control-color', 'style': 'max-width: 60px; display: inline-block;'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Descrição (opcional)', 'style': 'max-width: 220px; display: inline-block;'}),
        }


class CadastroPremiumMultietapasForm(MembroForm):
    data_batismo = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Data do Batismo'
    )
    numero_credencial = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numero da credencial'}),
        label='Numero da Credencial'
    )
    data_consagracao = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Data da Consagracao'
    )
    convencao = forms.CharField(
        required=False,
        max_length=120,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Convencao / jurisdicao'}),
        label='Convencao'
    )
    observacoes_ministeriais = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observacoes ministeriais'}),
        label='Observacoes Ministeriais'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'tipo_pessoa' in self.fields:
            self.fields['tipo_pessoa'].queryset = self.fields['tipo_pessoa'].queryset.exclude(nome__iexact='obreiro')

    def clean(self):
        cleaned_data = super().clean()

        tipo_pessoa = cleaned_data.get('tipo_pessoa')
        status_pessoa = cleaned_data.get('status_pessoa')
        grau_eclesiastico = cleaned_data.get('grau_eclesiastico')

        tipo_nome = (getattr(tipo_pessoa, 'nome', '') or '').strip().lower()
        status_nome = (getattr(status_pessoa, 'nome', '') or '').strip().lower()

        if tipo_nome == 'obreiro':
            self.add_error(
                'tipo_pessoa',
                'O tipo "Obreiro" foi incorporado ao Grau Eclesiastico. Selecione "Membro" e defina o grau eclesiastico.'
            )

        if status_nome in {'em disciplina', 'desligado'} and tipo_nome != 'membro':
            self.add_error(
                'status_pessoa',
                'Status "Em Disciplina" e "Desligado" sao permitidos apenas para Tipo de Pessoa "Membro".'
            )

        if tipo_nome != 'membro':
            cleaned_data['tipo_entrada'] = None
            cleaned_data['grau_eclesiastico'] = None
            cleaned_data['data_batismo'] = None
            cleaned_data['numero_credencial'] = ''
            cleaned_data['data_consagracao'] = None
            cleaned_data['convencao'] = ''
            cleaned_data['observacoes_ministeriais'] = ''
        else:
            if not grau_eclesiastico:
                cleaned_data['grau_eclesiastico'] = 'membro_comum'
            if cleaned_data.get('grau_eclesiastico') == 'membro_comum':
                cleaned_data['numero_credencial'] = ''
                cleaned_data['data_consagracao'] = None
                cleaned_data['convencao'] = ''
                cleaned_data['observacoes_ministeriais'] = ''

        if tipo_nome in {'visitante'}:
            cleaned_data['profissao'] = ''
            cleaned_data['escolaridade'] = ''
            cleaned_data['nome_pai'] = ''
            cleaned_data['nome_mae'] = ''

        return cleaned_data
