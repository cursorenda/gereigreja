# secretaria/views/__init__.py
#
# Proxy de compatibilidade: re-exporta tudo de _legacy.py
# para que urls.py continue funcionando sem nenhuma alteração.
#
# Estrutura de módulos (migração incremental):
#   _legacy.py      — código original completo (será esvaziado gradualmente)
#   _helpers.py     — helpers de permissão e escopo (sem dependência de request)
#   membros.py      — lista, detalhe, criar, editar, alternar status, ficha
#   visitantes.py   — lista, cadastrar, presença, acompanhamento
#   cargos.py       — lista, criar, editar, excluir, ocupantes
#   grupos_casa.py  — lista, criar, editar, agrupar, reagrupar
#   dashboard.py    — index, dashboard, painel_liderança, portal
#   tags.py         — criar, editar, excluir tag
#   ajax.py         — autocomplete, salvar nota, ajax presença/buscas
#   relatorios.py   — linha do tempo, relatório reunião, imprimir lista
#   certificado_apresentacao.py — emissão de certificado de apresentação
#   certificado_batismo.py — emissão de certificado de batismo

# Tudo que ainda não foi extraído permanece disponível via _legacy
from ._legacy import *  # noqa: F401, F403

# Importações explícitas dos módulos extraídos (têm precedência sobre _legacy)
from ._helpers import (  # noqa: F401
    _coletar_ids_grupos, _grupos_por_cargo_ativo, _grupos_reservados_para_cargo,
    recalcular_grupos_efetivos_usuario, get_request_scoped_churches,
    resolve_lideranca_scope, _hierarquia_grupos_permissoes,
    _user_has_permission_level_or_higher, pode_gerenciar_tags,
    is_admin_or_pastor, is_admin_or_pastor_local, _nomes_grupos_permitidos_para_cargos,
    _filtrar_cargos_por_escopo_usuario, _cargo_dentro_escopo_usuario,
    _membros_queryset_por_escopo, safe_instantiate_membroform, _get_navigation_context,
)
from .membros import (  # noqa: F401
    lista_membros, detalhe_membro, imprimir_lista_membros, editar_membro,
    criar_membro, alternar_status_membro, ficha_membro_impressao,
)
from .visitantes import (  # noqa: F401
    lista_visitantes, buscar_visitantes, registrar_presenca_visitante_evento,
    ajax_registrar_presenca_evento, ajax_get_presencas_evento,
    cadastrar_visitante, criar_visitante_parcial, registrar_acompanhamento_visita,
    central_visitacao,
)
from .cargos import (  # noqa: F401
    gerenciar_ocupantes, excluir_cargo, criar_cargo, editar_cargo, lista_cargos,
)
from .grupos_casa import (  # noqa: F401
    limpar_grupos_casa_vazios, lista_grupos_casa, agrupar_grupos_preview,
    agrupar_grupos_apply, reagrupar_grupo_casa, detalhe_grupo_casa,
    criar_grupo_casa, editar_grupo_casa, buscar_pessoas_grupo_casa,
)
from .dashboard import (  # noqa: F401
    index, salvar_nota_usuario, dashboard, exportar_dashboard_csv,
)
from .ajax import (  # noqa: F401
    autocomplete_nome, autocomplete_nome_membro,
)
from .relatorios import (  # noqa: F401
    linha_do_tempo, relatorio_reuniao_membros,
)
from .tags import (  # noqa: F401
    criar_tag, editar_tag, excluir_tag,
)
from .certificado_apresentacao import (  # noqa: F401
    certificado_apresentacao,
)
from .certificado_batismo import (  # noqa: F401
    certificado_batismo,
)
from .carta_recomendacao import (  # noqa: F401
    carta_recomendacao,
)
from .carteirinha import (  # noqa: F401
    carteirinha_premium_1, validar_carteirinha_qr,
)
from .cadastro_premium import (  # noqa: F401
    cadastro_premium_multietapas,
)
from .cadastro_legado_redirects import (  # noqa: F401
    pre_cadastro, cadastro_detalhado, cadastro_complementar,
)
