"""Call Recordings resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio.models._base import DataWrapper, PaginatedResponse
from attio.models.call_recordings import CallRecording
from attio.resources._base import AsyncResource, SyncResource


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
