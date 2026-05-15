"""Transcripts resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio.models._base import PaginatedResponse
from attio.models.transcripts import TranscriptSegment
from attio.resources._base import AsyncResource, SyncResource


class _TranscriptsMixin:
    """Shared parameter/body construction logic for the Transcripts resource."""

    @staticmethod
    def _build_params(
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        return params

    @staticmethod
    def _parse_paginated_response(
        raw: dict[str, Any],
    ) -> PaginatedResponse[TranscriptSegment]:
        return PaginatedResponse[TranscriptSegment].model_validate(raw)


class TranscriptsResource(SyncResource, _TranscriptsMixin):
    """Synchronous Transcripts resource."""

    def get(
        self,
        meeting_id: str,
        recording_id: str,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> PaginatedResponse[TranscriptSegment]:
        """Get a transcript for a call recording."""
        params = self._build_params(limit=limit, cursor=cursor)
        raw = self._http.request(
            "GET",
            f"/meetings/{meeting_id}/call_recordings/{recording_id}/transcript",
            params=params,
        )
        return self._parse_paginated_response(raw)


class AsyncTranscriptsResource(AsyncResource, _TranscriptsMixin):
    """Asynchronous Transcripts resource."""

    async def get(
        self,
        meeting_id: str,
        recording_id: str,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> PaginatedResponse[TranscriptSegment]:
        """Get a transcript for a call recording."""
        params = self._build_params(limit=limit, cursor=cursor)
        raw = await self._http.request(
            "GET",
            f"/meetings/{meeting_id}/call_recordings/{recording_id}/transcript",
            params=params,
        )
        return self._parse_paginated_response(raw)
