"""Models for the Webhooks resource."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from attio.models._base import AttioModel


class WebhookEventType(StrEnum):
    """Enumeration of all supported Attio webhook event types."""

    RECORD_CREATED = "record.created"
    RECORD_UPDATED = "record.updated"
    RECORD_DELETED = "record.deleted"
    RECORD_MERGED = "record.merged"
    LIST_ENTRY_CREATED = "list-entry.created"
    LIST_ENTRY_UPDATED = "list-entry.updated"
    LIST_ENTRY_DELETED = "list-entry.deleted"
    LIST_CREATED = "list.created"
    LIST_UPDATED = "list.updated"
    LIST_DELETED = "list.deleted"
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    NOTE_CREATED = "note.created"
    NOTE_UPDATED = "note.updated"
    NOTE_DELETED = "note.deleted"
    NOTE_CONTENT_UPDATED = "note-content.updated"
    COMMENT_CREATED = "comment.created"
    COMMENT_DELETED = "comment.deleted"
    COMMENT_RESOLVED = "comment.resolved"
    COMMENT_UNRESOLVED = "comment.unresolved"
    OBJECT_ATTRIBUTE_CREATED = "object-attribute.created"
    OBJECT_ATTRIBUTE_UPDATED = "object-attribute.updated"
    LIST_ATTRIBUTE_CREATED = "list-attribute.created"
    LIST_ATTRIBUTE_UPDATED = "list-attribute.updated"
    WORKSPACE_MEMBER_CREATED = "workspace-member.created"
    CALL_RECORDING_CREATED = "call-recording.created"


class WebhookSubscription(AttioModel):
    """A subscription entry for a webhook."""

    event_type: str
    filter: dict[str, Any] | None = None


class WebhookId(AttioModel):
    """Identifier for an Attio webhook."""

    workspace_id: str
    webhook_id: str


class Webhook(AttioModel):
    """Represents an Attio webhook configuration."""

    id: WebhookId
    target_url: str
    subscriptions: list[WebhookSubscription]
    status: str  # "active" | "paused"
    secret: str | None = None  # only present in create response
    created_at: datetime
