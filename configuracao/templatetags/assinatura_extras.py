from django import template

register = template.Library()

@register.simple_tag
def total_membros_ministerio(ministerio):
    total = 0
    for igreja in ministerio.igrejas.all():
        total += igreja.membros.count()
    return total
