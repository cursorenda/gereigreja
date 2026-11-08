"""Authoritative boundaries for explicit product mutations of events."""

from django.db import router, transaction


def delete_event(evento, *, using=None):
    """Delete this instance and its Collector effects on its write database."""
    if evento._state.adding or evento._state.db is None:
        raise ValueError("delete_event requires a persisted Evento instance.")
    using = using or router.db_for_write(type(evento), instance=evento)
    if evento._state.db is not None and evento._state.db != using:
        raise ValueError(
            f"Event alias {evento._state.db!r} conflicts with write alias {using!r}."
        )
    with transaction.atomic(using=using):
        return evento.delete(using=using)


def delete_events(eventos, *, using):
    """Delete only the supplied queryset, including its Collector effects."""
    # QuerySet.db can use a router; _db identifies an explicit .using() binding.
    queryset_alias = eventos._db
    if queryset_alias is not None and queryset_alias != using:
        raise ValueError(
            f"Queryset alias {queryset_alias!r} conflicts with write alias {using!r}."
        )
    with transaction.atomic(using=using):
        return eventos.using(using).delete()
