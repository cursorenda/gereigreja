from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.contrib import messages
from configuracao.models import PerfilUsuario, Ministerio
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from configuracao.models import AssinaturaMinisterio
from configuracao.services_assinatura import assinatura_esta_regular, obter_assinatura_ministerio
from notificacoes.models import Notificacao

import logging

logger = logging.getLogger(__name__)

WEEKDAY_LABELS = {
    'pt': {'mon': 'SEG', 'tue': 'TER', 'wed': 'QUA', 'thu': 'QUI', 'fri': 'SEX', 'sat': 'SÁB', 'sun': 'DOM'},
    'en': {'mon': 'MON', 'tue': 'TUE', 'wed': 'WED', 'thu': 'THU', 'fri': 'FRI', 'sat': 'SAT', 'sun': 'SUN'},
}


def get_weekday_label(value, language='pt'):
    """Retorna o nome abreviado do dia da semana em um idioma configurado.

    O padrão é português, mas o helper já aceita outros idiomas para futura expansão.
    """
    if hasattr(value, 'weekday'):
        weekday_index = value.weekday()
    else:
        weekday_index = int(value)

    names = WEEKDAY_LABELS.get(language, WEEKDAY_LABELS['pt'])
    mapping = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    return names[mapping[weekday_index]].upper()

def get_ministerio_or_error(request):
    """
    Obtém a ministério do usuário logado.
    Levanta PermissionDenied se não autenticado, superuser, ou erro de perfil.
    Levanta Http404 se o perfil não tem ministério associada.
    Retorna o objeto Ministerio em caso de sucesso.
    """
    from django.contrib import messages
    from django.shortcuts import reverse
    from configuracao.models import AssinaturaMinisterio
    from notificacoes.models import Notificacao
    import logging
    logger = logging.getLogger(__name__)
    
    if not request.user.is_authenticated:
        raise PermissionDenied("Usuário não autenticado.")
    
    if request.user.is_superuser:
        raise PermissionDenied("Superusuário não acessa esta área diretamente.")
    
    perfil = getattr(request.user, 'perfil', None)
    ministerio = getattr(perfil, 'ministerio', None)

    if not ministerio:
        membro = getattr(request.user, 'membro_secretaria', None)
        ministerio = getattr(getattr(membro, 'igreja', None), 'ministerio', None)

    if not ministerio:
        ministerio = Ministerio.objects.filter(administrador_principal=request.user).first()

    if not ministerio:
        raise Http404("Ministério não encontrada para o usuário.")
    
    if not ministerio.ativo:
        messages.warning(request, f"A ministério '{ministerio.nome_fantasia}' não está ativa. Contate o suporte do sistema.")
        raise PermissionDenied(f"Acesso negado: Ministério '{ministerio.nome_fantasia}' inativa.")
    
    # Nota: Verificação de status da assinatura agora centralizada em context_status_plano.py
    # Mantém apenas notificações no sininho para admins/tesouraria
    try:
        assinatura = obter_assinatura_ministerio(ministerio)
        if not assinatura_esta_regular(assinatura, ministerio) and request.path != reverse('configuracao:gerenciar_assinatura'):
            # Notificação no sininho apenas para perfis ministeriais responsáveis
            from contas.constants import ADMIN_MINISTERIO, LIDERANCA_FINANCEIRA
            from configuracao.models import PerfilUsuario
            perfis_notificados = PerfilUsuario.objects.filter(
                ministerio=ministerio,
                user__is_active=True,
                user__groups__name__in=[ADMIN_MINISTERIO, LIDERANCA_FINANCEIRA],
            ).select_related('user').distinct()
            users_in_org = [p.user for p in perfis_notificados]
            for user in users_in_org:
                existe = Notificacao.objects.filter(
                    user=user,
                    ministerio=ministerio,
                    notification_type='financeiro',
                    is_read=False,
                    message__icontains='assinatura',
                ).exists()
                if not existe:
                    plano_nome = assinatura.plano.get_nome_display() if assinatura and assinatura.plano else 'Atual'
                    Notificacao.objects.create(
                        user=user,
                        ministerio=ministerio,
                        message=f"Sua assinatura do plano {plano_nome} está {assinatura.get_status_display() if assinatura else 'indefinido'}. Regularize sua situação ou ative sua cortesia.",
                        notification_type='financeiro',
                        url=reverse('configuracao:gerenciar_assinatura'),
                    )
    except Exception as e_assinatura:
        logger.error(f"Erro ao verificar assinatura para ministério {ministerio.id} em get_ministerio_or_error: {e_assinatura}")

    return ministerio


# ===================================
# FUNÇÕES DE ESCOPO HIERÁRQUICO
# ===================================

def get_igrejas_selecionaveis(user, ministerio=None):
    """Retorna o escopo organizacional canônico do seletor de igreja.

    Este escopo não concede permissão funcional. Admin Ministério pode
    selecionar as igrejas do próprio ministério; os demais perfis dependem
    exclusivamente dos vínculos explícitos em ``PerfilUsuario``.
    """
    from configuracao.models import Igreja
    from contas.constants import user_is_admin

    if not getattr(user, 'is_authenticated', False):
        return Igreja.objects.none()

    perfil = getattr(user, 'perfil', None) or getattr(user, 'perfil_usuario', None)
    ministerio_perfil = getattr(perfil, 'ministerio', None)

    if user.is_superuser:
        if ministerio is not None:
            return Igreja.objects.filter(ministerio=ministerio)
        return Igreja.objects.all()

    if not ministerio_perfil:
        return Igreja.objects.none()

    if ministerio is not None and ministerio.pk != ministerio_perfil.pk:
        return Igreja.objects.none()

    if user_is_admin(user):
        return Igreja.objects.filter(ministerio=ministerio_perfil)

    return perfil.igrejas_permitidas.filter(ministerio=ministerio_perfil)

def get_igrejas_permitidas(user, ministerio=None):
    """
    Retorna queryset de igrejas que o usuário pode acessar baseado em seu escopo hierárquico.
    
    HIERARQUIA DE ESCOPOS:
    - Superusuário: TODAS as igrejas
    - Escopo Ministerial (Admin, Liderança): TODAS as igrejas do ministério
    - Escopo Regional (Pastor Regional): Igrejas da sua região + subordinadas
    - Escopo Local (demais): Apenas sua igreja_ativa + subordinadas do perfil
    
    Args:
        user: Objeto User autenticado
        ministerio: Objeto Ministerio (opcional, pega do perfil se None)
    
    Returns:
        QuerySet de Igreja: Igrejas que o usuário pode acessar
        
    Uso:
        igrejas = get_igrejas_permitidas(request.user)
        membros = Membro.objects.filter(igreja__in=igrejas)
    """
    from configuracao.models import Igreja
    from contas.constants import user_escopo_ministerial, user_escopo_regional, user_escopo_local
    
    logger.debug("[GET_IGREJAS_PERMITIDAS] Iniciando para user=%s", user.username)
    
    # Superusuário vê TUDO
    if user.is_superuser:
        logger.debug("[GET_IGREJAS_PERMITIDAS] Usuário é SUPERUSER - retornando TODAS")
        return Igreja.objects.all()
    
    if not user.is_authenticated:
        logger.debug("[GET_IGREJAS_PERMITIDAS] Usuário NÃO autenticado - retornando VAZIO")
        return Igreja.objects.none()
    
    # Tenta pegar ministério do perfil se não foi fornecido
    if not ministerio:
        try:
            ministerio = user.perfil.ministerio
            logger.debug("[GET_IGREJAS_PERMITIDAS] Ministério obtido do perfil: %s", ministerio)
        except Exception:
            logger.debug("[GET_IGREJAS_PERMITIDAS] Erro ao obter ministério do perfil")
            return Igreja.objects.none()
    
    if not ministerio:
        logger.debug("[GET_IGREJAS_PERMITIDAS] Ministério é None - retornando VAZIO")
        return Igreja.objects.none()
    
    # ESCOPO MINISTERIAL: Admin, Liderança Secretaria, Liderança Financeira
    if user_escopo_ministerial(user):
        logger.debug("[GET_IGREJAS_PERMITIDAS] Usuário tem ESCOPO MINISTERIAL")
        # Verifica se tem igrejas específicas no perfil
        if hasattr(user, 'perfil') and user.perfil.igrejas_permitidas.exists():
            igrejas = user.perfil.igrejas_permitidas.filter(ministerio=ministerio)
            logger.debug("[GET_IGREJAS_PERMITIDAS] Usando igrejas_permitidas do perfil")
            return igrejas
        # Se não tem restrição, vê TODAS do ministério
        igrejas = Igreja.objects.filter(ministerio=ministerio)
        logger.debug("[GET_IGREJAS_PERMITIDAS] Retornando TODAS as igrejas do ministério")
        return igrejas
    
    # ESCOPO REGIONAL: Pastor Regional
    elif user_escopo_regional(user):
        logger.debug("[GET_IGREJAS_PERMITIDAS] Usuário tem ESCOPO REGIONAL")
        # TODO: Implementar filtro por região quando o campo estiver pronto
        # Por enquanto, usa igrejas_permitidas do perfil
        if hasattr(user, 'perfil') and user.perfil.igrejas_permitidas.exists():
            igrejas_base = user.perfil.igrejas_permitidas.filter(ministerio=ministerio)
            # Inclui subordinadas
            igrejas = _get_igrejas_com_subordinadas(igrejas_base, ministerio)
            logger.debug("[GET_IGREJAS_PERMITIDAS] Retornando igrejas regionais + subordinadas")
            return igrejas
        # Se não tem igrejas no perfil, retorna vazio
        logger.debug("[GET_IGREJAS_PERMITIDAS] Sem igrejas_permitidas - retornando VAZIO")
        return Igreja.objects.none()
    
    # ESCOPO LOCAL: Pastor Local, Secretário, Tesoureiro, Equipes, etc
    elif user_escopo_local(user):
        logger.debug("[GET_IGREJAS_PERMITIDAS] Usuário tem ESCOPO LOCAL")
        if hasattr(user, 'perfil'):
            # Usa igrejas_permitidas do perfil
            if user.perfil.igrejas_permitidas.exists():
                igrejas_base = user.perfil.igrejas_permitidas.filter(ministerio=ministerio)
                igrejas = _get_igrejas_com_subordinadas(igrejas_base, ministerio)
                logger.debug("[GET_IGREJAS_PERMITIDAS] Usando igrejas_permitidas")
                return igrejas
            else:
                # Fallback seguro: usa igreja(s) vinculada(s) ao membro do próprio usuário.
                try:
                    from secretaria.models import Membro
                    igrejas_membro = Igreja.objects.filter(
                        membros__usuario=user,
                        ministerio=ministerio,
                    ).distinct()
                    if igrejas_membro.exists():
                        logger.debug("[GET_IGREJAS_PERMITIDAS] Fallback por vínculo de membro")
                        return igrejas_membro
                except Exception as exc:
                    logger.debug("[GET_IGREJAS_PERMITIDAS] Falha no fallback por membro: %s", exc)

                logger.debug("[GET_IGREJAS_PERMITIDAS] Perfil sem igrejas_permitidas e sem vínculo de membro - retornando VAZIO")
        else:
            logger.debug("[GET_IGREJAS_PERMITIDAS] Usuário sem perfil - retornando VAZIO")
        
        return Igreja.objects.none()
    
    # Sem grupo: sem acesso
    logger.debug("[GET_IGREJAS_PERMITIDAS] Usuário SEM ESCOPO definido - retornando VAZIO")
    return Igreja.objects.none()


def _get_igrejas_com_subordinadas(igrejas_base, ministerio):
    """
    Helper: retorna igrejas base + todas as subordinadas recursivamente.
    
    Args:
        igrejas_base: QuerySet de igrejas base
        ministerio: Objeto Ministerio para filtro de segurança
        
    Returns:
        QuerySet de Igreja com base + subordinadas
    """
    from configuracao.models import Igreja
    
    todas_igrejas_ids = set()
    
    def _recursivo(igreja):
        """Coleta recursivamente IDs de subordinadas."""
        ids = {igreja.pk}
        for sub in igreja.igrejas_subordinadas.filter(ministerio=ministerio):
            ids.update(_recursivo(sub))
        return ids
    
    for igreja in igrejas_base:
        todas_igrejas_ids.update(_recursivo(igreja))
    
    if todas_igrejas_ids:
        return Igreja.objects.filter(pk__in=list(todas_igrejas_ids), ministerio=ministerio)
    
    return Igreja.objects.none()


def resolve_lideranca_scope(request, ministerio, allowed_churches_base):
    """
    Resolve escopo hierárquico para filtros de painéis de liderança.

    Retorna dict com:
    - churches_for_queries
    - opcoes_filtro_pagina
    - igreja_id_filtro_selecionado
    - titulo_escopo_igreja
    - label_opcao_all
    - filtro_invalido (bool)
    """
    from configuracao.models import Igreja

    opcoes_filtro_pagina = allowed_churches_base.order_by('nome_igreja')
    igreja_id_filtro = request.GET.get('igreja_filtro', '')
    titulo_escopo_igreja = f"Consolidado - {ministerio.nome_fantasia}"
    igreja_em_foco_obj = None
    ver_apenas_entidade_foco = False
    filtro_invalido = False
    label_opcao_all = "Toda a Rede (Permitidas)"

    igreja_ativa = getattr(request, 'igreja_ativa', None)
    allowed_ids_qs = allowed_churches_base.values_list('pk', flat=True)

    if igreja_ativa and allowed_churches_base.filter(pk=igreja_ativa.pk).exists():
        dropdown_ids = {igreja_ativa.pk}
        desc_dropdown_qs = igreja_ativa.get_descendants(include_self=False).filter(pk__in=allowed_ids_qs)
        if desc_dropdown_qs.exists():
            dropdown_ids.update(desc_dropdown_qs.values_list('pk', flat=True))
        opcoes_filtro_pagina = Igreja.objects.filter(pk__in=list(dropdown_ids)).order_by('nome_igreja')

        if len(dropdown_ids) > 1:
            label_opcao_all = f"Rede: {igreja_ativa.nome_igreja}"

        if not igreja_id_filtro:
            igreja_id_filtro = str(igreja_ativa.pk)

        if igreja_id_filtro == str(igreja_ativa.pk):
            igreja_em_foco_obj = igreja_ativa
            explicit_global = request.GET.get('igreja_filtro') == str(igreja_ativa.pk)
            if explicit_global and len(dropdown_ids) > 1:
                ver_apenas_entidade_foco = True
                titulo_escopo_igreja = f"Apenas: {igreja_ativa.nome_igreja}"
            else:
                ver_apenas_entidade_foco = False
                titulo_escopo_igreja = f"Rede: {igreja_ativa.nome_igreja}" if len(dropdown_ids) > 1 else f"Igreja: {igreja_ativa.nome_igreja}"
        else:
            try:
                igreja_descendente = opcoes_filtro_pagina.get(pk=igreja_id_filtro)
                igreja_em_foco_obj = igreja_descendente
                igreja_id_filtro = str(igreja_descendente.pk)
                tem_filhas_no_escopo = igreja_descendente.get_descendants(include_self=False).filter(pk__in=allowed_ids_qs).exists()
                if tem_filhas_no_escopo:
                    ver_apenas_entidade_foco = False
                    titulo_escopo_igreja = f"Rede: {igreja_descendente.nome_igreja}"
                else:
                    ver_apenas_entidade_foco = True
                    titulo_escopo_igreja = f"Igreja: {igreja_descendente.nome_igreja}"
            except Igreja.DoesNotExist:
                filtro_invalido = True
                igreja_id_filtro = str(igreja_ativa.pk)
                igreja_em_foco_obj = igreja_ativa
                ver_apenas_entidade_foco = False
                titulo_escopo_igreja = f"Rede: {igreja_ativa.nome_igreja}" if len(dropdown_ids) > 1 else f"Igreja: {igreja_ativa.nome_igreja}"
    else:
        if igreja_id_filtro:
            try:
                igreja_em_foco_obj = allowed_churches_base.get(pk=igreja_id_filtro)
                ver_apenas_entidade_foco = False
            except Igreja.DoesNotExist:
                filtro_invalido = True
                igreja_id_filtro = ''
                igreja_em_foco_obj = None
                titulo_escopo_igreja = f"Consolidado - {ministerio.nome_fantasia}"

    if igreja_em_foco_obj:
        if ver_apenas_entidade_foco:
            churches_for_queries = Igreja.objects.filter(pk=igreja_em_foco_obj.pk)
        else:
            pks_to_include = {igreja_em_foco_obj.pk}
            desc_qs = igreja_em_foco_obj.get_descendants(include_self=False).filter(pk__in=allowed_ids_qs)
            if desc_qs.exists():
                pks_to_include.update(desc_qs.values_list('pk', flat=True))
            churches_for_queries = Igreja.objects.filter(pk__in=list(pks_to_include), ministerio=ministerio)
            if len(pks_to_include) > 1:
                titulo_escopo_igreja = f"Rede: {igreja_em_foco_obj.nome_igreja}"
            else:
                titulo_escopo_igreja = f"Igreja: {igreja_em_foco_obj.nome_igreja}"
    else:
        churches_for_queries = allowed_churches_base

    return {
        'churches_for_queries': churches_for_queries,
        'opcoes_filtro_pagina': opcoes_filtro_pagina,
        'igreja_id_filtro_selecionado': igreja_id_filtro,
        'titulo_escopo_igreja': titulo_escopo_igreja,
        'label_opcao_all': label_opcao_all,
        'filtro_invalido': filtro_invalido,
    }


def get_request_allowed_churches(request):
    """Retorna o queryset de igrejas permitidas já resolvido no request."""
    from configuracao.models import Igreja

    allowed_churches = getattr(request, 'igrejas_permitidas', None)
    if allowed_churches is None:
        return Igreja.objects.none()
    return allowed_churches


def get_request_scoped_churches(request, allowed_churches=None):
    """
    Retorna o escopo efetivo para consultas:
    - se igreja_ativa válida no escopo permitido: apenas ela
    - caso contrário: todas as igrejas permitidas
    """
    from configuracao.models import Igreja

    allowed = allowed_churches if allowed_churches is not None else get_request_allowed_churches(request)
    igreja_ativa = getattr(request, 'igreja_ativa', None)

    if igreja_ativa and allowed.filter(pk=igreja_ativa.pk).exists():
        return Igreja.objects.filter(pk=igreja_ativa.pk)
    return allowed


def validar_acesso_igreja(user, igreja):
    """
    Valida se o usuário tem permissão para acessar uma igreja específica.
    
    Args:
        user: Objeto User
        igreja: Objeto Igreja
        
    Returns:
        bool: True se tem acesso, False caso contrário
        
    Uso:
        if not validar_acesso_igreja(request.user, membro.igreja):
            raise PermissionDenied("Você não pode acessar membros desta igreja")
    """
    if user.is_superuser:
        return True
    
    igrejas_permitidas = get_igrejas_permitidas(user, igreja.ministerio)
    return igrejas_permitidas.filter(pk=igreja.pk).exists()


def validar_acesso_objeto_igreja(user, obj, campo_igreja='igreja'):
    """
    Valida se o usuário tem permissão para acessar um objeto que pertence a uma igreja.
    
    Args:
        user: Objeto User
        obj: Objeto com FK para Igreja
        campo_igreja: Nome do campo FK (default: 'igreja')
        
    Returns:
        bool: True se tem acesso
        
    Raises:
        PermissionDenied: Se não tem acesso
        
    Uso:
        validar_acesso_objeto_igreja(request.user, membro)  # membro.igreja
        validar_acesso_objeto_igreja(request.user, turma, 'escola__igreja')
    """
    igreja = obj
    for campo in campo_igreja.split('__'):
        igreja = getattr(igreja, campo, None)
        if igreja is None:
            raise PermissionDenied("Objeto não está associado a uma igreja")
    
    if not validar_acesso_igreja(user, igreja):
        raise PermissionDenied(f"Você não tem permissão para acessar dados desta igreja: {igreja.nome_igreja}")
    
    return True

