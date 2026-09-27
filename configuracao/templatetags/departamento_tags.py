from django import template

from configuracao.models import DepartamentoVinculo


register = template.Library()


@register.simple_tag
def usuario_tem_departamento_ativo(user):
    """Indica somente se o usuário possui vínculo departamental ativo para exibição no menu."""
    if not getattr(user, 'is_authenticated', False):
        return False

    return DepartamentoVinculo.objects.filter(
        membro__usuario=user,
        data_fim__isnull=True,
    ).exists()