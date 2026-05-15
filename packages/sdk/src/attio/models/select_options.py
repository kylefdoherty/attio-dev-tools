"""Models for the Select Options and Statuses resources."""

from __future__ import annotations

from attio.models._base import AttioModel


class SelectOptionId(AttioModel):
    """Identifier for a select option."""

    workspace_id: str
    object_id: str
    attribute_id: str
    option_id: str


class SelectOption(AttioModel):
    """Represents a select option on an attribute."""

    id: SelectOptionId
    title: str
    is_archived: bool


class StatusId(AttioModel):
    """Identifier for a status."""

    workspace_id: str
    object_id: str
    attribute_id: str
    status_id: str


class Status(AttioModel):
    """Represents a status on an attribute."""

    id: StatusId
    title: str
    is_archived: bool
    celebration_enabled: bool
    target_time_in_status: str | None = None
