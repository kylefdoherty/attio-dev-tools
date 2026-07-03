"""Base classes for queryable resources (Records and Entries).

Extracts the shared CRUD + pagination logic that Records and Entries have in
common.  Concrete subclasses supply:

- ``_collection_path(slug)`` -- e.g. ``/objects/{slug}/records``
- ``_item_path(slug, item_id)`` -- e.g. ``/objects/{slug}/records/{id}``
- ``_item_model`` -- the Pydantic model type (``Record`` or ``Entry``)
- ``_values_key`` -- ``"values"`` for Records, ``"entry_values"`` for Entries

The public API of RecordsResource / EntriesResource remains unchanged -- they
each keep their own method signatures (with resource-specific parameter names)
and any resource-specific methods (e.g. ``global_search``, ``list_entries``).
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from attio._pagination import AsyncOffsetIterator, OffsetIterator
from attio.models._base import DataWrapper, ListResponse
from attio.models.common import AttributeValue
from attio.models.records import Sort
from attio.resources._base import AsyncResource, SyncResource

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Shared mixin -- body/param construction that is identical for both resources
# ---------------------------------------------------------------------------


class _QueryableMixin(Generic[T]):
    """Shared parameter/body construction logic for queryable resources.

    Generic over the item model type *T* (``Record`` or ``Entry``).
    """

    # Subclasses must set these:
    _values_key: str  # "values" | "entry_values"
    _item_model: type[T]  # type: ignore[misc]

    # -- URL helpers (overridden by subclasses) --------------------------------

    @staticmethod
    def _collection_path(slug: str) -> str:  # pragma: no cover
        raise NotImplementedError

    @staticmethod
    def _item_path(slug: str, item_id: str) -> str:  # pragma: no cover
        raise NotImplementedError

    # -- Body / param builders -------------------------------------------------

    def _build_values_body(self, values: dict[str, Any]) -> dict[str, Any]:
        """Wrap values in ``{"data": {<values_key>: values}}``."""
        return {"data": {self._values_key: values}}

    @staticmethod
    def _build_query_body(
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        if filter is not None and filter_view_id is not None:
            raise ValueError(
                "filter and filter_view_id are mutually exclusive; provide only one"
            )
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

    # -- Response parsers ------------------------------------------------------

    def _parse_list_response(self, raw: dict[str, Any]) -> ListResponse[T]:
        return ListResponse[self._item_model].model_validate(raw)  # type: ignore[name-defined]

    def _parse_single_response(self, raw: dict[str, Any]) -> T:
        wrapper = DataWrapper[self._item_model].model_validate(raw)  # type: ignore[name-defined]
        return wrapper.data

    @staticmethod
    def _parse_attribute_values_response(
        raw: dict[str, Any],
    ) -> ListResponse[AttributeValue]:
        return ListResponse[AttributeValue].model_validate(raw)


# ---------------------------------------------------------------------------
# Sync queryable base
# ---------------------------------------------------------------------------


class SyncQueryableResource(SyncResource, _QueryableMixin[T]):
    """Synchronous base for queryable resources (Records / Entries).

    Provides the common CRUD + pagination implementations.  Subclasses add
    resource-specific methods (create, upsert, etc.) and may re-expose base
    methods with resource-specific parameter names via thin overrides.
    """

    def _list(
        self,
        slug: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[T]:
        # Attio API does not support GET for listing records/entries;
        # delegate to POST /query with just limit/offset params.
        return self._query(slug, limit=limit, offset=offset)

    def _query(
        self,
        slug: str,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[T]:
        body = self._build_query_body(
            filter=filter,
            filter_view_id=filter_view_id,
            sorts=sorts,
            limit=limit,
            offset=offset,
        )
        raw = self._http.request(
            "POST", f"{self._collection_path(slug)}/query", json=body
        )
        return self._parse_list_response(raw)

    def _get(self, slug: str, item_id: str) -> T:
        raw = self._http.request("GET", self._item_path(slug, item_id))
        return self._parse_single_response(raw)

    def _update(self, slug: str, item_id: str, values: dict[str, Any]) -> T:
        body = self._build_values_body(values)
        raw = self._http.request(
            "PUT", self._item_path(slug, item_id), json=body
        )
        return self._parse_single_response(raw)

    def _append(self, slug: str, item_id: str, values: dict[str, Any]) -> T:
        body = self._build_values_body(values)
        raw = self._http.request(
            "PATCH", self._item_path(slug, item_id), json=body
        )
        return self._parse_single_response(raw)

    def _delete(self, slug: str, item_id: str) -> None:
        self._http.request("DELETE", self._item_path(slug, item_id))

    def _get_attribute_values(
        self,
        slug: str,
        item_id: str,
        attribute: str,
        *,
        show_historic: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[AttributeValue]:
        params = self._build_attribute_values_params(
            show_historic=show_historic, limit=limit, offset=offset
        )
        raw = self._http.request(
            "GET",
            f"{self._item_path(slug, item_id)}/attributes/{attribute}/values",
            params=params,
        )
        return self._parse_attribute_values_response(raw)

    def _query_all(
        self,
        slug: str,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int = 500,
    ) -> OffsetIterator[T]:
        def fetch_page(offset: int, page_limit: int) -> ListResponse[T]:
            return self._query(
                slug,
                filter=filter,
                filter_view_id=filter_view_id,
                sorts=sorts,
                limit=page_limit,
                offset=offset,
            )

        return OffsetIterator(fetch_page, limit=limit)


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncQueryableResource(AsyncResource, _QueryableMixin[T]):
    """Asynchronous base for queryable resources (Records / Entries).

    Provides the common CRUD + pagination implementations.  Subclasses add
    resource-specific methods (create, upsert, etc.) and may re-expose base
    methods with resource-specific parameter names via thin overrides.
    """

    async def _list(
        self,
        slug: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[T]:
        # Attio API does not support GET for listing records/entries;
        # delegate to POST /query with just limit/offset params.
        return await self._query(slug, limit=limit, offset=offset)

    async def _query(
        self,
        slug: str,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[T]:
        body = self._build_query_body(
            filter=filter,
            filter_view_id=filter_view_id,
            sorts=sorts,
            limit=limit,
            offset=offset,
        )
        raw = await self._http.request(
            "POST", f"{self._collection_path(slug)}/query", json=body
        )
        return self._parse_list_response(raw)

    async def _get(self, slug: str, item_id: str) -> T:
        raw = await self._http.request("GET", self._item_path(slug, item_id))
        return self._parse_single_response(raw)

    async def _update(self, slug: str, item_id: str, values: dict[str, Any]) -> T:
        body = self._build_values_body(values)
        raw = await self._http.request(
            "PUT", self._item_path(slug, item_id), json=body
        )
        return self._parse_single_response(raw)

    async def _append(self, slug: str, item_id: str, values: dict[str, Any]) -> T:
        body = self._build_values_body(values)
        raw = await self._http.request(
            "PATCH", self._item_path(slug, item_id), json=body
        )
        return self._parse_single_response(raw)

    async def _delete(self, slug: str, item_id: str) -> None:
        await self._http.request("DELETE", self._item_path(slug, item_id))

    async def _get_attribute_values(
        self,
        slug: str,
        item_id: str,
        attribute: str,
        *,
        show_historic: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[AttributeValue]:
        params = self._build_attribute_values_params(
            show_historic=show_historic, limit=limit, offset=offset
        )
        raw = await self._http.request(
            "GET",
            f"{self._item_path(slug, item_id)}/attributes/{attribute}/values",
            params=params,
        )
        return self._parse_attribute_values_response(raw)

    def _query_all(
        self,
        slug: str,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int = 500,
    ) -> AsyncOffsetIterator[T]:
        async def fetch_page(offset: int, page_limit: int) -> ListResponse[T]:
            return await self._query(
                slug,
                filter=filter,
                filter_view_id=filter_view_id,
                sorts=sorts,
                limit=page_limit,
                offset=offset,
            )

        return AsyncOffsetIterator(fetch_page, limit=limit)
