"""Pydantic models for the Entries resource."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel
from attio.models.common import AttributeValue


class EntryId(AttioModel):
    """Unique identifier for a list entry."""

    workspace_id: str
    list_id: str
    entry_id: str


class Entry(AttioModel):
    """An entry within a list (e.g., a deal in a sales pipeline)."""

    id: EntryId
    parent_record_id: str
    parent_object: str
    created_at: datetime
    entry_values: dict[str, list[AttributeValue]]
