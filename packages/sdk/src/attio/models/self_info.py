"""Models for the Self / Identify endpoint."""

from __future__ import annotations

from attio.models._base import AttioModel


class SelfInfo(AttioModel):
    """Information about the current API token and workspace."""

    active: bool | None = None
    scope: str | None = None
    client_id: str | None = None
    token_type: str | None = None
    exp: int | None = None
    iat: int | None = None
    sub: str | None = None
    aud: str | None = None
    iss: str | None = None
    authorized_by_workspace_member_id: str | None = None
    workspace_id: str | None = None
    workspace_name: str | None = None
    workspace_slug: str | None = None
    workspace_logo_url: str | None = None
