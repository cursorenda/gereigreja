"""Pure domain rules for the future authoritative event services.

Mutation boundaries will cover Evento writes, ParticipacaoEvento transitions,
and EBD lesson-to-event linking. Existing callers retain their current paths.
"""

from dataclasses import dataclass
from enum import Enum

from django.core.exceptions import ValidationError


@dataclass(frozen=True)
class ParticipationReferences:
    event_id: int
    # None means the participation has no session.
    session_event_id: int | None = None


class ParticipationTransition(Enum):
    CONSISTENT = "consistent"
    NEW_DIVERGENT_STATE = "new_divergent_state"
    PRESERVED_DIVERGENT_STATE = "preserved_divergent_state"
    REPAIR_TO_CONSISTENT_STATE = "repair_to_consistent_state"
    EXPLICIT_DELETE = "explicit_delete"


def _is_divergent(references: ParticipationReferences | None) -> bool:
    return (
        references is not None
        and references.session_event_id is not None
        and references.session_event_id != references.event_id
    )


def classify_participation_transition(
    *,
    previous: ParticipationReferences | None = None,
    proposed: ParticipationReferences | None,
) -> ParticipationTransition:
    """Classify a create, update, or explicit delete from resolved references."""
    if proposed is None:
        if previous is None:
            raise ValidationError("Informe a participação a excluir.", code="missing_participation")
        return ParticipationTransition.EXPLICIT_DELETE

    was_divergent = _is_divergent(previous)
    if _is_divergent(proposed):
        if was_divergent:
            return ParticipationTransition.PRESERVED_DIVERGENT_STATE
        return ParticipationTransition.NEW_DIVERGENT_STATE
    if was_divergent:
        return ParticipationTransition.REPAIR_TO_CONSISTENT_STATE
    return ParticipationTransition.CONSISTENT


def validate_participation_transition(
    *,
    previous: ParticipationReferences | None = None,
    proposed: ParticipationReferences | None,
) -> ParticipationTransition:
    """Reject divergent writes while allowing repair or explicit deletion."""
    transition = classify_participation_transition(previous=previous, proposed=proposed)
    if transition in (
        ParticipationTransition.NEW_DIVERGENT_STATE,
        ParticipationTransition.PRESERVED_DIVERGENT_STATE,
    ):
        raise ValidationError(
            {"sessao": ValidationError(
                "A sessão deve pertencer ao evento da participação.",
                code=transition.value,
            )}
        )
    return transition


def participation_church_lock_set(
    *,
    old_event_church_id: int | None = None,
    old_session_event_church_id: int | None = None,
    new_event_church_id: int | None = None,
    new_session_event_church_id: int | None = None,
) -> list[int]:
    """Return the potential church keys in acquisition order."""
    church_ids = {
        old_event_church_id, old_session_event_church_id,
        new_event_church_id, new_session_event_church_id,
    }
    church_ids.discard(None)
    return sorted(church_ids)


def participation_scope_changed(
    *,
    old_event_church_id: int | None = None,
    old_session_event_church_id: int | None = None,
    new_event_church_id: int | None = None,
    new_session_event_church_id: int | None = None,
) -> bool:
    """Compare effective church sets, independently of reference order."""
    return participation_church_lock_set(
        old_event_church_id=old_event_church_id,
        old_session_event_church_id=old_session_event_church_id,
    ) != participation_church_lock_set(
        new_event_church_id=new_event_church_id,
        new_session_event_church_id=new_session_event_church_id,
    )
