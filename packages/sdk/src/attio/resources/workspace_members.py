"""Workspace Members resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio.models._base import DataWrapper, ListResponse
from attio.models.workspace_members import WorkspaceMember
from attio.resources._base import AsyncResource, SyncResource


class _WorkspaceMembersMixin:
    """Shared parameter/body construction logic for the Workspace Members resource."""

    @staticmethod
    def _parse_list_response(raw: dict[str, Any]) -> ListResponse[WorkspaceMember]:
        return ListResponse[WorkspaceMember].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> WorkspaceMember:
        wrapper = DataWrapper[WorkspaceMember].model_validate(raw)
        return wrapper.data


class WorkspaceMembersResource(SyncResource, _WorkspaceMembersMixin):
    """Synchronous Workspace Members resource (read-only)."""

    def list(self) -> ListResponse[WorkspaceMember]:
        """List all workspace members."""
        raw = self._http.request("GET", "/workspace_members")
        return self._parse_list_response(raw)

    def get(self, member_id: str) -> WorkspaceMember:
        """Get a single workspace member by ID."""
        raw = self._http.request("GET", f"/workspace_members/{member_id}")
        return self._parse_single_response(raw)


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncWorkspaceMembersResource(AsyncResource, _WorkspaceMembersMixin):
    """Asynchronous Workspace Members resource (read-only)."""

    async def list(self) -> ListResponse[WorkspaceMember]:
        """List all workspace members."""
        raw = await self._http.request("GET", "/workspace_members")
        return self._parse_list_response(raw)

    async def get(self, member_id: str) -> WorkspaceMember:
        """Get a single workspace member by ID."""
        raw = await self._http.request("GET", f"/workspace_members/{member_id}")
        return self._parse_single_response(raw)
