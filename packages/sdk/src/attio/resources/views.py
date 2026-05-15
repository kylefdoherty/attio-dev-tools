"""Views resource implementation (sync and async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attio.models._base import PaginatedResponse
from attio.models.views import View
from attio.resources._base import AsyncResource, SyncResource

if TYPE_CHECKING:
    from attio._pagination import AsyncCursorIterator, CursorIterator


class _ViewsMixin:
    """Shared parameter/body construction logic for the Views resource."""

    @staticmethod
    def _build_query_params(
        *,
        show_archived: bool = False,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if show_archived:
            params["show_archived"] = True
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        return params

    @staticmethod
    def _parse_paginated_response(raw: dict[str, Any]) -> PaginatedResponse[View]:
        return PaginatedResponse[View].model_validate(raw)


class ViewsResource(SyncResource, _ViewsMixin):
    """Synchronous Views resource."""

    def list_for_object(
        self,
        object: str,
        *,
        show_archived: bool = False,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> PaginatedResponse[View]:
        """List views for an object."""
        params = self._build_query_params(
            show_archived=show_archived,
            limit=limit,
            cursor=cursor,
        )
        raw = self._http.request("GET", f"/objects/{object}/views", params=params)
        return self._parse_paginated_response(raw)

    def list_for_list(
        self,
        list: str,
        *,
        show_archived: bool = False,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> PaginatedResponse[View]:
        """List views for a list."""
        params = self._build_query_params(
            show_archived=show_archived,
            limit=limit,
            cursor=cursor,
        )
        raw = self._http.request("GET", f"/lists/{list}/views", params=params)
        return self._parse_paginated_response(raw)

    def list_all_for_object(
        self,
        object: str,
        *,
        show_archived: bool = False,
        limit: int | None = None,
    ) -> CursorIterator[View]:
        """Auto-paginate all views for an object."""
        from attio._pagination import CursorIterator

        def fetch_page(cursor: str | None) -> PaginatedResponse[View]:
            return self.list_for_object(
                object,
                show_archived=show_archived,
                limit=limit,
                cursor=cursor,
            )

        return CursorIterator(fetch_page=fetch_page)

    def list_all_for_list(
        self,
        list: str,
        *,
        show_archived: bool = False,
        limit: int | None = None,
    ) -> CursorIterator[View]:
        """Auto-paginate all views for a list."""
        from attio._pagination import CursorIterator

        def fetch_page(cursor: str | None) -> PaginatedResponse[View]:
            return self.list_for_list(
                list,
                show_archived=show_archived,
                limit=limit,
                cursor=cursor,
            )

        return CursorIterator(fetch_page=fetch_page)


class AsyncViewsResource(AsyncResource, _ViewsMixin):
    """Asynchronous Views resource."""

    async def list_for_object(
        self,
        object: str,
        *,
        show_archived: bool = False,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> PaginatedResponse[View]:
        """List views for an object."""
        params = self._build_query_params(
            show_archived=show_archived,
            limit=limit,
            cursor=cursor,
        )
        raw = await self._http.request("GET", f"/objects/{object}/views", params=params)
        return self._parse_paginated_response(raw)

    async def list_for_list(
        self,
        list: str,
        *,
        show_archived: bool = False,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> PaginatedResponse[View]:
        """List views for a list."""
        params = self._build_query_params(
            show_archived=show_archived,
            limit=limit,
            cursor=cursor,
        )
        raw = await self._http.request("GET", f"/lists/{list}/views", params=params)
        return self._parse_paginated_response(raw)

    def list_all_for_object(
        self,
        object: str,
        *,
        show_archived: bool = False,
        limit: int | None = None,
    ) -> AsyncCursorIterator[View]:
        """Auto-paginate all views for an object."""
        from attio._pagination import AsyncCursorIterator

        async def fetch_page(cursor: str | None) -> PaginatedResponse[View]:
            return await self.list_for_object(
                object,
                show_archived=show_archived,
                limit=limit,
                cursor=cursor,
            )

        return AsyncCursorIterator(fetch_page=fetch_page)

    def list_all_for_list(
        self,
        list: str,
        *,
        show_archived: bool = False,
        limit: int | None = None,
    ) -> AsyncCursorIterator[View]:
        """Auto-paginate all views for a list."""
        from attio._pagination import AsyncCursorIterator

        async def fetch_page(cursor: str | None) -> PaginatedResponse[View]:
            return await self.list_for_list(
                list,
                show_archived=show_archived,
                limit=limit,
                cursor=cursor,
            )

        return AsyncCursorIterator(fetch_page=fetch_page)
