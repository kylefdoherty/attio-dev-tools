"""Attributes resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any, Literal

from attio.models._base import DataWrapper, ListResponse
from attio.models.attributes import Attribute
from attio.resources._base import AsyncResource, SyncResource


class _AttributesMixin:
    """Shared parameter/body construction logic for the Attributes resource."""

    @staticmethod
    def _build_list_params(
        *,
        limit: int | None = None,
        offset: int | None = None,
        show_archived: bool = False,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if show_archived:
            params["show_archived"] = True
        return params

    @staticmethod
    def _build_create_body(
        *,
        title: str,
        description: str | None = None,
        api_slug: str,
        type: str,
        is_required: bool,
        is_unique: bool,
        is_multiselect: bool,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "title": title,
            "description": description,
            "api_slug": api_slug,
            "type": type,
            "is_required": is_required,
            "is_unique": is_unique,
            "is_multiselect": is_multiselect,
        }
        if config is not None:
            data["config"] = config
        else:
            data["config"] = {}
        return {"data": data}

    @staticmethod
    def _build_update_body(
        *,
        title: str | None = None,
        description: str | None = None,
        is_required: bool | None = None,
        is_unique: bool | None = None,
        is_multiselect: bool | None = None,
        is_archived: bool | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if is_required is not None:
            data["is_required"] = is_required
        if is_unique is not None:
            data["is_unique"] = is_unique
        if is_multiselect is not None:
            data["is_multiselect"] = is_multiselect
        if is_archived is not None:
            data["is_archived"] = is_archived
        return {"data": data}

    @staticmethod
    def _base_path(
        target: Literal["objects", "lists"],
        target_id: str,
    ) -> str:
        return f"/{target}/{target_id}/attributes"

    @staticmethod
    def _parse_list_response(raw: dict[str, Any]) -> ListResponse[Attribute]:
        return ListResponse[Attribute].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> Attribute:
        wrapper = DataWrapper[Attribute].model_validate(raw)
        return wrapper.data


class AttributesResource(SyncResource, _AttributesMixin):
    """Synchronous Attributes resource."""

    def list(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        show_archived: bool = False,
    ) -> ListResponse[Attribute]:
        """List all attributes on an object or list."""
        params = self._build_list_params(
            limit=limit, offset=offset, show_archived=show_archived
        )
        path = self._base_path(target, target_id)
        raw = self._http.request("GET", path, params=params)
        return self._parse_list_response(raw)

    def get(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
    ) -> Attribute:
        """Get a single attribute by slug or ID."""
        path = f"{self._base_path(target, target_id)}/{attribute}"
        raw = self._http.request("GET", path)
        return self._parse_single_response(raw)

    def create(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        *,
        title: str,
        description: str | None = None,
        api_slug: str,
        type: str,
        is_required: bool,
        is_unique: bool,
        is_multiselect: bool,
        config: dict[str, Any] | None = None,
    ) -> Attribute:
        """Create a new attribute on an object or list."""
        body = self._build_create_body(
            title=title,
            description=description,
            api_slug=api_slug,
            type=type,
            is_required=is_required,
            is_unique=is_unique,
            is_multiselect=is_multiselect,
            config=config,
        )
        path = self._base_path(target, target_id)
        raw = self._http.request("POST", path, json=body)
        return self._parse_single_response(raw)

    def update(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
        *,
        title: str | None = None,
        description: str | None = None,
        is_required: bool | None = None,
        is_unique: bool | None = None,
        is_multiselect: bool | None = None,
        is_archived: bool | None = None,
    ) -> Attribute:
        """Update an existing attribute on an object or list."""
        body = self._build_update_body(
            title=title,
            description=description,
            is_required=is_required,
            is_unique=is_unique,
            is_multiselect=is_multiselect,
            is_archived=is_archived,
        )
        path = f"{self._base_path(target, target_id)}/{attribute}"
        raw = self._http.request("PATCH", path, json=body)
        return self._parse_single_response(raw)


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncAttributesResource(AsyncResource, _AttributesMixin):
    """Asynchronous Attributes resource."""

    async def list(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        show_archived: bool = False,
    ) -> ListResponse[Attribute]:
        """List all attributes on an object or list."""
        params = self._build_list_params(
            limit=limit, offset=offset, show_archived=show_archived
        )
        path = self._base_path(target, target_id)
        raw = await self._http.request("GET", path, params=params)
        return self._parse_list_response(raw)

    async def get(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
    ) -> Attribute:
        """Get a single attribute by slug or ID."""
        path = f"{self._base_path(target, target_id)}/{attribute}"
        raw = await self._http.request("GET", path)
        return self._parse_single_response(raw)

    async def create(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        *,
        title: str,
        description: str | None = None,
        api_slug: str,
        type: str,
        is_required: bool,
        is_unique: bool,
        is_multiselect: bool,
        config: dict[str, Any] | None = None,
    ) -> Attribute:
        """Create a new attribute on an object or list."""
        body = self._build_create_body(
            title=title,
            description=description,
            api_slug=api_slug,
            type=type,
            is_required=is_required,
            is_unique=is_unique,
            is_multiselect=is_multiselect,
            config=config,
        )
        path = self._base_path(target, target_id)
        raw = await self._http.request("POST", path, json=body)
        return self._parse_single_response(raw)

    async def update(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
        *,
        title: str | None = None,
        description: str | None = None,
        is_required: bool | None = None,
        is_unique: bool | None = None,
        is_multiselect: bool | None = None,
        is_archived: bool | None = None,
    ) -> Attribute:
        """Update an existing attribute on an object or list."""
        body = self._build_update_body(
            title=title,
            description=description,
            is_required=is_required,
            is_unique=is_unique,
            is_multiselect=is_multiselect,
            is_archived=is_archived,
        )
        path = f"{self._base_path(target, target_id)}/{attribute}"
        raw = await self._http.request("PATCH", path, json=body)
        return self._parse_single_response(raw)
