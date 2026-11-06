from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from eventos.services import (
    ParticipationReferences,
    ParticipationTransition,
    classify_participation_transition,
    participation_church_lock_set,
    participation_scope_changed,
    validate_participation_transition,
)


class ParticipationTransitionTests(SimpleTestCase):
    def test_session_of_same_event_is_valid(self):
        self.assertEqual(
            validate_participation_transition(proposed=ParticipationReferences(1, 1)),
            ParticipationTransition.CONSISTENT,
        )

    def test_session_of_another_event_is_rejected_on_update(self):
        with self.assertRaises(ValidationError) as error:
            validate_participation_transition(
                previous=ParticipationReferences(1, 1),
                proposed=ParticipationReferences(1, 2),
            )
        self.assertEqual(error.exception.error_dict["sessao"][0].code, "new_divergent_state")

    def test_no_session_is_valid(self):
        self.assertEqual(
            validate_participation_transition(proposed=ParticipationReferences(1)),
            ParticipationTransition.CONSISTENT,
        )

    def test_new_divergent_participation_is_rejected(self):
        with self.assertRaises(ValidationError) as error:
            validate_participation_transition(proposed=ParticipationReferences(1, 2))
        self.assertEqual(error.exception.error_dict["sessao"][0].code, "new_divergent_state")

    def test_legacy_divergence_cannot_be_preserved(self):
        divergent = ParticipationReferences(1, 2)
        with self.assertRaises(ValidationError) as error:
            validate_participation_transition(previous=divergent, proposed=divergent)
        self.assertEqual(error.exception.error_dict["sessao"][0].code, "preserved_divergent_state")

    def test_legacy_repair_is_valid(self):
        self.assertEqual(
            validate_participation_transition(
                previous=ParticipationReferences(1, 2),
                proposed=ParticipationReferences(2, 2),
            ),
            ParticipationTransition.REPAIR_TO_CONSISTENT_STATE,
        )

    def test_explicit_delete_of_divergent_legacy_participation_is_valid(self):
        self.assertEqual(
            validate_participation_transition(previous=ParticipationReferences(1, 2), proposed=None),
            ParticipationTransition.EXPLICIT_DELETE,
        )

    def test_changed_legacy_divergence_is_still_rejected(self):
        previous = ParticipationReferences(1, 2)
        proposed = ParticipationReferences(3, 4)

        self.assertIs(
            classify_participation_transition(previous=previous, proposed=proposed),
            ParticipationTransition.PRESERVED_DIVERGENT_STATE,
        )
        with self.assertRaises(ValidationError) as error:
            validate_participation_transition(previous=previous, proposed=proposed)
        self.assertEqual(error.exception.error_dict["sessao"][0].code, "preserved_divergent_state")

    def test_removing_session_repairs_legacy_divergence(self):
        self.assertIs(
            validate_participation_transition(
                previous=ParticipationReferences(1, 2),
                proposed=ParticipationReferences(1),
            ),
            ParticipationTransition.REPAIR_TO_CONSISTENT_STATE,
        )

    def test_explicit_delete_of_consistent_participation(self):
        self.assertIs(
            validate_participation_transition(
                previous=ParticipationReferences(1, 1),
                proposed=None,
            ),
            ParticipationTransition.EXPLICIT_DELETE,
        )


class ParticipationScopeTests(SimpleTestCase):
    def test_lock_set_deduplicates_churches(self):
        self.assertEqual(
            participation_church_lock_set(old_event_church_id=9, new_event_church_id=9),
            [9],
        )

    def test_lock_set_ignores_nulls(self):
        self.assertEqual(participation_church_lock_set(), [])
        self.assertEqual(participation_church_lock_set(new_session_event_church_id=3), [3])

    def test_lock_set_sorts_churches(self):
        self.assertEqual(
            participation_church_lock_set(
                old_event_church_id=9, old_session_event_church_id=3, new_session_event_church_id=9,
            ),
            [3, 9],
        )

    def test_same_church_does_not_change_scope(self):
        self.assertFalse(participation_scope_changed(
            old_event_church_id=9, new_event_church_id=9, new_session_event_church_id=9,
        ))

    def test_changed_church_changes_scope(self):
        self.assertTrue(participation_scope_changed(
            old_event_church_id=9, new_event_church_id=3,
        ))


    def test_reassignment_between_distinct_events_in_same_church_preserves_scope(self):
        old_event_id, new_event_id = 10, 20
        event_church_ids = {old_event_id: 1, new_event_id: 1}

        self.assertFalse(participation_scope_changed(
            old_event_church_id=event_church_ids[old_event_id],
            new_event_church_id=event_church_ids[new_event_id],
        ))

    def test_same_church_set_in_different_reference_order_preserves_scope(self):
        self.assertFalse(participation_scope_changed(
            old_event_church_id=1, old_session_event_church_id=2,
            new_event_church_id=2, new_session_event_church_id=1,
        ))

    def test_empty_scope_to_one_church_changes_scope(self):
        self.assertTrue(participation_scope_changed(new_event_church_id=1))
