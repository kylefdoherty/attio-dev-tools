"""Models for the Lists resource."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from attio.models._base import AttioModel
from attio.models.common import ActorReference


class ListId(AttioModel):
    """Identifier for an Attio list."""

    workspace_id: str
    list_id: str


class AttioList(AttioModel):
    """Represents an Attio list. Named AttioList to avoid shadowing the built-in list."""

    id: ListId
    api_slug: str
    name: str
    parent_object: list[str] | str
    workspace_access: str | None = None
    workspace_member_access: list[Any] | str | None = None
    created_by_actor: ActorReference
    created_at: datetime
