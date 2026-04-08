from django import forms
from django.contrib.auth.models import Group, User

from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, PASTOR_REGIONAL, user_has_permission_level_or_higher
from contas.models import HierarquiaPermissoes
from configuracao.models import Igreja


class EditarGruposUsuarioForm(forms.Form):
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Grupos/Permissoes",
    )

    def __init__(self, *args, allowed_groups=None, current_groups=None, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_groups = allowed_groups if allowed_groups is not None else Group.objects.none()
        self.fields["grupos"].queryset = allowed_groups
        if current_groups is not None:
            self.fields["grupos"].initial = list(current_groups.values_list("id", flat=True))


class VinculoHierarquicoForm(forms.ModelForm):
    class Meta:
        model = HierarquiaPermissoes
        fields = ["usuario_subordinado", "nivel_superior", "igreja", "ativo"]
        labels = {
            "usuario_subordinado": "Usuário Subordinado",
            "nivel_superior": "Nível do Vínculo",
            "igreja": "Igreja (Contexto)",
            "ativo": "Vínculo Ativo",
        }
        help_texts = {
            "usuario_subordinado": "Usuário cuja permissão será gerenciada pelo superior.",
            "nivel_superior": "Nível hierárquico que autoriza o gerenciamento.",
            "igreja": "Igreja na qual este vínculo é válido. Para Pastores Locais é obrigatório.",
            "ativo": "Desmarque para desativar sem excluir o histórico.",
        }
        widgets = {
            "usuario_subordinado": forms.Select(attrs={"class": "form-select"}),
            "nivel_superior": forms.Select(attrs={"class": "form-select"}),
            "igreja": forms.Select(attrs={"class": "form-select"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, usuario_superior=None, ministerio=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.usuario_superior = usuario_superior
        self.ministerio = ministerio

        users_qs = User.objects.filter(is_active=True).exclude(pk=getattr(usuario_superior, "pk", None))
        igrejas_qs = Igreja.objects.all()

        if ministerio is not None:
            users_qs = users_qs.filter(perfil__ministerio=ministerio)
            igrejas_qs = igrejas_qs.filter(ministerio=ministerio)

        if usuario_superior and user_has_permission_level_or_higher(usuario_superior, PASTOR_LOCAL):
            igreja_local = None
            perfil = getattr(usuario_superior, "perfil", None)
            if perfil is not None:
                igreja_local = perfil.igrejas_permitidas.first()
            if igreja_local is not None and not user_has_permission_level_or_higher(usuario_superior, PASTOR_REGIONAL):
                users_qs = users_qs.filter(perfil__igrejas_permitidas=igreja_local)
                igrejas_qs = igrejas_qs.filter(pk=igreja_local.pk)

        self.fields["usuario_subordinado"].queryset = users_qs.distinct().order_by("first_name", "last_name", "username")
        self.fields["igreja"].queryset = igrejas_qs.order_by("nome_igreja")

        if usuario_superior:
            if user_has_permission_level_or_higher(usuario_superior, ADMIN_MINISTERIO):
                self.fields["nivel_superior"].choices = HierarquiaPermissoes.NIVEL_CHOICES
            elif user_has_permission_level_or_higher(usuario_superior, PASTOR_REGIONAL):
                self.fields["nivel_superior"].choices = [(PASTOR_REGIONAL, "Pastor Regional")]
                self.fields["nivel_superior"].initial = PASTOR_REGIONAL
            else:
                self.fields["nivel_superior"].choices = [(PASTOR_LOCAL, "Pastor Local")]
                self.fields["nivel_superior"].initial = PASTOR_LOCAL

    def clean_usuario_subordinado(self):
        usuario_subordinado = self.cleaned_data["usuario_subordinado"]
        if self.usuario_superior and usuario_subordinado == self.usuario_superior:
            raise forms.ValidationError("Nao e permitido criar vinculo com o proprio usuario.")
        return usuario_subordinado
