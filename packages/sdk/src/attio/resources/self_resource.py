"""Self resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio.models.self_info import SelfInfo
from attio.resources._base import AsyncResource, SyncResource


class _SelfMixin:
    """Shared parameter/body construction logic for the Self resource."""

    @staticmethod
    def _parse_response(raw: dict[str, Any]) -> SelfInfo:
        return SelfInfo.model_validate(raw)


class SelfResource(SyncResource, _SelfMixin):
    """Synchronous Self resource."""

    def identify(self) -> SelfInfo:
        """Get information about the current API token and workspace."""
        raw = self._http.request("GET", "/self")
        return self._parse_response(raw)


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncSelfResource(AsyncResource, _SelfMixin):
    """Asynchronous Self resource."""

    async def identify(self) -> SelfInfo:
        """Get information about the current API token and workspace."""
        raw = await self._http.request("GET", "/self")
        return self._parse_response(raw)
