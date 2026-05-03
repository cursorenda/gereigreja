"""
secretaria/views/_helpers.py
Funções helper de permissão, escopo e utilitários da secretaria.
Não contém views nem decoradores de URL.
"""
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q

from configuracao.models import Igreja
from core.utils import get_ministerio_or_error
from secretaria.forms import MembroForm
from secretaria.models import Cargo, Membro, MembroCargo, StatusPessoa, TipoPessoa
from secretaria.utils import get_allowed_churches_for_membros, is_admin_org

logger = logging.getLogger(__name__)
User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers de grupos de permissão (cargo ↔ Group)
# ---------------------------------------------------------------------------

def _coletar_ids_grupos(grupos):
    if grupos is None:
        return None

    if hasattr(grupos, 'values_list'):
        return set(grupos.values_list('id', flat=True))

    ids = set()
    for grupo in grupos:
        if isinstance(grupo, int):
            ids.add(grupo)
            continue
        grupo_id = getattr(grupo, 'id', None)
        if grupo_id is not None:
            ids.add(grupo_id)
    return ids


def _grupos_por_cargo_ativo(user):
    if not user:
        return set()

    return set(
        MembroCargo.objects.filter(
            membro__usuario=user,
            data_fim__isnull=True,
            cargo__grupo_permissao__isnull=False,
        )
        .values_list('cargo__grupo_permissao_id', flat=True)
        .distinct()
    )


def _grupos_reservados_para_cargo():
    return set(
        Cargo.objects.filter(grupo_permissao__isnull=False)
        .values_list('grupo_permissao_id', flat=True)
        .distinct()
    )


def recalcular_grupos_efetivos_usuario(
    user,
    grupos_manuais=None,
    grupos_editaveis=None,
    ignorar_grupos_reservados_no_manual=False,
):
    if not user:
        return Group.objects.none()

    ids_cargo = _grupos_por_cargo_ativo(user)
    ids_atuais = set(user.groups.values_list('id', flat=True))
    ids_manuais_atuais = ids_atuais - ids_cargo
    ids_reservados_cargo = set()

    if ignorar_grupos_reservados_no_manual:
        ids_reservados_cargo = _grupos_reservados_para_cargo()
        ids_manuais_atuais -= ids_reservados_cargo

    ids_editaveis = _coletar_ids_grupos(grupos_editaveis)
    ids_manuais_informados = _coletar_ids_grupos(grupos_manuais)
    if ignorar_grupos_reservados_no_manual and ids_manuais_informados is not None:
        ids_manuais_informados -= ids_reservados_cargo

    if ids_editaveis is None:
        if ids_manuais_informados is None:
            ids_manuais_finais = ids_manuais_atuais
        else:
            ids_manuais_finais = ids_manuais_informados
    else:
        ids_editaveis = set(ids_editaveis)
        ids_manuais_fora_escopo = ids_manuais_atuais - ids_editaveis

        if ids_manuais_informados is None:
            ids_editaveis_finais = ids_manuais_atuais & ids_editaveis
        else:
            ids_editaveis_finais = set(ids_manuais_informados) & ids_editaveis

        ids_manuais_finais = ids_manuais_fora_escopo | ids_editaveis_finais

    ids_finais = ids_cargo | ids_manuais_finais

    if ids_finais != ids_atuais:
        user.groups.set(Group.objects.filter(id__in=ids_finais))

    return user.groups.all()


# ---------------------------------------------------------------------------
# Helpers de escopo de igrejas / liderança
# ---------------------------------------------------------------------------

def get_request_scoped_churches(request, allowed_churches=None):
    allowed = allowed_churches if allowed_churches is not None else getattr(request, 'igrejas_permitidas', Igreja.objects.none())
    igreja_ativa = getattr(request, 'igreja_ativa', None)

    if igreja_ativa and allowed.filter(pk=igreja_ativa.pk).exists():
        return Igreja.objects.filter(pk=igreja_ativa.pk)
    return allowed


def resolve_lideranca_scope(request, ministerio, allowed_churches_base):
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
                titulo_escopo_igreja = f"Rede: {igreja_ativa.nome_igreja}" if len(dropdown_ids) > 1 else f"Igreja: {igreja_ativa.nome_igreja}"
        else:
            try:
                igreja_descendente = opcoes_filtro_pagina.get(pk=igreja_id_filtro)
                igreja_em_foco_obj = igreja_descendente
                igreja_id_filtro = str(igreja_descendente.pk)
                tem_filhas_no_escopo = igreja_descendente.get_descendants(include_self=False).filter(pk__in=allowed_ids_qs).exists()
                if tem_filhas_no_escopo:
                    titulo_escopo_igreja = f"Rede: {igreja_descendente.nome_igreja}"
                else:
                    ver_apenas_entidade_foco = True
                    titulo_escopo_igreja = f"Igreja: {igreja_descendente.nome_igreja}"
            except Igreja.DoesNotExist:
                filtro_invalido = True
                igreja_id_filtro = str(igreja_ativa.pk)
                igreja_em_foco_obj = igreja_ativa
                titulo_escopo_igreja = f"Rede: {igreja_ativa.nome_igreja}" if len(dropdown_ids) > 1 else f"Igreja: {igreja_ativa.nome_igreja}"
    else:
        if igreja_id_filtro:
            try:
                igreja_em_foco_obj = allowed_churches_base.get(pk=igreja_id_filtro)
            except Igreja.DoesNotExist:
                filtro_invalido = True
                igreja_id_filtro = ''
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
            titulo_escopo_igreja = f"Rede: {igreja_em_foco_obj.nome_igreja}" if len(pks_to_include) > 1 else f"Igreja: {igreja_em_foco_obj.nome_igreja}"
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


# ---------------------------------------------------------------------------
# Helpers de permissão hierárquica
# ---------------------------------------------------------------------------

def _hierarquia_grupos_permissoes():
    from contas.constants import (
        ADMIN_MINISTERIO,
        LIDERANCA_SECRETARIA,
        LIDERANCA_FINANCEIRA,
        PASTOR_REGIONAL,
        PASTOR_LOCAL,
        SECRETARIO_LOCAL,
        TESOUREIRO,
        SUPERINTENDENTE_EBD,
        EQUIPE_EVENTOS,
        EQUIPE_MIDIA,
        EQUIPE_RECEPCAO,
        PROFESSOR_EBD,
        SECRETARIA_EBD,
        MEMBRO_COMUM,
    )
    return [
        ADMIN_MINISTERIO,
        LIDERANCA_SECRETARIA,
        LIDERANCA_FINANCEIRA,
        PASTOR_REGIONAL,
        PASTOR_LOCAL,
        SECRETARIO_LOCAL,
        TESOUREIRO,
        SUPERINTENDENTE_EBD,
        EQUIPE_EVENTOS,
        EQUIPE_MIDIA,
        EQUIPE_RECEPCAO,
        PROFESSOR_EBD,
        SECRETARIA_EBD,
        MEMBRO_COMUM,
    ]


def _user_has_permission_level_or_higher(user, required_group):
    """Compatibilidade para ambientes sem helper central no contas.constants."""
    try:
        from contas.constants import user_has_permission_level_or_higher as _helper
        return _helper(user, required_group)
    except Exception:
        if not getattr(user, 'is_authenticated', False):
            return False
        if getattr(user, 'is_superuser', False):
            return True

        hierarquia = _hierarquia_grupos_permissoes()
        try:
            required_idx = hierarquia.index(required_group)
        except ValueError:
            return False

        user_groups = set(user.groups.values_list('name', flat=True))
        user_level = None
        for idx, group in enumerate(hierarquia):
            if group in user_groups:
                user_level = idx
                break

        if user_level is None:
            return False

        return user_level <= required_idx


def pode_gerenciar_tags(user):
    """Permissão: pode criar/editar/excluir tags (secretaria/admin)."""
    from contas.constants import SECRETARIO_LOCAL
    try:
        return _user_has_permission_level_or_higher(user, SECRETARIO_LOCAL)
    except Exception:
        return False


def is_admin_or_pastor(user):
    """Permissão: é superuser ou pertence a grupos administrativos/pastorais."""
    from contas.constants import PASTOR_REGIONAL
    try:
        return _user_has_permission_level_or_higher(user, PASTOR_REGIONAL)
    except Exception:
        return False


def is_admin_or_pastor_local(user):
    """Permissão local para cargos: Admin, Pastor Regional ou Pastor Local."""
    from contas.constants import PASTOR_LOCAL
    try:
        return _user_has_permission_level_or_higher(user, PASTOR_LOCAL)
    except Exception:
        return False


def _nomes_grupos_permitidos_para_cargos(user):
    """Retorna nomes de grupos permitidos no módulo de cargos para o usuário.

    None = sem restrição por grupo (apenas Admin Ministério).
    Caso contrário, retorna o conjunto de grupos a partir do nível do usuário.
    """
    from contas.constants import (
        ADMIN_MINISTERIO,
        PASTOR_LOCAL,
        PASTOR_REGIONAL,
    )

    HIERARQUIA_GRUPOS = _hierarquia_grupos_permissoes()

    if _user_has_permission_level_or_higher(user, ADMIN_MINISTERIO):
        return None

    if _user_has_permission_level_or_higher(user, PASTOR_REGIONAL):
        try:
            idx_regional = HIERARQUIA_GRUPOS.index(PASTOR_REGIONAL)
        except ValueError:
            return set()
        return set(HIERARQUIA_GRUPOS[idx_regional:])

    if _user_has_permission_level_or_higher(user, PASTOR_LOCAL):
        try:
            idx_local = HIERARQUIA_GRUPOS.index(PASTOR_LOCAL)
        except ValueError:
            return set()
        return set(HIERARQUIA_GRUPOS[idx_local:])

    return set()


def _filtrar_cargos_por_escopo_usuario(user, cargos_qs):
    """Restringe cargos visíveis por escopo hierárquico quando necessário."""
    grupos_permitidos = _nomes_grupos_permitidos_para_cargos(user)
    if grupos_permitidos is None:
        return cargos_qs
    if not grupos_permitidos:
        return cargos_qs.none()
    return cargos_qs.filter(
        Q(grupo_permissao__isnull=True) | Q(grupo_permissao__name__in=grupos_permitidos)
    )


def _cargo_dentro_escopo_usuario(user, cargo):
    """Valida se o cargo está dentro do escopo permitido para o usuário."""
    grupos_permitidos = _nomes_grupos_permitidos_para_cargos(user)
    if grupos_permitidos is None:
        return True
    if not grupos_permitidos:
        return False
    if cargo.grupo_permissao_id is None:
        return True
    return cargo.grupo_permissao.name in grupos_permitidos


# ---------------------------------------------------------------------------
# Helper de queryset de membros/visitantes por escopo
# ---------------------------------------------------------------------------

def _membros_queryset_por_escopo(request):
    """Retorna queryset base de pessoas respeitando igreja_ativa e igrejas_permitidas."""
    if request.user.is_superuser:
        return Membro.objects.all()

    igrejas_permitidas = getattr(request, 'igrejas_permitidas', None)
    if igrejas_permitidas is None:
        ministerio = get_ministerio_or_error(request)
        igrejas_permitidas = get_allowed_churches_for_membros(request.user, ministerio)
    igreja_ativa = getattr(request, 'igreja_ativa', None)

    if igreja_ativa:
        if igrejas_permitidas.filter(pk=igreja_ativa.pk).exists():
            return Membro.objects.filter(igreja=igreja_ativa)
        return Membro.objects.none()

    return Membro.objects.filter(igreja__in=igrejas_permitidas)


# ---------------------------------------------------------------------------
# Helper de instanciação segura de MembroForm
# ---------------------------------------------------------------------------

def safe_instantiate_membroform(*args, **kwargs):
    extras = ('ministerio', 'user', 'allowed_churches', 'igreja_inicial')
    try:
        return MembroForm(*args, **kwargs)
    except TypeError as e:
        # try remove known extras and instantiate
        filtered = kwargs.copy()
        for k in extras:
            filtered.pop(k, None)
        try:
            inst = MembroForm(*args, **filtered)
        except TypeError:
            # last-resort: call without kwargs
            try:
                inst = MembroForm(*args[:2]) if args else MembroForm()
            except Exception:
                inst = MembroForm()

        # apply minimal post-init adjustments expected by views
        try:
            ministerio = kwargs.get('ministerio')
            user = kwargs.get('user')
            allowed_churches = kwargs.get('allowed_churches')
            igreja_inicial = kwargs.get('igreja_inicial')
            if hasattr(inst, 'fields'):
                if 'igreja' in inst.fields:
                    try:
                        if user and not is_admin_org(user) and allowed_churches is not None:
                            inst.fields['igreja'].queryset = allowed_churches
                        elif ministerio:
                            inst.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')
                        else:
                            inst.fields['igreja'].queryset = Igreja.objects.none()
                    except Exception as exc:
                        logger.debug('safe_instantiate_membroform: falha ao configurar queryset de igreja: %s', exc)
                    try:
                        if igreja_inicial and getattr(inst.fields['igreja'].queryset, 'filter', None):
                            if inst.fields['igreja'].queryset.filter(pk=igreja_inicial.pk).exists():
                                inst.initial.setdefault('igreja', igreja_inicial)
                                inst.fields['igreja'].disabled = True
                    except Exception as exc:
                        logger.debug('safe_instantiate_membroform: falha ao aplicar igreja inicial: %s', exc)
                if 'tipo_pessoa' in inst.fields:
                    try:
                        inst.fields['tipo_pessoa'].queryset = TipoPessoa.objects.all().order_by('nome')
                    except Exception as exc:
                        logger.debug('safe_instantiate_membroform: falha ao configurar tipo_pessoa: %s', exc)
                if 'status_pessoa' in inst.fields:
                    try:
                        inst.fields['status_pessoa'].queryset = StatusPessoa.objects.all().order_by('nome')
                    except Exception as exc:
                        logger.debug('safe_instantiate_membroform: falha ao configurar status_pessoa: %s', exc)
        except Exception as exc:
            logger.warning('safe_instantiate_membroform: falha em ajuste pós-init do formulário: %s', exc)
        return inst


# ---------------------------------------------------------------------------
# Helper de navegação entre membros
# ---------------------------------------------------------------------------

def _get_navigation_context(membro_id, igreja_ativa):
    """
    Helper para obter contexto de navegação entre membros.
    Retorna: dict com prev_id, next_id, current_position, total_count, membros_lista

    NOTA: Exclui apenas pessoas INATIVAS (falecidos, mudados definitivamente).
    Disciplinados, desligados e outros status ainda aparecem pois podem precisar edição.
    """
    # Robustez: só filtra se igreja_ativa for válida
    igreja_ativa_obj = None
    if igreja_ativa is None:
        membros_permitidos = []
    elif hasattr(igreja_ativa, 'first'):
        igreja_ativa_obj = igreja_ativa.first()
    elif isinstance(igreja_ativa, (list, tuple)):
        igreja_ativa_obj = igreja_ativa[0] if igreja_ativa else None
    else:
        igreja_ativa_obj = igreja_ativa
    if igreja_ativa_obj:
        membros_permitidos = Membro.objects.filter(
            igreja=igreja_ativa_obj
        ).exclude(
            status_pessoa__nome='Inativo'  # Exclui apenas inativos
        ).order_by('nome').values_list('pk', 'nome')
    else:
        membros_permitidos = []

    # Converte para lista para facilitar navegação
    membros_lista = list(membros_permitidos)
    total_count = len(membros_lista)

    # Encontra índice do membro atual
    current_index = None
    for idx, (pk, nome) in enumerate(membros_lista):
        if pk == membro_id:
            current_index = idx
            break

    # Determina anterior e próximo
    prev_id = None
    next_id = None
    current_position = 0

    if current_index is not None:
        current_position = current_index + 1
        if current_index > 0:
            prev_id = membros_lista[current_index - 1][0]
        if current_index < total_count - 1:
            next_id = membros_lista[current_index + 1][0]

    return {
        'prev_id': prev_id,
        'next_id': next_id,
        'current_position': current_position,
        'total_count': total_count,
        'membros_lista': membros_lista,
    }
