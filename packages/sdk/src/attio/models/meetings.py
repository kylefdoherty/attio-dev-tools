"""Models for the Meetings resource."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel


class MeetingId(AttioModel):
    """Unique identifier for a meeting."""

    workspace_id: str
    meeting_id: str


class MeetingParticipant(AttioModel):
    """A participant in a meeting."""

    email_address: str | None = None
    name: str | None = None
    workspace_member_id: str | None = None


class Meeting(AttioModel):
    """Represents a meeting in Attio."""

    id: MeetingId
    title: str | None = None
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    participants: list[MeetingParticipant]
    linked_records: list[dict[str, str]]
    created_at: datetime
