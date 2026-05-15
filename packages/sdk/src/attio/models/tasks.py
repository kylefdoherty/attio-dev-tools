"""Models for the Tasks resource."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel
from attio.models.common import ActorReference


class TaskId(AttioModel):
    """Identifier for an Attio task."""

    workspace_id: str
    task_id: str


class LinkedRecord(AttioModel):
    """A record linked to a task."""

    target_object: str
    target_record_id: str


class TaskAssignee(AttioModel):
    """An assignee of a task."""

    referenced_actor_type: str
    referenced_actor_id: str


class Task(AttioModel):
    """Represents an Attio task."""

    id: TaskId
    content_plaintext: str
    content_markdown: str | None = None
    format: str
    is_completed: bool
    completed_at: datetime | None = None
    deadline_at: datetime | None = None
    linked_records: list[LinkedRecord]
    assignees: list[TaskAssignee]
    created_by_actor: ActorReference
    created_at: datetime
