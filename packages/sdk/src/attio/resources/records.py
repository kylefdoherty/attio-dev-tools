"""Records resource implementation (sync and async).

Thin adapters over ``SyncQueryableResource`` / ``AsyncQueryableResource`` that
supply the Records-specific URL scheme, model type, and values key, plus the
methods unique to Records (``list_entries``, ``global_search``).
"""

from __future__ import annotations

from typing import Any

from attio._pagination import AsyncOffsetIterator, OffsetIterator
from attio.models._base import ListResponse
from attio.models.common import AttributeValue
from attio.models.records import GlobalSearchResult, Record, RecordEntry, Sort
from attio.resources._queryable import (
    AsyncQueryableResource,
    SyncQueryableResource,
    _QueryableMixin,
)


# ---------------------------------------------------------------------------
# Mixin kept for backward-compatibility of tests that import _RecordsMixin
# ---------------------------------------------------------------------------


class _RecordsMixin(_QueryableMixin[Record]):
    """Records-specific parameter/body construction logic."""

    _values_key = "values"
    _item_model = Record

    @staticmethod
    def _collection_path(slug: str) -> str:
        return f"/objects/{slug}/records"

    @staticmethod
    def _item_path(slug: str, item_id: str) -> str:
        return f"/objects/{slug}/records/{item_id}"

    # -- Records-only body builders -------------------------------------------

    @staticmethod
    def _build_values_body(values: dict[str, Any]) -> dict[str, Any]:  # type: ignore[override]
        """Wrap values in ``{"data": {"values": ...}}``."""
        return {"data": {"values": values}}

    @staticmethod
    def _build_upsert_body(
        matching_attribute: str,
        values: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "data": {
                "matching_attribute": matching_attribute,
                "values": values,
            }
        }

    @staticmethod
    def _build_search_body(
        *,
        query: str,
        objects: list[str],
        request_as: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "query": query,
            "objects": objects,
            # request_as is required by the API; default to workspace-wide results.
            "request_as": request_as if request_as is not None else {"type": "workspace"},
        }
        if limit is not None:
            body["limit"] = limit
        return body

    # -- Records-only response parsers ----------------------------------------

    @staticmethod
    def _parse_entries_response(raw: dict[str, Any]) -> ListResponse[RecordEntry]:
        return ListResponse[RecordEntry].model_validate(raw)

    @staticmethod
    def _parse_search_response(
        raw: dict[str, Any],
    ) -> ListResponse[GlobalSearchResult]:
        return ListResponse[GlobalSearchResult].model_validate(raw)


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------


class RecordsResource(SyncQueryableResource[Record], _RecordsMixin):
    """Synchronous Records resource."""

    def list(
        self,
        object: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Record]:
        """List records for an object."""
        return self._list(object, limit=limit, offset=offset)

    def query(
        self,
        object: str,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Record]:
        """Query records with filters and sorting."""
        return self._query(
            object,
            filter=filter,
            filter_view_id=filter_view_id,
            sorts=sorts,
            limit=limit,
            offset=offset,
        )

    def get(self, object: str, record_id: str) -> Record:
        """Get a single record by ID."""
        return self._get(object, record_id)

    def create(self, object: str, *, values: dict[str, Any]) -> Record:
        """Create a new record."""
        body = self._build_values_body(values)
        raw = self._http.request("POST", self._collection_path(object), json=body)
        return self._parse_single_response(raw)

    def update(
        self, object: str, record_id: str, *, values: dict[str, Any]
    ) -> Record:
        """Update a record (overwrites multiselect values)."""
        return self._update(object, record_id, values)

    def append(
        self, object: str, record_id: str, *, values: dict[str, Any]
    ) -> Record:
        """Update a record (appends to multiselect values)."""
        return self._append(object, record_id, values)

    def delete(self, object: str, record_id: str) -> None:
        """Delete a record."""
        self._delete(object, record_id)

    def upsert(
        self,
        object: str,
        *,
        matching_attribute: str,
        values: dict[str, Any],
    ) -> Record:
        """Upsert a record by matching attribute (create or update)."""
        body = self._build_upsert_body(matching_attribute, values)
        raw = self._http.request("PUT", self._collection_path(object), json=body)
        return self._parse_single_response(raw)

    def get_attribute_values(
        self,
        object: str,
        record_id: str,
        attribute: str,
        *,
        show_historic: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[AttributeValue]:
        """Get attribute values for a specific record and attribute."""
        return self._get_attribute_values(
            object, record_id, attribute,
            show_historic=show_historic, limit=limit, offset=offset,
        )

    def list_entries(
        self,
        object: str,
        record_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[RecordEntry]:
        """List entries for a record (across all lists)."""
        params = self._build_list_params(limit=limit, offset=offset)
        raw = self._http.request(
            "GET",
            f"/objects/{object}/records/{record_id}/entries",
            params=params,
        )
        return self._parse_entries_response(raw)

    def global_search(
        self,
        *,
        query: str,
        objects: list[str],
        request_as: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> ListResponse[GlobalSearchResult]:
        """Fuzzy-search records across one or more objects. (beta)

        BETA: results are eventually consistent; recently written records may
        not appear immediately. At least one object slug/ID is required and
        ``limit`` is capped at 25 (default 25). ``request_as`` scopes results
        to what a workspace member can see (e.g. ``{"type":
        "workspace-member", "email_address": ...}``); defaults to
        ``{"type": "workspace"}`` (all results).
        """
        body = self._build_search_body(
            query=query, objects=objects, request_as=request_as, limit=limit
        )
        raw = self._http.request("POST", "/objects/records/search", json=body)
        return self._parse_search_response(raw)

    def query_all(
        self,
        object: str,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int = 500,
    ) -> OffsetIterator[Record]:
        """Auto-paginating version of query(). Returns an iterator over all records."""
        return self._query_all(
            object, filter=filter, filter_view_id=filter_view_id, sorts=sorts, limit=limit
        )


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncRecordsResource(AsyncQueryableResource[Record], _RecordsMixin):
    """Asynchronous Records resource."""

    async def list(
        self,
        object: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Record]:
        """List records for an object."""
        return await self._list(object, limit=limit, offset=offset)

    async def query(
        self,
        object: str,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Record]:
        """Query records with filters and sorting."""
        return await self._query(
            object,
            filter=filter,
            filter_view_id=filter_view_id,
            sorts=sorts,
            limit=limit,
            offset=offset,
        )

    async def get(self, object: str, record_id: str) -> Record:
        """Get a single record by ID."""
        return await self._get(object, record_id)

    async def create(self, object: str, *, values: dict[str, Any]) -> Record:
        """Create a new record."""
        body = self._build_values_body(values)
        raw = await self._http.request("POST", self._collection_path(object), json=body)
        return self._parse_single_response(raw)

    async def update(
        self, object: str, record_id: str, *, values: dict[str, Any]
    ) -> Record:
        """Update a record (overwrites multiselect values)."""
        return await self._update(object, record_id, values)

    async def append(
        self, object: str, record_id: str, *, values: dict[str, Any]
    ) -> Record:
        """Update a record (appends to multiselect values)."""
        return await self._append(object, record_id, values)

    async def delete(self, object: str, record_id: str) -> None:
        """Delete a record."""
        await self._delete(object, record_id)

    async def upsert(
        self,
        object: str,
        *,
        matching_attribute: str,
        values: dict[str, Any],
    ) -> Record:
        """Upsert a record by matching attribute (create or update)."""
        body = self._build_upsert_body(matching_attribute, values)
        raw = await self._http.request("PUT", self._collection_path(object), json=body)
        return self._parse_single_response(raw)

    async def get_attribute_values(
        self,
        object: str,
        record_id: str,
        attribute: str,
        *,
        show_historic: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[AttributeValue]:
        """Get attribute values for a specific record and attribute."""
        return await self._get_attribute_values(
            object, record_id, attribute,
            show_historic=show_historic, limit=limit, offset=offset,
        )

    async def list_entries(
        self,
        object: str,
        record_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[RecordEntry]:
        """List entries for a record (across all lists)."""
        params = self._build_list_params(limit=limit, offset=offset)
        raw = await self._http.request(
            "GET",
            f"/objects/{object}/records/{record_id}/entries",
            params=params,
        )
        return self._parse_entries_response(raw)

    async def global_search(
        self,
        *,
        query: str,
        objects: list[str],
        request_as: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> ListResponse[GlobalSearchResult]:
        """Fuzzy-search records across one or more objects. (beta)

        BETA: results are eventually consistent; recently written records may
        not appear immediately. At least one object slug/ID is required and
        ``limit`` is capped at 25 (default 25). ``request_as`` scopes results
        to what a workspace member can see (e.g. ``{"type":
        "workspace-member", "email_address": ...}``); defaults to
        ``{"type": "workspace"}`` (all results).
        """
        body = self._build_search_body(
            query=query, objects=objects, request_as=request_as, limit=limit
        )
        raw = await self._http.request("POST", "/objects/records/search", json=body)
        return self._parse_search_response(raw)

    def query_all(
        self,
        object: str,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int = 500,
    ) -> AsyncOffsetIterator[Record]:
        """Auto-paginating version of query(). Returns an async iterator over all records."""
        return self._query_all(
            object, filter=filter, filter_view_id=filter_view_id, sorts=sorts, limit=limit
        )
