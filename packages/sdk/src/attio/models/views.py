"""Models for the Views resource."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel


class ViewId(AttioModel):
    """Identifier for an Attio view."""

    workspace_id: str
    object_id: str | None = None
    list_id: str | None = None
    view_id: str


class View(AttioModel):
    """Represents an Attio view (for objects or lists)."""

    id: ViewId
    title: str
    created_at: datetime
