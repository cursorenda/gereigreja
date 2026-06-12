# context_onboarding.py
import logging

from configuracao.models_onboarding import OnboardingStatus
from configuracao.utils_onboarding import (
    etapa_igreja_concluida,
    etapa_membros_concluida,
    etapa_configuracoes_concluida,
    etapa_usuarios_concluida,
)

logger = logging.getLogger("onboarding")

def onboarding_context(request):
    mostrar_assistente = False
    onboarding_etapa = None
    ministerio_dados = None
    igreja_dados = None
    if request.user.is_authenticated:
        try:
            onboarding, _ = OnboardingStatus.objects.get_or_create(usuario=request.user)
            if not etapa_igreja_concluida(request.user):
                onboarding_etapa = 1
            elif not etapa_membros_concluida(request.user):
                onboarding_etapa = 2
            elif not etapa_configuracoes_concluida(request.user):
                onboarding_etapa = 3
            elif not etapa_usuarios_concluida(request.user):
                onboarding_etapa = 4
            if onboarding_etapa:
                mostrar_assistente = True
            # Coleta dados do ministério para exibir na etapa 1
            perfil = getattr(request.user, 'perfil', None)
            if perfil and getattr(perfil, 'ministerio', None):
                ministerio = perfil.ministerio
                ministerio_dados = {
                    'nome_fantasia': getattr(ministerio, 'nome_fantasia', ''),
                    'razao_social': getattr(ministerio, 'razao_social', ''),
                    'cnpj': getattr(ministerio, 'cnpj', ''),
                    'responsavel': getattr(ministerio, 'administrador_principal', None),
                    'email': getattr(ministerio, 'email', ''),
                    'telefone': getattr(ministerio, 'telefone', ''),
                    'endereco': f"{getattr(ministerio, 'rua', '')}, {getattr(ministerio, 'numero_casa', '')} {getattr(ministerio, 'bairro_distrito', '')} {getattr(ministerio, 'cidade', '')} {getattr(ministerio, 'estado', '')}",
                }
                if ministerio_dados['responsavel']:
                    ministerio_dados['responsavel'] = str(ministerio_dados['responsavel'])
                # Coleta dados da igreja em contexto (prioriza igreja ativa da sessão).
                igrejas = getattr(ministerio, 'igrejas', None)
                if igrejas and igrejas.exists():
                    igreja = None
                    igreja_contexto_label = 'Igreja principal do ministério'

                    igreja_ativa = getattr(request, 'igreja_ativa', None)
                    if igreja_ativa and getattr(igreja_ativa, 'ministerio_id', None) == ministerio.id:
                        igreja = igreja_ativa
                        igreja_contexto_label = 'Igreja selecionada no topo (contexto ativo)'
                    else:
                        igreja = igrejas.first()

                    igreja_dados = {
                        'id': igreja.id,
                        'nome_igreja': igreja.nome_igreja,
                        'contexto_label': igreja_contexto_label,
                        'tipo_igreja': igreja.get_tipo_igreja_display() if hasattr(igreja, 'get_tipo_igreja_display') else '',
                        'endereco': f"{igreja.rua or ''}, {igreja.numero_casa or ''} {getattr(igreja, 'bairro', '') or ''} {igreja.cidade or ''} {igreja.estado or ''}",
                        'responsavel': igreja.pastor_local or '',
                        'telefone': igreja.telefone or '',
                        'email': igreja.email or '',
                        'cnpj': igreja.cnpj or '',
                        'data_fundacao': igreja.data_fundacao,
                    }
        except Exception:
            logger.exception("ONBOARDING CONTEXT PROCESSOR ERROR")
            mostrar_assistente = False
            onboarding_etapa = None
            ministerio_dados = None
            igreja_dados = None
    logger.debug(
        "ONBOARDING CONTEXT user=%s mostrar_assistente=%s onboarding_etapa=%s",
        getattr(request.user, "username", None),
        mostrar_assistente,
        onboarding_etapa,
    )
    return {
        'mostrar_assistente': mostrar_assistente,
        'onboarding_etapa': onboarding_etapa,
        'onboarding_ministerio_dados': ministerio_dados,
        'onboarding_igreja_dados': igreja_dados,
    }
