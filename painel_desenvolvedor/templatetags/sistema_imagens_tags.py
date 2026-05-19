from django import template
from django.templatetags.static import static

from painel_desenvolvedor.models import SistemaImagem

register = template.Library()


@register.simple_tag
def sistema_imagem_url(tipo, variacao='original', fallback_path=''):
    """Retorna a URL da imagem ativa da galeria para tipo/variacao.

    Se não houver imagem ativa, usa o fallback_path (caminho static relativo)
    quando informado.
    """
    try:
        imagem = SistemaImagem.objects.filter(
            tipo=tipo,
            variacao=variacao,
            ativo=True,
        ).order_by('-data_upload').first()

        if imagem and imagem.imagem:
            return imagem.imagem.url
    except Exception:
        pass

    if fallback_path:
        if fallback_path.startswith('http://') or fallback_path.startswith('https://'):
            return fallback_path
        if fallback_path.startswith('/'):
            return fallback_path
        return static(fallback_path)

    return ''
