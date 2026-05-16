"""Select Options resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any, Literal

from attio.models._base import DataWrapper, ListResponse
from attio.models.select_options import SelectOption
from attio.resources._base import AsyncResource, SyncResource


class _SelectOptionsMixin:
    """Shared parameter/body construction logic for the Select Options resource."""

    @staticmethod
    def _build_list_params(
        *,
        show_archived: bool = False,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if show_archived:
            params["show_archived"] = True
        return params

    @staticmethod
    def _build_create_body(*, title: str) -> dict[str, Any]:
        return {"data": {"title": title}}

    @staticmethod
    def _build_update_body(
        *,
        title: str | None = None,
        is_archived: bool | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if title is not None:
            data["title"] = title
        if is_archived is not None:
            data["is_archived"] = is_archived
        return {"data": data}

    @staticmethod
    def _base_path(
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
    ) -> str:
        return f"/{target}/{target_id}/attributes/{attribute}/options"

    @staticmethod
    def _parse_list_response(raw: dict[str, Any]) -> ListResponse[SelectOption]:
        return ListResponse[SelectOption].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> SelectOption:
        wrapper = DataWrapper[SelectOption].model_validate(raw)
        return wrapper.data


class SelectOptionsResource(SyncResource, _SelectOptionsMixin):
    """Synchronous Select Options resource."""

    def list(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
        *,
        show_archived: bool = False,
    ) -> ListResponse[SelectOption]:
        """List all select options for an attribute."""
        params = self._build_list_params(show_archived=show_archived)
        path = self._base_path(target, target_id, attribute)
        raw = self._http.request("GET", path, params=params)
        return self._parse_list_response(raw)

    def create(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
        *,
        title: str,
    ) -> SelectOption:
        """Create a new select option for an attribute."""
        body = self._build_create_body(title=title)
        path = self._base_path(target, target_id, attribute)
        raw = self._http.request("POST", path, json=body)
        return self._parse_single_response(raw)

    def update(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
        option_id: str,
        *,
        title: str | None = None,
        is_archived: bool | None = None,
    ) -> SelectOption:
        """Update an existing select option."""
        body = self._build_update_body(title=title, is_archived=is_archived)
        path = f"{self._base_path(target, target_id, attribute)}/{option_id}"
        raw = self._http.request("PATCH", path, json=body)
        return self._parse_single_response(raw)


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncSelectOptionsResource(AsyncResource, _SelectOptionsMixin):
    """Asynchronous Select Options resource."""

    async def list(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
        *,
        show_archived: bool = False,
    ) -> ListResponse[SelectOption]:
        """List all select options for an attribute."""
        params = self._build_list_params(show_archived=show_archived)
        path = self._base_path(target, target_id, attribute)
        raw = await self._http.request("GET", path, params=params)
        return self._parse_list_response(raw)

    async def create(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
        *,
        title: str,
    ) -> SelectOption:
        """Create a new select option for an attribute."""
        body = self._build_create_body(title=title)
        path = self._base_path(target, target_id, attribute)
        raw = await self._http.request("POST", path, json=body)
        return self._parse_single_response(raw)

    async def update(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
        option_id: str,
        *,
        title: str | None = None,
        is_archived: bool | None = None,
    ) -> SelectOption:
        """Update an existing select option."""
        body = self._build_update_body(title=title, is_archived=is_archived)
        path = f"{self._base_path(target, target_id, attribute)}/{option_id}"
        raw = await self._http.request("PATCH", path, json=body)
        return self._parse_single_response(raw)
