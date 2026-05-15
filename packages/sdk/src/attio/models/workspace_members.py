"""Models for the Workspace Members resource."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel


class WorkspaceMemberId(AttioModel):
    """Identifier for a workspace member."""

    workspace_id: str
    workspace_member_id: str


class WorkspaceMember(AttioModel):
    """Represents a workspace member in Attio."""

    id: WorkspaceMemberId
    first_name: str
    last_name: str
    email_address: str
    avatar_url: str | None = None
    access_level: str
    created_at: datetime
