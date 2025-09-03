from django import template

register = template.Library()

@register.filter
def igrejas_ativas_count(ministerio):
    """Retorna a quantidade de igrejas ativas do ministério."""
    return ministerio.igrejas.filter(ativo=True).count() if ministerio else 0
