"""Entries resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio._pagination import AsyncOffsetIterator, OffsetIterator
from attio.models._base import DataWrapper, ListResponse
from attio.models.common import AttributeValue
from attio.models.entries import Entry
from attio.models.records import Sort
from attio.resources._base import AsyncResource, SyncResource


class _EntriesMixin:
    """Shared parameter/body construction logic for the Entries resource."""

    @staticmethod
    def _build_entry_values_body(entry_values: dict[str, Any]) -> dict[str, Any]:
        return {"data": {"entry_values": entry_values}}

    @staticmethod
    def _build_create_body(
        parent_record_id: str,
        parent_object: str,
        entry_values: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "parent_record_id": parent_record_id,
            "parent_object": parent_object,
        }
        if entry_values is not None:
            data["entry_values"] = entry_values
        return {"data": data}

    @staticmethod
    def _build_upsert_body(
        parent_record_id: str,
        parent_object: str,
        entry_values: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "parent_record_id": parent_record_id,
            "parent_object": parent_object,
        }
        if entry_values is not None:
            data["entry_values"] = entry_values
        return {"data": data}

    @staticmethod
    def _build_query_body(
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if filter is not None:
            body["filter"] = filter
        if filter_view_id is not None:
            body["filter_view_id"] = filter_view_id
        if sorts is not None:
            body["sorts"] = [s.model_dump(exclude_none=True) for s in sorts]
        if limit is not None:
            body["limit"] = limit
        if offset is not None:
            body["offset"] = offset
        return body

    @staticmethod
    def _build_list_params(
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | None:
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return params or None

    @staticmethod
    def _build_attribute_values_params(
        *,
        show_historic: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | None:
        params: dict[str, Any] = {}
        if show_historic:
            params["show_historic"] = "true"
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return params or None

    @staticmethod
    def _parse_list_response(raw: dict[str, Any]) -> ListResponse[Entry]:
        return ListResponse[Entry].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> Entry:
        wrapper = DataWrapper[Entry].model_validate(raw)
        return wrapper.data

    @staticmethod
    def _parse_attribute_values_response(
        raw: dict[str, Any],
    ) -> ListResponse[AttributeValue]:
        return ListResponse[AttributeValue].model_validate(raw)


class EntriesResource(SyncResource, _EntriesMixin):
    """Synchronous Entries resource."""

    def list(
        self,
        list_slug: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Entry]:
        """List entries for a list."""
        params = self._build_list_params(limit=limit, offset=offset)
        raw = self._http.request("GET", f"/lists/{list_slug}/entries", params=params)
        return self._parse_list_response(raw)

    def query(
        self,
        list_slug: str,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Entry]:
        """Query entries with filters and sorting."""
        body = self._build_query_body(
            filter=filter,
            filter_view_id=filter_view_id,
            sorts=sorts,
            limit=limit,
            offset=offset,
        )
        raw = self._http.request(
            "POST", f"/lists/{list_slug}/entries/query", json=body
        )
        return self._parse_list_response(raw)

    def get(self, list_slug: str, entry_id: str) -> Entry:
        """Get a single entry by ID."""
        raw = self._http.request(
            "GET", f"/lists/{list_slug}/entries/{entry_id}"
        )
        return self._parse_single_response(raw)

    def create(
        self,
        list_slug: str,
        *,
        parent_record_id: str,
        parent_object: str,
        entry_values: dict[str, Any] | None = None,
    ) -> Entry:
        """Create a new entry in a list."""
        body = self._build_create_body(parent_record_id, parent_object, entry_values)
        raw = self._http.request("POST", f"/lists/{list_slug}/entries", json=body)
        return self._parse_single_response(raw)

    def update(
        self, list_slug: str, entry_id: str, *, entry_values: dict[str, Any]
    ) -> Entry:
        """Update an entry (overwrites multiselect values)."""
        body = self._build_entry_values_body(entry_values)
        raw = self._http.request(
            "PUT", f"/lists/{list_slug}/entries/{entry_id}", json=body
        )
        return self._parse_single_response(raw)

    def append(
        self, list_slug: str, entry_id: str, *, entry_values: dict[str, Any]
    ) -> Entry:
        """Update an entry (appends to multiselect values)."""
        body = self._build_entry_values_body(entry_values)
        raw = self._http.request(
            "PATCH", f"/lists/{list_slug}/entries/{entry_id}", json=body
        )
        return self._parse_single_response(raw)

    def delete(self, list_slug: str, entry_id: str) -> None:
        """Delete an entry."""
        self._http.request(
            "DELETE", f"/lists/{list_slug}/entries/{entry_id}"
        )

    def upsert(
        self,
        list_slug: str,
        *,
        parent_record_id: str,
        parent_object: str,
        entry_values: dict[str, Any] | None = None,
    ) -> Entry:
        """Upsert an entry by parent record (create or update)."""
        body = self._build_upsert_body(parent_record_id, parent_object, entry_values)
        raw = self._http.request("PUT", f"/lists/{list_slug}/entries", json=body)
        return self._parse_single_response(raw)

    def get_attribute_values(
        self,
        list_slug: str,
        entry_id: str,
        attribute: str,
        *,
        show_historic: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[AttributeValue]:
        """Get attribute values for a specific entry and attribute."""
        params = self._build_attribute_values_params(
            show_historic=show_historic, limit=limit, offset=offset
        )
        raw = self._http.request(
            "GET",
            f"/lists/{list_slug}/entries/{entry_id}/attributes/{attribute}/values",
            params=params,
        )
        return self._parse_attribute_values_response(raw)

    def query_all(
        self,
        list_slug: str,
        *,
        filter: dict[str, Any] | None = None,
        sorts: list[Sort] | None = None,
        limit: int = 500,
    ) -> OffsetIterator[Entry]:
        """Auto-paginating version of query(). Returns an iterator over all entries."""

        def fetch_page(offset: int, page_limit: int) -> ListResponse[Entry]:
            return self.query(
                list_slug,
                filter=filter,
                sorts=sorts,
                limit=page_limit,
                offset=offset,
            )

        return OffsetIterator(fetch_page, limit=limit)


class AsyncEntriesResource(AsyncResource, _EntriesMixin):
    """Asynchronous Entries resource."""

    async def list(
        self,
        list_slug: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Entry]:
        """List entries for a list."""
        params = self._build_list_params(limit=limit, offset=offset)
        raw = await self._http.request(
            "GET", f"/lists/{list_slug}/entries", params=params
        )
        return self._parse_list_response(raw)

    async def query(
        self,
        list_slug: str,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Entry]:
        """Query entries with filters and sorting."""
        body = self._build_query_body(
            filter=filter,
            filter_view_id=filter_view_id,
            sorts=sorts,
            limit=limit,
            offset=offset,
        )
        raw = await self._http.request(
            "POST", f"/lists/{list_slug}/entries/query", json=body
        )
        return self._parse_list_response(raw)

    async def get(self, list_slug: str, entry_id: str) -> Entry:
        """Get a single entry by ID."""
        raw = await self._http.request(
            "GET", f"/lists/{list_slug}/entries/{entry_id}"
        )
        return self._parse_single_response(raw)

    async def create(
        self,
        list_slug: str,
        *,
        parent_record_id: str,
        parent_object: str,
        entry_values: dict[str, Any] | None = None,
    ) -> Entry:
        """Create a new entry in a list."""
        body = self._build_create_body(parent_record_id, parent_object, entry_values)
        raw = await self._http.request(
            "POST", f"/lists/{list_slug}/entries", json=body
        )
        return self._parse_single_response(raw)

    async def update(
        self, list_slug: str, entry_id: str, *, entry_values: dict[str, Any]
    ) -> Entry:
        """Update an entry (overwrites multiselect values)."""
        body = self._build_entry_values_body(entry_values)
        raw = await self._http.request(
            "PUT", f"/lists/{list_slug}/entries/{entry_id}", json=body
        )
        return self._parse_single_response(raw)

    async def append(
        self, list_slug: str, entry_id: str, *, entry_values: dict[str, Any]
    ) -> Entry:
        """Update an entry (appends to multiselect values)."""
        body = self._build_entry_values_body(entry_values)
        raw = await self._http.request(
            "PATCH", f"/lists/{list_slug}/entries/{entry_id}", json=body
        )
        return self._parse_single_response(raw)

    async def delete(self, list_slug: str, entry_id: str) -> None:
        """Delete an entry."""
        await self._http.request(
            "DELETE", f"/lists/{list_slug}/entries/{entry_id}"
        )

    async def upsert(
        self,
        list_slug: str,
        *,
        parent_record_id: str,
        parent_object: str,
        entry_values: dict[str, Any] | None = None,
    ) -> Entry:
        """Upsert an entry by parent record (create or update)."""
        body = self._build_upsert_body(parent_record_id, parent_object, entry_values)
        raw = await self._http.request(
            "PUT", f"/lists/{list_slug}/entries", json=body
        )
        return self._parse_single_response(raw)

    async def get_attribute_values(
        self,
        list_slug: str,
        entry_id: str,
        attribute: str,
        *,
        show_historic: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[AttributeValue]:
        """Get attribute values for a specific entry and attribute."""
        params = self._build_attribute_values_params(
            show_historic=show_historic, limit=limit, offset=offset
        )
        raw = await self._http.request(
            "GET",
            f"/lists/{list_slug}/entries/{entry_id}/attributes/{attribute}/values",
            params=params,
        )
        return self._parse_attribute_values_response(raw)

    def query_all(
        self,
        list_slug: str,
        *,
        filter: dict[str, Any] | None = None,
        sorts: list[Sort] | None = None,
        limit: int = 500,
    ) -> AsyncOffsetIterator[Entry]:
        """Auto-paginating version of query(). Returns an async iterator over all entries."""

        async def fetch_page(
            offset: int, page_limit: int
        ) -> ListResponse[Entry]:
            return await self.query(
                list_slug,
                filter=filter,
                sorts=sorts,
                limit=page_limit,
                offset=offset,
            )

        return AsyncOffsetIterator(fetch_page, limit=limit)
