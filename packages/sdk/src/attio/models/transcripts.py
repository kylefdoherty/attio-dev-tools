"""Models for the Transcripts resource."""

from __future__ import annotations

from attio.models._base import AttioModel


class TranscriptSegment(AttioModel):
    """A single segment of a transcript."""

    speech: str
    start_time: float
    end_time: float
    speaker: str | None = None
