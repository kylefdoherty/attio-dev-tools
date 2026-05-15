"""Lists resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio.models._base import DataWrapper, ListResponse
from attio.models.lists import AttioList
from attio.resources._base import AsyncResource, SyncResource


class _ListsMixin:
    """Shared parameter/body construction logic for the Lists resource."""

    @staticmethod
    def _build_create_body(
        *,
        name: str,
        api_slug: str,
        parent_object: str,
        workspace_access: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": name,
            "api_slug": api_slug,
            "parent_object": parent_object,
        }
        if workspace_access is not None:
            data["workspace_access"] = workspace_access
        return {"data": data}

    @staticmethod
    def _build_update_body(
        *,
        name: str | None = None,
        api_slug: str | None = None,
        workspace_access: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if api_slug is not None:
            data["api_slug"] = api_slug
        if workspace_access is not None:
            data["workspace_access"] = workspace_access
        return {"data": data}

    @staticmethod
    def _parse_list_response(raw: dict[str, Any]) -> ListResponse[AttioList]:
        return ListResponse[AttioList].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> AttioList:
        wrapper = DataWrapper[AttioList].model_validate(raw)
        return wrapper.data


class ListsResource(SyncResource, _ListsMixin):
    """Synchronous Lists resource."""

    def list(self) -> ListResponse[AttioList]:
        """List all lists in the workspace."""
        raw = self._http.request("GET", "/lists")
        return self._parse_list_response(raw)

    def get(self, list_slug: str) -> AttioList:
        """Get a single list by slug or ID."""
        raw = self._http.request("GET", f"/lists/{list_slug}")
        return self._parse_single_response(raw)

    def create(
        self,
        *,
        name: str,
        api_slug: str,
        parent_object: str,
        workspace_access: str | None = None,
    ) -> AttioList:
        """Create a new list."""
        body = self._build_create_body(
            name=name,
            api_slug=api_slug,
            parent_object=parent_object,
            workspace_access=workspace_access,
        )
        raw = self._http.request("POST", "/lists", json=body)
        return self._parse_single_response(raw)

    def update(
        self,
        list_slug: str,
        *,
        name: str | None = None,
        api_slug: str | None = None,
        workspace_access: str | None = None,
    ) -> AttioList:
        """Update an existing list."""
        body = self._build_update_body(
            name=name,
            api_slug=api_slug,
            workspace_access=workspace_access,
        )
        raw = self._http.request("PATCH", f"/lists/{list_slug}", json=body)
        return self._parse_single_response(raw)


class AsyncListsResource(AsyncResource, _ListsMixin):
    """Asynchronous Lists resource."""

    async def list(self) -> ListResponse[AttioList]:
        """List all lists in the workspace."""
        raw = await self._http.request("GET", "/lists")
        return self._parse_list_response(raw)

    async def get(self, list_slug: str) -> AttioList:
        """Get a single list by slug or ID."""
        raw = await self._http.request("GET", f"/lists/{list_slug}")
        return self._parse_single_response(raw)

    async def create(
        self,
        *,
        name: str,
        api_slug: str,
        parent_object: str,
        workspace_access: str | None = None,
    ) -> AttioList:
        """Create a new list."""
        body = self._build_create_body(
            name=name,
            api_slug=api_slug,
            parent_object=parent_object,
            workspace_access=workspace_access,
        )
        raw = await self._http.request("POST", "/lists", json=body)
        return self._parse_single_response(raw)

    async def update(
        self,
        list_slug: str,
        *,
        name: str | None = None,
        api_slug: str | None = None,
        workspace_access: str | None = None,
    ) -> AttioList:
        """Update an existing list."""
        body = self._build_update_body(
            name=name,
            api_slug=api_slug,
            workspace_access=workspace_access,
        )
        raw = await self._http.request("PATCH", f"/lists/{list_slug}", json=body)
        return self._parse_single_response(raw)
