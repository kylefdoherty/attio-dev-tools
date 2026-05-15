"""Base classes for standard object convenience wrappers.

These delegate all operations to the underlying RecordsResource/AsyncRecordsResource,
pre-filling the object slug so callers don't have to specify it on every call.
"""

from __future__ import annotations

from typing import Any

from attio._pagination import AsyncOffsetIterator, OffsetIterator
from attio.models._base import ListResponse
from attio.models.common import AttributeValue
from attio.models.records import Record, RecordEntry, Sort
from attio.resources.records import AsyncRecordsResource, RecordsResource


class StandardObjectResource:
    """Base for standard object convenience wrappers (sync).

    Subclasses set ``_object_slug`` and inherit every Records method with
    the slug pre-filled.
    """

    _object_slug: str

    def __init__(self, records: RecordsResource) -> None:
        self._records = records

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Record]:
        """List records for this object."""
        return self._records.list(self._object_slug, limit=limit, offset=offset)

    def query(
        self,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Record]:
        """Query records with filters and sorting."""
        return self._records.query(
            self._object_slug,
            filter=filter,
            filter_view_id=filter_view_id,
            sorts=sorts,
            limit=limit,
            offset=offset,
        )

    def get(self, record_id: str) -> Record:
        """Get a single record by ID."""
        return self._records.get(self._object_slug, record_id)

    def create(self, *, values: dict[str, Any]) -> Record:
        """Create a new record."""
        return self._records.create(self._object_slug, values=values)

    def update(self, record_id: str, *, values: dict[str, Any]) -> Record:
        """Update a record (overwrites multiselect values)."""
        return self._records.update(self._object_slug, record_id, values=values)

    def append(self, record_id: str, *, values: dict[str, Any]) -> Record:
        """Update a record (appends to multiselect values)."""
        return self._records.append(self._object_slug, record_id, values=values)

    def delete(self, record_id: str) -> None:
        """Delete a record."""
        return self._records.delete(self._object_slug, record_id)

    def upsert(
        self,
        *,
        matching_attribute: str,
        values: dict[str, Any],
    ) -> Record:
        """Upsert a record by matching attribute (create or update)."""
        return self._records.upsert(
            self._object_slug,
            matching_attribute=matching_attribute,
            values=values,
        )

    def get_attribute_values(
        self,
        record_id: str,
        attribute: str,
        *,
        show_historic: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[AttributeValue]:
        """Get attribute values for a specific record and attribute."""
        return self._records.get_attribute_values(
            self._object_slug,
            record_id,
            attribute,
            show_historic=show_historic,
            limit=limit,
            offset=offset,
        )

    def list_entries(
        self,
        record_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[RecordEntry]:
        """List entries for a record (across all lists)."""
        return self._records.list_entries(
            self._object_slug, record_id, limit=limit, offset=offset
        )

    def query_all(
        self,
        *,
        filter: dict[str, Any] | None = None,
        sorts: list[Sort] | None = None,
        limit: int = 500,
    ) -> OffsetIterator[Record]:
        """Auto-paginating version of query(). Returns an iterator over all records."""
        return self._records.query_all(
            self._object_slug, filter=filter, sorts=sorts, limit=limit
        )


class AsyncStandardObjectResource:
    """Base for standard object convenience wrappers (async).

    Subclasses set ``_object_slug`` and inherit every Records method with
    the slug pre-filled.
    """

    _object_slug: str

    def __init__(self, records: AsyncRecordsResource) -> None:
        self._records = records

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Record]:
        """List records for this object."""
        return await self._records.list(self._object_slug, limit=limit, offset=offset)

    async def query(
        self,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Record]:
        """Query records with filters and sorting."""
        return await self._records.query(
            self._object_slug,
            filter=filter,
            filter_view_id=filter_view_id,
            sorts=sorts,
            limit=limit,
            offset=offset,
        )

    async def get(self, record_id: str) -> Record:
        """Get a single record by ID."""
        return await self._records.get(self._object_slug, record_id)

    async def create(self, *, values: dict[str, Any]) -> Record:
        """Create a new record."""
        return await self._records.create(self._object_slug, values=values)

    async def update(self, record_id: str, *, values: dict[str, Any]) -> Record:
        """Update a record (overwrites multiselect values)."""
        return await self._records.update(
            self._object_slug, record_id, values=values
        )

    async def append(self, record_id: str, *, values: dict[str, Any]) -> Record:
        """Update a record (appends to multiselect values)."""
        return await self._records.append(
            self._object_slug, record_id, values=values
        )

    async def delete(self, record_id: str) -> None:
        """Delete a record."""
        await self._records.delete(self._object_slug, record_id)

    async def upsert(
        self,
        *,
        matching_attribute: str,
        values: dict[str, Any],
    ) -> Record:
        """Upsert a record by matching attribute (create or update)."""
        return await self._records.upsert(
            self._object_slug,
            matching_attribute=matching_attribute,
            values=values,
        )

    async def get_attribute_values(
        self,
        record_id: str,
        attribute: str,
        *,
        show_historic: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[AttributeValue]:
        """Get attribute values for a specific record and attribute."""
        return await self._records.get_attribute_values(
            self._object_slug,
            record_id,
            attribute,
            show_historic=show_historic,
            limit=limit,
            offset=offset,
        )

    async def list_entries(
        self,
        record_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[RecordEntry]:
        """List entries for a record (across all lists)."""
        return await self._records.list_entries(
            self._object_slug, record_id, limit=limit, offset=offset
        )

    def query_all(
        self,
        *,
        filter: dict[str, Any] | None = None,
        sorts: list[Sort] | None = None,
        limit: int = 500,
    ) -> AsyncOffsetIterator[Record]:
        """Auto-paginating version of query(). Returns an async iterator over all records."""
        return self._records.query_all(
            self._object_slug, filter=filter, sorts=sorts, limit=limit
        )
