from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import TemplateView

from core.utils import get_ministerio_or_error

from .services import (
    resolver_igreja_contexto,
    listar_hinos_para_portal,
    obter_hino_para_exibicao,
    paginar_hinos,
    listar_resumo_portal,
)


class HinoCatalogoView(LoginRequiredMixin, TemplateView):
    """Catálogo premium de hinos para o membro."""

    template_name = 'hinario/catalogo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ministerio = get_ministerio_or_error(self.request)
        ministerio, igreja_contexto, igrejas_permitidas = resolver_igreja_contexto(self.request, ministerio)

        busca = self.request.GET.get('q', '').strip()
        colecao = self.request.GET.get('colecao', '').strip()
        tema = self.request.GET.get('tema', '').strip()
        ordem = self.request.GET.get('ordem', 'numero_asc').strip()
        if not colecao:
            colecao = None
        if not tema:
            tema = None
        if ordem not in ['numero_asc', 'numero_desc', 'titulo_asc', 'titulo_desc']:
            ordem = 'numero_asc'

        hinos = listar_hinos_para_portal(
            igreja_contexto,
            colecao=colecao,
            busca=busca,
            ordem=ordem,
            tema=tema,
        )
        page_obj = paginar_hinos(hinos, self.request.GET.get('page', 1), per_page=12)
        resumo = listar_resumo_portal(igreja_contexto)

        context.update({
            'ministerio': ministerio,
            'igreja_contexto': igreja_contexto,
            'igrejas_permitidas': igrejas_permitidas,
            'resumo': resumo,
            'busca': busca,
            'ordem': ordem,
            'colecao_selecionada': colecao or '',
            'tema_selecionado': tema or '',
            'colecoes_disponiveis': resumo['colecoes'],
            'temas_disponiveis': resumo['temas'],
            'hinos': page_obj.object_list,
            'page_obj': page_obj,
            'total_hinos': len(hinos),
            'url_detalhe_base': 'hinario:detalhe',
        })
        return context


class HinoDetalheView(LoginRequiredMixin, TemplateView):
    """Detalhe premium de um hino."""

    template_name = 'hinario/detalhe.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ministerio = get_ministerio_or_error(self.request)
        ministerio, igreja_contexto, igrejas_permitidas = resolver_igreja_contexto(self.request, ministerio)

        colecao = kwargs.get('colecao')
        numero = kwargs.get('numero')
        try:
            numero = int(numero)
        except (TypeError, ValueError):
            raise Http404('Hino inválido.')

        hino = obter_hino_para_exibicao(igreja_contexto, colecao, numero)
        if not hino:
            raise Http404('Hino não encontrado.')

        context.update({
            'ministerio': ministerio,
            'igreja_contexto': igreja_contexto,
            'igrejas_permitidas': igrejas_permitidas,
            'hino': hino,
            'tem_texto_publico': hino['can_render_public_text'],
            'bloqueado': not hino['can_render_public_text'],
            'motivo_bloqueio': 'Conteúdo sob revisão ou restrição jurídica.' if not hino['can_render_public_text'] else '',
        })
        return context
