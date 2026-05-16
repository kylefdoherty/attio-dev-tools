"""Entries resource implementation (sync and async).

Thin adapters over ``SyncQueryableResource`` / ``AsyncQueryableResource`` that
supply the Entries-specific URL scheme, model type, and values key, plus the
methods unique to Entries (``create`` and ``upsert`` with parent context).
"""

from __future__ import annotations

from typing import Any

from attio._pagination import AsyncOffsetIterator, OffsetIterator
from attio.models._base import ListResponse
from attio.models.common import AttributeValue
from attio.models.entries import Entry
from attio.models.records import Sort
from attio.resources._queryable import (
    AsyncQueryableResource,
    SyncQueryableResource,
    _QueryableMixin,
)


# ---------------------------------------------------------------------------
# Mixin kept for backward-compatibility of tests that import _EntriesMixin
# ---------------------------------------------------------------------------


class _EntriesMixin(_QueryableMixin[Entry]):
    """Entries-specific parameter/body construction logic."""

    _values_key = "entry_values"
    _item_model = Entry

    @staticmethod
    def _collection_path(slug: str) -> str:
        return f"/lists/{slug}/entries"

    @staticmethod
    def _item_path(slug: str, item_id: str) -> str:
        return f"/lists/{slug}/entries/{item_id}"

    # -- Entries-only body builders -------------------------------------------

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

    # Keep the original name for backward-compatibility of mixin tests.
    @staticmethod
    def _build_entry_values_body(entry_values: dict[str, Any]) -> dict[str, Any]:
        return {"data": {"entry_values": entry_values}}


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------


class EntriesResource(SyncQueryableResource[Entry], _EntriesMixin):
    """Synchronous Entries resource."""

    def list(
        self,
        list_slug: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Entry]:
        """List entries for a list."""
        return self._list(list_slug, limit=limit, offset=offset)

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
        return self._query(
            list_slug,
            filter=filter,
            filter_view_id=filter_view_id,
            sorts=sorts,
            limit=limit,
            offset=offset,
        )

    def get(self, list_slug: str, entry_id: str) -> Entry:
        """Get a single entry by ID."""
        return self._get(list_slug, entry_id)

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
        raw = self._http.request("POST", self._collection_path(list_slug), json=body)
        return self._parse_single_response(raw)

    def update(
        self, list_slug: str, entry_id: str, *, entry_values: dict[str, Any]
    ) -> Entry:
        """Update an entry (overwrites multiselect values)."""
        return self._update(list_slug, entry_id, entry_values)

    def append(
        self, list_slug: str, entry_id: str, *, entry_values: dict[str, Any]
    ) -> Entry:
        """Update an entry (appends to multiselect values)."""
        return self._append(list_slug, entry_id, entry_values)

    def delete(self, list_slug: str, entry_id: str) -> None:
        """Delete an entry."""
        self._delete(list_slug, entry_id)

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
        raw = self._http.request("PUT", self._collection_path(list_slug), json=body)
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
        return self._get_attribute_values(
            list_slug, entry_id, attribute,
            show_historic=show_historic, limit=limit, offset=offset,
        )

    def query_all(
        self,
        list_slug: str,
        *,
        filter: dict[str, Any] | None = None,
        sorts: list[Sort] | None = None,
        limit: int = 500,
    ) -> OffsetIterator[Entry]:
        """Auto-paginating version of query(). Returns an iterator over all entries."""
        return self._query_all(list_slug, filter=filter, sorts=sorts, limit=limit)


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncEntriesResource(AsyncQueryableResource[Entry], _EntriesMixin):
    """Asynchronous Entries resource."""

    async def list(
        self,
        list_slug: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Entry]:
        """List entries for a list."""
        return await self._list(list_slug, limit=limit, offset=offset)

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
        return await self._query(
            list_slug,
            filter=filter,
            filter_view_id=filter_view_id,
            sorts=sorts,
            limit=limit,
            offset=offset,
        )

    async def get(self, list_slug: str, entry_id: str) -> Entry:
        """Get a single entry by ID."""
        return await self._get(list_slug, entry_id)

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
        raw = await self._http.request("POST", self._collection_path(list_slug), json=body)
        return self._parse_single_response(raw)

    async def update(
        self, list_slug: str, entry_id: str, *, entry_values: dict[str, Any]
    ) -> Entry:
        """Update an entry (overwrites multiselect values)."""
        return await self._update(list_slug, entry_id, entry_values)

    async def append(
        self, list_slug: str, entry_id: str, *, entry_values: dict[str, Any]
    ) -> Entry:
        """Update an entry (appends to multiselect values)."""
        return await self._append(list_slug, entry_id, entry_values)

    async def delete(self, list_slug: str, entry_id: str) -> None:
        """Delete an entry."""
        await self._delete(list_slug, entry_id)

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
        raw = await self._http.request("PUT", self._collection_path(list_slug), json=body)
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
        return await self._get_attribute_values(
            list_slug, entry_id, attribute,
            show_historic=show_historic, limit=limit, offset=offset,
        )

    def query_all(
        self,
        list_slug: str,
        *,
        filter: dict[str, Any] | None = None,
        sorts: list[Sort] | None = None,
        limit: int = 500,
    ) -> AsyncOffsetIterator[Entry]:
        """Auto-paginating version of query(). Returns an async iterator over all entries."""
        return self._query_all(list_slug, filter=filter, sorts=sorts, limit=limit)
