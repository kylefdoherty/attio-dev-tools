"""Pydantic models for Comments."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel
from attio.models.common import ActorReference


class CommentId(AttioModel):
    """Identifier for a Comment."""

    workspace_id: str
    comment_id: str


class Comment(AttioModel):
    """A comment on a thread, record, or entry."""

    id: CommentId
    thread_id: str
    content_plaintext: str
    entry: dict[str, str] | None = None
    record: dict[str, str] | None = None
    resolved_at: datetime | None = None
    resolved_by: ActorReference | None = None
    created_at: datetime
    author: ActorReference
