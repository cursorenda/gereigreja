from django.contrib.auth.models import Group


def _coletar_ids_grupos(grupos):
    if grupos is None:
        return None

    if hasattr(grupos, 'values_list'):
        return set(grupos.values_list('id', flat=True))

    ids = set()
    for grupo in grupos:
        if isinstance(grupo, int):
            ids.add(grupo)
        else:
            grupo_id = getattr(grupo, 'id', None)
            if grupo_id is not None:
                ids.add(grupo_id)
    return ids


def grupos_por_cargo_ativo(user):
    """Retorna ids de grupos derivados dos cargos ativos do usuario."""
    if not user:
        return set()

    # Import local para evitar ciclo entre apps no carregamento do Django.
    from secretaria.models import MembroCargo

    return set(
        MembroCargo.objects.filter(
            membro__usuario=user,
            data_fim__isnull=True,
            cargo__grupo_permissao__isnull=False,
        )
        .values_list('cargo__grupo_permissao_id', flat=True)
        .distinct()
    )


def grupos_reservados_para_cargo():
    """Retorna ids de grupos usados por pelo menos um cargo cadastrado."""
    # Import local para evitar ciclo entre apps no carregamento do Django.
    from secretaria.models import Cargo

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
    """
    Recalcula grupos efetivos preservando grupos de cargo ativo e grupos manuais.

    Regra:
    grupos_efetivos = grupos_por_cargo_ativo U grupos_manuais

    Quando ``grupos_editaveis`` e informado, apenas esses grupos manuais sao
    substituidos; os demais grupos manuais existentes continuam preservados.
    """
    if not user:
        return Group.objects.none()

    ids_cargo = grupos_por_cargo_ativo(user)
    ids_atuais = set(user.groups.values_list('id', flat=True))
    ids_manuais_atuais = ids_atuais - ids_cargo
    ids_reservados_cargo = set()

    if ignorar_grupos_reservados_no_manual:
        ids_reservados_cargo = grupos_reservados_para_cargo()
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
