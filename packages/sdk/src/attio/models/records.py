"""Pydantic models for the Records resource."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel
from attio.models.common import AttributeValue


class RecordId(AttioModel):
    """Unique identifier for a record."""

    workspace_id: str
    object_id: str
    record_id: str


class Record(AttioModel):
    """A record within an object (e.g., a person, company, deal)."""

    id: RecordId
    created_at: datetime
    web_url: str
    values: dict[str, list[AttributeValue]]


class RecordEntry(AttioModel):
    """An entry associated with a record (representing membership in a list)."""

    list_id: str
    list_api_slug: str
    entry_id: str
    created_at: datetime


class GlobalSearchResult(AttioModel):
    """A result from the global record search endpoint."""

    id: RecordId
    record_text: str
    record_image: str | None = None
    object_slug: str


class Sort(AttioModel):
    """Sort specification for record queries."""

    attribute: str
    direction: str  # "asc" | "desc"
    field: str | None = None
