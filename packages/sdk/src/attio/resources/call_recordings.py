"""Call Recordings resource implementation (sync and async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attio.models._base import DataWrapper, PaginatedResponse
from attio.models.call_recordings import CallRecording
from attio.resources._base import AsyncResource, SyncResource

if TYPE_CHECKING:
    from attio._pagination import AsyncCursorIterator, CursorIterator


class _CallRecordingsMixin:
    """Shared parameter/body construction logic for the Call Recordings resource."""

    @staticmethod
    def _build_list_params(
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
    def _build_create_body(*, video_url: str) -> dict[str, Any]:
        return {"data": {"video_url": video_url}}

    @staticmethod
    def _parse_paginated_response(raw: dict[str, Any]) -> PaginatedResponse[CallRecording]:
        return PaginatedResponse[CallRecording].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> CallRecording:
        wrapper = DataWrapper[CallRecording].model_validate(raw)
        return wrapper.data


class CallRecordingsResource(SyncResource, _CallRecordingsMixin):
    """Synchronous Call Recordings resource."""

    def list(
        self,
        meeting_id: str,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> PaginatedResponse[CallRecording]:
        """List call recordings for a meeting."""
        params = self._build_list_params(limit=limit, cursor=cursor)
        raw = self._http.request(
            "GET",
            f"/meetings/{meeting_id}/call_recordings",
            params=params,
        )
        return self._parse_paginated_response(raw)

    def get(self, meeting_id: str, recording_id: str) -> CallRecording:
        """Get a single call recording."""
        raw = self._http.request(
            "GET",
            f"/meetings/{meeting_id}/call_recordings/{recording_id}",
        )
        return self._parse_single_response(raw)

    def create(self, meeting_id: str, *, video_url: str) -> CallRecording:
        """Create a call recording for a meeting.

        ALPHA: this endpoint is in alpha and may be subject to breaking
        changes. Rate limited to 1 request per second.

        ``video_url`` must be a publicly accessible HTTPS URL to a ``.mp4``
        file no larger than 500MB; Attio downloads the video asynchronously
        (the returned recording starts with ``status="processing"``). The URL
        must answer a HEAD request with a ``Content-Length`` header.
        """
        body = self._build_create_body(video_url=video_url)
        raw = self._http.request(
            "POST",
            f"/meetings/{meeting_id}/call_recordings",
            json=body,
        )
        return self._parse_single_response(raw)

    def delete(self, meeting_id: str, recording_id: str) -> None:
        """Delete a call recording and all associated data.

        ALPHA: this endpoint is in alpha and may be subject to breaking
        changes.
        """
        self._http.request(
            "DELETE",
            f"/meetings/{meeting_id}/call_recordings/{recording_id}",
        )

    def list_all(
        self,
        meeting_id: str,
        *,
        limit: int | None = None,
    ) -> CursorIterator[CallRecording]:
        """Auto-paginate all call recordings for a meeting. Returns an iterator over all recordings."""
        from attio._pagination import CursorIterator

        def fetch_page(cursor: str | None) -> PaginatedResponse[CallRecording]:
            return self.list(meeting_id, limit=limit, cursor=cursor)

        return CursorIterator(fetch_page=fetch_page)


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncCallRecordingsResource(AsyncResource, _CallRecordingsMixin):
    """Asynchronous Call Recordings resource."""

    async def list(
        self,
        meeting_id: str,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> PaginatedResponse[CallRecording]:
        """List call recordings for a meeting."""
        params = self._build_list_params(limit=limit, cursor=cursor)
        raw = await self._http.request(
            "GET",
            f"/meetings/{meeting_id}/call_recordings",
            params=params,
        )
        return self._parse_paginated_response(raw)

    async def get(self, meeting_id: str, recording_id: str) -> CallRecording:
        """Get a single call recording."""
        raw = await self._http.request(
            "GET",
            f"/meetings/{meeting_id}/call_recordings/{recording_id}",
        )
        return self._parse_single_response(raw)

    async def create(self, meeting_id: str, *, video_url: str) -> CallRecording:
        """Create a call recording for a meeting.

        ALPHA: this endpoint is in alpha and may be subject to breaking
        changes. Rate limited to 1 request per second.

        ``video_url`` must be a publicly accessible HTTPS URL to a ``.mp4``
        file no larger than 500MB; Attio downloads the video asynchronously
        (the returned recording starts with ``status="processing"``). The URL
        must answer a HEAD request with a ``Content-Length`` header.
        """
        body = self._build_create_body(video_url=video_url)
        raw = await self._http.request(
            "POST",
            f"/meetings/{meeting_id}/call_recordings",
            json=body,
        )
        return self._parse_single_response(raw)

    async def delete(self, meeting_id: str, recording_id: str) -> None:
        """Delete a call recording and all associated data.

        ALPHA: this endpoint is in alpha and may be subject to breaking
        changes.
        """
        await self._http.request(
            "DELETE",
            f"/meetings/{meeting_id}/call_recordings/{recording_id}",
        )

    def list_all(
        self,
        meeting_id: str,
        *,
        limit: int | None = None,
    ) -> AsyncCursorIterator[CallRecording]:
        """Auto-paginate all call recordings for a meeting. Returns an async iterator over all recordings."""
        from attio._pagination import AsyncCursorIterator

        async def fetch_page(cursor: str | None) -> PaginatedResponse[CallRecording]:
            return await self.list(meeting_id, limit=limit, cursor=cursor)

        return AsyncCursorIterator(fetch_page=fetch_page)
