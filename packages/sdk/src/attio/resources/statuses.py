"""Statuses resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any, Literal

from attio.models._base import DataWrapper, ListResponse
from attio.models.select_options import Status
from attio.resources._base import AsyncResource, SyncResource


class _StatusesMixin:
    """Shared parameter/body construction logic for the Statuses resource."""

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
    def _build_create_body(
        *,
        title: str,
        celebration_enabled: bool = False,
        target_time_in_status: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "title": title,
            "celebration_enabled": celebration_enabled,
        }
        if target_time_in_status is not None:
            data["target_time_in_status"] = target_time_in_status
        return {"data": data}

    @staticmethod
    def _build_update_body(
        *,
        title: str | None = None,
        is_archived: bool | None = None,
        celebration_enabled: bool | None = None,
        target_time_in_status: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if title is not None:
            data["title"] = title
        if is_archived is not None:
            data["is_archived"] = is_archived
        if celebration_enabled is not None:
            data["celebration_enabled"] = celebration_enabled
        if target_time_in_status is not None:
            data["target_time_in_status"] = target_time_in_status
        return {"data": data}

    @staticmethod
    def _base_path(
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
    ) -> str:
        return f"/{target}/{target_id}/attributes/{attribute}/statuses"

    @staticmethod
    def _parse_list_response(raw: dict[str, Any]) -> ListResponse[Status]:
        return ListResponse[Status].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> Status:
        wrapper = DataWrapper[Status].model_validate(raw)
        return wrapper.data


class StatusesResource(SyncResource, _StatusesMixin):
    """Synchronous Statuses resource."""

    def list(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
        *,
        show_archived: bool = False,
    ) -> ListResponse[Status]:
        """List all statuses for an attribute."""
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
        celebration_enabled: bool = False,
        target_time_in_status: str | None = None,
    ) -> Status:
        """Create a new status for an attribute."""
        body = self._build_create_body(
            title=title,
            celebration_enabled=celebration_enabled,
            target_time_in_status=target_time_in_status,
        )
        path = self._base_path(target, target_id, attribute)
        raw = self._http.request("POST", path, json=body)
        return self._parse_single_response(raw)

    def update(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
        status_id: str,
        *,
        title: str | None = None,
        is_archived: bool | None = None,
        celebration_enabled: bool | None = None,
        target_time_in_status: str | None = None,
    ) -> Status:
        """Update an existing status."""
        body = self._build_update_body(
            title=title,
            is_archived=is_archived,
            celebration_enabled=celebration_enabled,
            target_time_in_status=target_time_in_status,
        )
        path = f"{self._base_path(target, target_id, attribute)}/{status_id}"
        raw = self._http.request("PATCH", path, json=body)
        return self._parse_single_response(raw)


class AsyncStatusesResource(AsyncResource, _StatusesMixin):
    """Asynchronous Statuses resource."""

    async def list(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
        *,
        show_archived: bool = False,
    ) -> ListResponse[Status]:
        """List all statuses for an attribute."""
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
        celebration_enabled: bool = False,
        target_time_in_status: str | None = None,
    ) -> Status:
        """Create a new status for an attribute."""
        body = self._build_create_body(
            title=title,
            celebration_enabled=celebration_enabled,
            target_time_in_status=target_time_in_status,
        )
        path = self._base_path(target, target_id, attribute)
        raw = await self._http.request("POST", path, json=body)
        return self._parse_single_response(raw)

    async def update(
        self,
        target: Literal["objects", "lists"],
        target_id: str,
        attribute: str,
        status_id: str,
        *,
        title: str | None = None,
        is_archived: bool | None = None,
        celebration_enabled: bool | None = None,
        target_time_in_status: str | None = None,
    ) -> Status:
        """Update an existing status."""
        body = self._build_update_body(
            title=title,
            is_archived=is_archived,
            celebration_enabled=celebration_enabled,
            target_time_in_status=target_time_in_status,
        )
        path = f"{self._base_path(target, target_id, attribute)}/{status_id}"
        raw = await self._http.request("PATCH", path, json=body)
        return self._parse_single_response(raw)
