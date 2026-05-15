"""Models for the Call Recordings resource."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel
from attio.models.common import ActorReference


class CallRecordingId(AttioModel):
    """Unique identifier for a call recording."""

    workspace_id: str
    call_recording_id: str


class CallRecording(AttioModel):
    """Represents a call recording in Attio."""

    id: CallRecordingId
    meeting_id: str
    status: str
    web_url: str | None = None
    actor: ActorReference | None = None
    created_at: datetime
