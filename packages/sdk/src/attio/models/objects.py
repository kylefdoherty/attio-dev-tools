"""Models for the Objects resource."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel


class ObjectId(AttioModel):
    """Identifier for an Attio object."""

    workspace_id: str
    object_id: str


class Object(AttioModel):
    """Represents an Attio object (e.g., People, Companies, Deals)."""

    id: ObjectId
    api_slug: str | None = None
    singular_noun: str | None = None
    plural_noun: str | None = None
    created_at: datetime
