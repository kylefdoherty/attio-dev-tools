"""Objects resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio.models._base import DataWrapper, ListResponse
from attio.models.objects import Object
from attio.resources._base import AsyncResource, SyncResource


class _ObjectsMixin:
    """Shared parameter/body construction logic for the Objects resource."""

    @staticmethod
    def _build_create_body(
        *,
        api_slug: str,
        singular_noun: str,
        plural_noun: str,
    ) -> dict[str, Any]:
        return {
            "data": {
                "api_slug": api_slug,
                "singular_noun": singular_noun,
                "plural_noun": plural_noun,
            }
        }

    @staticmethod
    def _build_update_body(
        *,
        singular_noun: str | None = None,
        plural_noun: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if singular_noun is not None:
            data["singular_noun"] = singular_noun
        if plural_noun is not None:
            data["plural_noun"] = plural_noun
        return {"data": data}

    @staticmethod
    def _parse_list_response(raw: dict[str, Any]) -> ListResponse[Object]:
        return ListResponse[Object].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> Object:
        wrapper = DataWrapper[Object].model_validate(raw)
        return wrapper.data


class ObjectsResource(SyncResource, _ObjectsMixin):
    """Synchronous Objects resource."""

    def list(self) -> ListResponse[Object]:
        """List all objects in the workspace."""
        raw = self._http.request("GET", "/objects")
        return self._parse_list_response(raw)

    def get(self, object: str) -> Object:
        """Get a single object by slug or ID."""
        raw = self._http.request("GET", f"/objects/{object}")
        return self._parse_single_response(raw)

    def create(
        self,
        *,
        api_slug: str,
        singular_noun: str,
        plural_noun: str,
    ) -> Object:
        """Create a new custom object."""
        body = self._build_create_body(
            api_slug=api_slug,
            singular_noun=singular_noun,
            plural_noun=plural_noun,
        )
        raw = self._http.request("POST", "/objects", json=body)
        return self._parse_single_response(raw)

    def update(
        self,
        object: str,
        *,
        singular_noun: str | None = None,
        plural_noun: str | None = None,
    ) -> Object:
        """Update an existing object."""
        body = self._build_update_body(
            singular_noun=singular_noun,
            plural_noun=plural_noun,
        )
        raw = self._http.request("PUT", f"/objects/{object}", json=body)
        return self._parse_single_response(raw)


class AsyncObjectsResource(AsyncResource, _ObjectsMixin):
    """Asynchronous Objects resource."""

    async def list(self) -> ListResponse[Object]:
        """List all objects in the workspace."""
        raw = await self._http.request("GET", "/objects")
        return self._parse_list_response(raw)

    async def get(self, object: str) -> Object:
        """Get a single object by slug or ID."""
        raw = await self._http.request("GET", f"/objects/{object}")
        return self._parse_single_response(raw)

    async def create(
        self,
        *,
        api_slug: str,
        singular_noun: str,
        plural_noun: str,
    ) -> Object:
        """Create a new custom object."""
        body = self._build_create_body(
            api_slug=api_slug,
            singular_noun=singular_noun,
            plural_noun=plural_noun,
        )
        raw = await self._http.request("POST", "/objects", json=body)
        return self._parse_single_response(raw)

    async def update(
        self,
        object: str,
        *,
        singular_noun: str | None = None,
        plural_noun: str | None = None,
    ) -> Object:
        """Update an existing object."""
        body = self._build_update_body(
            singular_noun=singular_noun,
            plural_noun=plural_noun,
        )
        raw = await self._http.request("PUT", f"/objects/{object}", json=body)
        return self._parse_single_response(raw)
