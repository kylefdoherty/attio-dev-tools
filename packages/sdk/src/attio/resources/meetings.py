"""Meetings resource implementation (sync and async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

from attio.models._base import DataWrapper, PaginatedResponse
from attio.models.meetings import Meeting
from attio.resources._base import AsyncResource, SyncResource

if TYPE_CHECKING:
    from attio._pagination import AsyncCursorIterator, CursorIterator


class _MeetingsMixin:
    """Shared parameter/body construction logic for the Meetings resource."""

    @staticmethod
    def _build_list_params(
        *,
        limit: int | None = None,
        cursor: str | None = None,
        linked_object: str | None = None,
        linked_record_id: str | None = None,
        participants: str | list[str] | None = None,
        sort: str | None = None,
        ends_from: str | None = None,
        starts_before: str | None = None,
        timezone: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if linked_object is not None:
            params["linked_object"] = linked_object
        if linked_record_id is not None:
            params["linked_record_id"] = linked_record_id
        if participants is not None:
            if isinstance(participants, list):
                params["participants"] = ",".join(participants)
            else:
                params["participants"] = participants
        if sort is not None:
            params["sort"] = sort
        if ends_from is not None:
            params["ends_from"] = ends_from
        if starts_before is not None:
            params["starts_before"] = starts_before
        if timezone is not None:
            params["timezone"] = timezone
        return params

    @staticmethod
    def _build_create_body(
        *,
        title: str,
        description: str,
        start: dict[str, Any],
        end: dict[str, Any],
        is_all_day: bool,
        participants: list[dict[str, Any]],
        external_ref: Union[str, dict[str, Any]],
        linked_records: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "title": title,
            "description": description,
            "start": start,
            "end": end,
            "is_all_day": is_all_day,
            "participants": participants,
            "external_ref": external_ref,
        }
        if linked_records is not None:
            data["linked_records"] = linked_records
        return {"data": data}

    @staticmethod
    def _parse_paginated_response(raw: dict[str, Any]) -> PaginatedResponse[Meeting]:
        return PaginatedResponse[Meeting].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> Meeting:
        wrapper = DataWrapper[Meeting].model_validate(raw)
        return wrapper.data


class MeetingsResource(SyncResource, _MeetingsMixin):
    """Synchronous Meetings resource."""

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        linked_object: str | None = None,
        linked_record_id: str | None = None,
        participants: str | list[str] | None = None,
        sort: str | None = None,
        ends_from: str | None = None,
        starts_before: str | None = None,
        timezone: str | None = None,
    ) -> PaginatedResponse[Meeting]:
        """List meetings."""
        params = self._build_list_params(
            limit=limit,
            cursor=cursor,
            linked_object=linked_object,
            linked_record_id=linked_record_id,
            participants=participants,
            sort=sort,
            ends_from=ends_from,
            starts_before=starts_before,
            timezone=timezone,
        )
        raw = self._http.request("GET", "/meetings", params=params)
        return self._parse_paginated_response(raw)

    def get(self, meeting_id: str) -> Meeting:
        """Get a single meeting by ID."""
        raw = self._http.request("GET", f"/meetings/{meeting_id}")
        return self._parse_single_response(raw)

    def create(
        self,
        *,
        title: str,
        description: str,
        start: dict[str, Any],
        end: dict[str, Any],
        is_all_day: bool,
        participants: list[dict[str, Any]],
        external_ref: Union[str, dict[str, Any]],
        linked_records: list[dict[str, str]] | None = None,
    ) -> Meeting:
        """Find or create a meeting (find-or-create semantics).

        ALPHA: this endpoint is in alpha and may be subject to breaking
        changes. Uses ``external_ref`` to de-duplicate meetings across calls.

        ``start`` / ``end`` take ``{"datetime": ..., "timezone": ...}`` for
        non-all-day meetings or ``{"date": ...}`` for all-day meetings
        (``end`` is exclusive). Each participant requires ``email_address``,
        ``is_organizer``, and ``status``; person/company records are
        auto-created and linked from participant email addresses.
        """
        body = self._build_create_body(
            title=title,
            description=description,
            start=start,
            end=end,
            is_all_day=is_all_day,
            participants=participants,
            external_ref=external_ref,
            linked_records=linked_records,
        )
        raw = self._http.request("POST", "/meetings", json=body)
        return self._parse_single_response(raw)

    def list_all(
        self,
        *,
        limit: int | None = None,
        linked_object: str | None = None,
        linked_record_id: str | None = None,
        participants: str | list[str] | None = None,
        sort: str | None = None,
        ends_from: str | None = None,
        starts_before: str | None = None,
        timezone: str | None = None,
    ) -> CursorIterator[Meeting]:
        """Auto-paginate all meetings. Returns an iterator over all meetings."""
        from attio._pagination import CursorIterator

        def fetch_page(cursor: str | None) -> PaginatedResponse[Meeting]:
            return self.list(
                limit=limit,
                cursor=cursor,
                linked_object=linked_object,
                linked_record_id=linked_record_id,
                participants=participants,
                sort=sort,
                ends_from=ends_from,
                starts_before=starts_before,
                timezone=timezone,
            )

        return CursorIterator(fetch_page=fetch_page)


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncMeetingsResource(AsyncResource, _MeetingsMixin):
    """Asynchronous Meetings resource."""

    async def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        linked_object: str | None = None,
        linked_record_id: str | None = None,
        participants: str | list[str] | None = None,
        sort: str | None = None,
        ends_from: str | None = None,
        starts_before: str | None = None,
        timezone: str | None = None,
    ) -> PaginatedResponse[Meeting]:
        """List meetings."""
        params = self._build_list_params(
            limit=limit,
            cursor=cursor,
            linked_object=linked_object,
            linked_record_id=linked_record_id,
            participants=participants,
            sort=sort,
            ends_from=ends_from,
            starts_before=starts_before,
            timezone=timezone,
        )
        raw = await self._http.request("GET", "/meetings", params=params)
        return self._parse_paginated_response(raw)

    async def get(self, meeting_id: str) -> Meeting:
        """Get a single meeting by ID."""
        raw = await self._http.request("GET", f"/meetings/{meeting_id}")
        return self._parse_single_response(raw)

    async def create(
        self,
        *,
        title: str,
        description: str,
        start: dict[str, Any],
        end: dict[str, Any],
        is_all_day: bool,
        participants: list[dict[str, Any]],
        external_ref: Union[str, dict[str, Any]],
        linked_records: list[dict[str, str]] | None = None,
    ) -> Meeting:
        """Find or create a meeting (find-or-create semantics).

        ALPHA: this endpoint is in alpha and may be subject to breaking
        changes. Uses ``external_ref`` to de-duplicate meetings across calls.

        ``start`` / ``end`` take ``{"datetime": ..., "timezone": ...}`` for
        non-all-day meetings or ``{"date": ...}`` for all-day meetings
        (``end`` is exclusive). Each participant requires ``email_address``,
        ``is_organizer``, and ``status``; person/company records are
        auto-created and linked from participant email addresses.
        """
        body = self._build_create_body(
            title=title,
            description=description,
            start=start,
            end=end,
            is_all_day=is_all_day,
            participants=participants,
            external_ref=external_ref,
            linked_records=linked_records,
        )
        raw = await self._http.request("POST", "/meetings", json=body)
        return self._parse_single_response(raw)

    def list_all(
        self,
        *,
        limit: int | None = None,
        linked_object: str | None = None,
        linked_record_id: str | None = None,
        participants: str | list[str] | None = None,
        sort: str | None = None,
        ends_from: str | None = None,
        starts_before: str | None = None,
        timezone: str | None = None,
    ) -> AsyncCursorIterator[Meeting]:
        """Auto-paginate all meetings. Returns an async iterator over all meetings."""
        from attio._pagination import AsyncCursorIterator

        async def fetch_page(cursor: str | None) -> PaginatedResponse[Meeting]:
            return await self.list(
                limit=limit,
                cursor=cursor,
                linked_object=linked_object,
                linked_record_id=linked_record_id,
                participants=participants,
                sort=sort,
                ends_from=ends_from,
                starts_before=starts_before,
                timezone=timezone,
            )

        return AsyncCursorIterator(fetch_page=fetch_page)
