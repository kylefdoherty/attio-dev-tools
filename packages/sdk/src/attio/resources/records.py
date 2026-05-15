"""Records resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio._pagination import AsyncOffsetIterator, OffsetIterator
from attio.models._base import DataWrapper, ListResponse
from attio.models.common import AttributeValue
from attio.models.records import GlobalSearchResult, Record, RecordEntry, Sort
from attio.resources._base import AsyncResource, SyncResource


class _RecordsMixin:
    """Shared parameter/body construction logic for the Records resource."""

    @staticmethod
    def _build_values_body(values: dict[str, Any]) -> dict[str, Any]:
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
    def _build_search_body(
        *,
        query: str,
        objects: list[str],
        limit: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"query": query, "objects": objects}
        if limit is not None:
            body["limit"] = limit
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
    def _parse_list_response(raw: dict[str, Any]) -> ListResponse[Record]:
        return ListResponse[Record].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> Record:
        wrapper = DataWrapper[Record].model_validate(raw)
        return wrapper.data

    @staticmethod
    def _parse_attribute_values_response(
        raw: dict[str, Any],
    ) -> ListResponse[AttributeValue]:
        return ListResponse[AttributeValue].model_validate(raw)

    @staticmethod
    def _parse_entries_response(raw: dict[str, Any]) -> ListResponse[RecordEntry]:
        return ListResponse[RecordEntry].model_validate(raw)

    @staticmethod
    def _parse_search_response(
        raw: dict[str, Any],
    ) -> ListResponse[GlobalSearchResult]:
        return ListResponse[GlobalSearchResult].model_validate(raw)


class RecordsResource(SyncResource, _RecordsMixin):
    """Synchronous Records resource."""

    def list(
        self,
        object: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Record]:
        """List records for an object."""
        params = self._build_list_params(limit=limit, offset=offset)
        raw = self._http.request("GET", f"/objects/{object}/records", params=params)
        return self._parse_list_response(raw)

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
        body = self._build_query_body(
            filter=filter,
            filter_view_id=filter_view_id,
            sorts=sorts,
            limit=limit,
            offset=offset,
        )
        raw = self._http.request(
            "POST", f"/objects/{object}/records/query", json=body
        )
        return self._parse_list_response(raw)

    def get(self, object: str, record_id: str) -> Record:
        """Get a single record by ID."""
        raw = self._http.request(
            "GET", f"/objects/{object}/records/{record_id}"
        )
        return self._parse_single_response(raw)

    def create(self, object: str, *, values: dict[str, Any]) -> Record:
        """Create a new record."""
        body = self._build_values_body(values)
        raw = self._http.request("POST", f"/objects/{object}/records", json=body)
        return self._parse_single_response(raw)

    def update(
        self, object: str, record_id: str, *, values: dict[str, Any]
    ) -> Record:
        """Update a record (overwrites multiselect values)."""
        body = self._build_values_body(values)
        raw = self._http.request(
            "PUT", f"/objects/{object}/records/{record_id}", json=body
        )
        return self._parse_single_response(raw)

    def append(
        self, object: str, record_id: str, *, values: dict[str, Any]
    ) -> Record:
        """Update a record (appends to multiselect values)."""
        body = self._build_values_body(values)
        raw = self._http.request(
            "PATCH", f"/objects/{object}/records/{record_id}", json=body
        )
        return self._parse_single_response(raw)

    def delete(self, object: str, record_id: str) -> None:
        """Delete a record."""
        self._http.request(
            "DELETE", f"/objects/{object}/records/{record_id}"
        )

    def upsert(
        self,
        object: str,
        *,
        matching_attribute: str,
        values: dict[str, Any],
    ) -> Record:
        """Upsert a record by matching attribute (create or update)."""
        body = self._build_upsert_body(matching_attribute, values)
        raw = self._http.request("PUT", f"/objects/{object}/records", json=body)
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
        params = self._build_attribute_values_params(
            show_historic=show_historic, limit=limit, offset=offset
        )
        raw = self._http.request(
            "GET",
            f"/objects/{object}/records/{record_id}/attributes/{attribute}/values",
            params=params,
        )
        return self._parse_attribute_values_response(raw)

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
        limit: int | None = None,
    ) -> ListResponse[GlobalSearchResult]:
        """Search across all object records globally."""
        body = self._build_search_body(query=query, objects=objects, limit=limit)
        raw = self._http.request("POST", "/objects/records/search", json=body)
        return self._parse_search_response(raw)

    def query_all(
        self,
        object: str,
        *,
        filter: dict[str, Any] | None = None,
        sorts: list[Sort] | None = None,
        limit: int = 500,
    ) -> OffsetIterator[Record]:
        """Auto-paginating version of query(). Returns an iterator over all records."""

        def fetch_page(offset: int, page_limit: int) -> ListResponse[Record]:
            return self.query(
                object,
                filter=filter,
                sorts=sorts,
                limit=page_limit,
                offset=offset,
            )

        return OffsetIterator(fetch_page, limit=limit)


class AsyncRecordsResource(AsyncResource, _RecordsMixin):
    """Asynchronous Records resource."""

    async def list(
        self,
        object: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Record]:
        """List records for an object."""
        params = self._build_list_params(limit=limit, offset=offset)
        raw = await self._http.request(
            "GET", f"/objects/{object}/records", params=params
        )
        return self._parse_list_response(raw)

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
        body = self._build_query_body(
            filter=filter,
            filter_view_id=filter_view_id,
            sorts=sorts,
            limit=limit,
            offset=offset,
        )
        raw = await self._http.request(
            "POST", f"/objects/{object}/records/query", json=body
        )
        return self._parse_list_response(raw)

    async def get(self, object: str, record_id: str) -> Record:
        """Get a single record by ID."""
        raw = await self._http.request(
            "GET", f"/objects/{object}/records/{record_id}"
        )
        return self._parse_single_response(raw)

    async def create(self, object: str, *, values: dict[str, Any]) -> Record:
        """Create a new record."""
        body = self._build_values_body(values)
        raw = await self._http.request(
            "POST", f"/objects/{object}/records", json=body
        )
        return self._parse_single_response(raw)

    async def update(
        self, object: str, record_id: str, *, values: dict[str, Any]
    ) -> Record:
        """Update a record (overwrites multiselect values)."""
        body = self._build_values_body(values)
        raw = await self._http.request(
            "PUT", f"/objects/{object}/records/{record_id}", json=body
        )
        return self._parse_single_response(raw)

    async def append(
        self, object: str, record_id: str, *, values: dict[str, Any]
    ) -> Record:
        """Update a record (appends to multiselect values)."""
        body = self._build_values_body(values)
        raw = await self._http.request(
            "PATCH", f"/objects/{object}/records/{record_id}", json=body
        )
        return self._parse_single_response(raw)

    async def delete(self, object: str, record_id: str) -> None:
        """Delete a record."""
        await self._http.request(
            "DELETE", f"/objects/{object}/records/{record_id}"
        )

    async def upsert(
        self,
        object: str,
        *,
        matching_attribute: str,
        values: dict[str, Any],
    ) -> Record:
        """Upsert a record by matching attribute (create or update)."""
        body = self._build_upsert_body(matching_attribute, values)
        raw = await self._http.request(
            "PUT", f"/objects/{object}/records", json=body
        )
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
        params = self._build_attribute_values_params(
            show_historic=show_historic, limit=limit, offset=offset
        )
        raw = await self._http.request(
            "GET",
            f"/objects/{object}/records/{record_id}/attributes/{attribute}/values",
            params=params,
        )
        return self._parse_attribute_values_response(raw)

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
        limit: int | None = None,
    ) -> ListResponse[GlobalSearchResult]:
        """Search across all object records globally."""
        body = self._build_search_body(query=query, objects=objects, limit=limit)
        raw = await self._http.request(
            "POST", "/objects/records/search", json=body
        )
        return self._parse_search_response(raw)

    def query_all(
        self,
        object: str,
        *,
        filter: dict[str, Any] | None = None,
        sorts: list[Sort] | None = None,
        limit: int = 500,
    ) -> AsyncOffsetIterator[Record]:
        """Auto-paginating version of query(). Returns an async iterator over all records."""

        async def fetch_page(
            offset: int, page_limit: int
        ) -> ListResponse[Record]:
            return await self.query(
                object,
                filter=filter,
                sorts=sorts,
                limit=page_limit,
                offset=offset,
            )

        return AsyncOffsetIterator(fetch_page, limit=limit)
