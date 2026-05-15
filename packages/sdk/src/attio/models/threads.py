"""Pydantic models for Threads."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel
from attio.models.comments import Comment


class ThreadId(AttioModel):
    """Identifier for a Thread."""

    workspace_id: str
    thread_id: str


class Thread(AttioModel):
    """A thread containing comments."""

    id: ThreadId
    comments: list[Comment]
    created_at: datetime
