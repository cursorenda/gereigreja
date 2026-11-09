"""Prepare Pessoa photo references before the database write."""

import re
from dataclasses import dataclass
from typing import Literal
from uuid import uuid4


@dataclass(frozen=True)
class _PessoaPhotoAttempt:
    intent: Literal["NONE", "NEW", "REPLACE", "CLEAR"]
    using: str
    previous_db_key: str | None = None
    final_storage_key: str | None = None
    attempt_id: str | None = None
    managed_candidate_key: str | None = None
    cleanup_eligible: bool = False


def prepare_pessoa_photo(pessoa, *, using):
    """Materialize a pending upload and bind its committed key without saving Pessoa."""
    field = pessoa._meta.get_field("foto")
    attname = field.attname
    if attname not in pessoa.__dict__:
        return _PessoaPhotoAttempt("NONE", using)

    previous_key = None
    if not pessoa._state.adding:
        previous_key = (
            type(pessoa)._base_manager.using(using)
            .values_list(attname, flat=True).get(pk=pessoa.pk)
        ) or None

    entry_photo = pessoa.__dict__[attname]
    photo = getattr(pessoa, attname)
    if photo._committed:
        return _PessoaPhotoAttempt(
            "CLEAR" if previous_key and not photo.name else "NONE",
            using,
            previous_key,
            photo.name or None,
        )

    stream = photo.file
    try:
        position = stream.tell()
    except (AttributeError, OSError, ValueError):
        position = None

    attempt_id = uuid4().hex
    basename = (photo.name or "").replace("\\", "/").rsplit("/", 1)[-1]
    suffix = re.search(r"\.[a-zA-Z0-9]{1,10}\Z", basename)
    extension = suffix.group().lower() if suffix else ""
    try:
        candidate = field.generate_filename(pessoa, f"_managed/{attempt_id}{extension}").replace("\\", "/")
        final_key = field.storage.save(candidate, stream, max_length=field.max_length)
    except Exception:
        pessoa.__dict__[attname] = entry_photo
        if position is not None:
            try:
                stream.seek(position)
            except Exception:
                # A failed rewind must not hide the original storage error.
                pass
        raise

    setattr(pessoa, attname, final_key)
    return _PessoaPhotoAttempt(
        "REPLACE" if previous_key else "NEW",
        using,
        previous_key,
        final_key,
        attempt_id,
        candidate,
    )
