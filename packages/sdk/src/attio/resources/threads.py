"""Threads resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio.models._base import DataWrapper, ListResponse
from attio.models.threads import Thread
from attio.resources._base import AsyncResource, SyncResource


class _ThreadsMixin:
    """Shared parameter/body construction logic for the Threads resource."""

    @staticmethod
    def _build_query_params(
        *,
        record_id: str | None = None,
        object: str | None = None,
        entry_id: str | None = None,
        list: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if record_id is not None:
            params["record_id"] = record_id
        if object is not None:
            params["object"] = object
        if entry_id is not None:
            params["entry_id"] = entry_id
        if list is not None:
            params["list"] = list
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return params

    @staticmethod
    def _parse_list_response(raw: dict[str, Any]) -> ListResponse[Thread]:
        return ListResponse[Thread].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> Thread:
        wrapper = DataWrapper[Thread].model_validate(raw)
        return wrapper.data


class ThreadsResource(SyncResource, _ThreadsMixin):
    """Synchronous Threads resource."""

    def list(
        self,
        *,
        record_id: str | None = None,
        object: str | None = None,
        entry_id: str | None = None,
        list: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Thread]:
        """List threads, optionally filtered by record or entry."""
        params = self._build_query_params(
            record_id=record_id,
            object=object,
            entry_id=entry_id,
            list=list,
            limit=limit,
            offset=offset,
        )
        raw = self._http.request("GET", "/threads", params=params)
        return self._parse_list_response(raw)

    def get(self, thread_id: str) -> Thread:
        """Get a single thread by ID."""
        raw = self._http.request("GET", f"/threads/{thread_id}")
        return self._parse_single_response(raw)


class AsyncThreadsResource(AsyncResource, _ThreadsMixin):
    """Asynchronous Threads resource."""

    async def list(
        self,
        *,
        record_id: str | None = None,
        object: str | None = None,
        entry_id: str | None = None,
        list: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Thread]:
        """List threads, optionally filtered by record or entry."""
        params = self._build_query_params(
            record_id=record_id,
            object=object,
            entry_id=entry_id,
            list=list,
            limit=limit,
            offset=offset,
        )
        raw = await self._http.request("GET", "/threads", params=params)
        return self._parse_list_response(raw)

    async def get(self, thread_id: str) -> Thread:
        """Get a single thread by ID."""
        raw = await self._http.request("GET", f"/threads/{thread_id}")
        return self._parse_single_response(raw)
