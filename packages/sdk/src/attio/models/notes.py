"""Models for the Notes resource."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel
from attio.models.common import ActorReference


class NoteId(AttioModel):
    """Identifier for an Attio note."""

    workspace_id: str
    note_id: str


class Note(AttioModel):
    """Represents an Attio note attached to a record."""

    id: NoteId
    parent_object: str
    parent_record_id: str
    title: str
    content_plaintext: str | None = None
    content_markdown: str | None = None
    format: str  # "plaintext" or "markdown"
    created_by_actor: ActorReference
    created_at: datetime
