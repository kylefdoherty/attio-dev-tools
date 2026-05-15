"""Common models shared across multiple resources."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel


class ActorReference(AttioModel):
    """Reference to an actor (API token, workspace member, system, or app)."""

    id: str | None = None
    type: str  # "api-token" | "workspace-member" | "system" | "app"


class AttributeValue(AttioModel):
    """A single attribute value entry. Type-specific fields are captured by extra='allow'."""

    active_from: datetime
    active_until: datetime | None = None
    created_by_actor: ActorReference
    attribute_type: str
