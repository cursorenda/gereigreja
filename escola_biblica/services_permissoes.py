"""Regras de autorização da Escola Bíblica."""

import logging

from contas.constants import (
    SECRETARIA_EBD,
    SUPERINTENDENTE_EBD,
    user_has_permission_level_or_higher,
    user_tem_grupo,
)
from secretaria.models import MembroCargo

from .models import Turma


logger = logging.getLogger(__name__)


def usuario_pode_gerenciar_ebd(user):
    """Distingue a Secretaria EBD do professor, apesar do mesmo nível global."""
    return (
        user.is_superuser
        or user_tem_grupo(user, SECRETARIA_EBD)
        or user_has_permission_level_or_higher(user, SUPERINTENDENTE_EBD)
    )


def _membro_e_professor_ebd_ativo(membro):
    return MembroCargo.objects.filter(
        membro=membro,
        cargo__is_ebd=True,
        cargo__nome__icontains='professor',
        data_fim__isnull=True,
    ).exists()


def pode_acessar_chamada_turma(user, turma):
    if usuario_pode_gerenciar_ebd(user):
        return True
    try:
        membro = getattr(user, 'membro_secretaria', None)
        return bool(membro and turma.membros.filter(pk=membro.pk).exists() and _membro_e_professor_ebd_ativo(membro))
    except Exception as exc:
        logger.warning('Falha ao validar acesso de chamada da turma para user=%s: %s', user.pk, exc)
        return False


def get_turmas_professor(user):
    try:
        membro = getattr(user, 'membro_secretaria', None)
        if membro and _membro_e_professor_ebd_ativo(membro):
            return Turma.objects.filter(membros=membro)
    except Exception as exc:
        logger.warning('Falha ao buscar turmas do professor para user=%s: %s', user.pk, exc)
    return Turma.objects.none()


def filtrar_turmas_para_usuario(turmas, user):
    """Restringe uma consulta de turmas ao escopo operacional do usuário."""
    if usuario_pode_gerenciar_ebd(user):
        return turmas
    return turmas.filter(id__in=get_turmas_professor(user).values('id'))


def filtrar_queryset_por_turmas_do_usuario(*, queryset, user, campo_turma):
    """Restringe registros relacionados a turma quando o usuario nao gerencia a EBD."""
    if usuario_pode_gerenciar_ebd(user):
        return queryset
    return queryset.filter(**{f'{campo_turma}__in': get_turmas_professor(user)})


def pode_ver_aluno(user, aluno):
    return usuario_pode_gerenciar_ebd(user) or pode_acessar_chamada_turma(user, aluno.turma)
