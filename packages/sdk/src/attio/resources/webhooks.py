"""Webhooks resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio.models._base import DataWrapper, ListResponse
from attio.models.webhooks import Webhook
from attio.resources._base import AsyncResource, SyncResource


class _WebhooksMixin:
    """Shared parameter/body construction logic for the Webhooks resource."""

    @staticmethod
    def _build_create_body(
        *,
        target_url: str,
        subscriptions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "data": {
                "target_url": target_url,
                "subscriptions": subscriptions,
            }
        }

    @staticmethod
    def _build_update_body(
        *,
        target_url: str | None = None,
        subscriptions: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if target_url is not None:
            data["target_url"] = target_url
        if subscriptions is not None:
            data["subscriptions"] = subscriptions
        return {"data": data}

    @staticmethod
    def _parse_list_response(raw: dict[str, Any]) -> ListResponse[Webhook]:
        return ListResponse[Webhook].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> Webhook:
        wrapper = DataWrapper[Webhook].model_validate(raw)
        return wrapper.data


class WebhooksResource(SyncResource, _WebhooksMixin):
    """Synchronous Webhooks resource."""

    def list(self) -> ListResponse[Webhook]:
        """List all webhooks in the workspace."""
        raw = self._http.request("GET", "/webhooks")
        return self._parse_list_response(raw)

    def get(self, webhook_id: str) -> Webhook:
        """Get a single webhook by ID."""
        raw = self._http.request("GET", f"/webhooks/{webhook_id}")
        return self._parse_single_response(raw)

    def create(
        self,
        *,
        target_url: str,
        subscriptions: list[dict[str, Any]],
    ) -> Webhook:
        """Create a new webhook."""
        body = self._build_create_body(
            target_url=target_url,
            subscriptions=subscriptions,
        )
        raw = self._http.request("POST", "/webhooks", json=body)
        return self._parse_single_response(raw)

    def update(
        self,
        webhook_id: str,
        *,
        target_url: str | None = None,
        subscriptions: list[dict[str, Any]] | None = None,
    ) -> Webhook:
        """Update an existing webhook."""
        body = self._build_update_body(
            target_url=target_url,
            subscriptions=subscriptions,
        )
        raw = self._http.request("PATCH", f"/webhooks/{webhook_id}", json=body)
        return self._parse_single_response(raw)

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook by ID."""
        self._http.request("DELETE", f"/webhooks/{webhook_id}")


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncWebhooksResource(AsyncResource, _WebhooksMixin):
    """Asynchronous Webhooks resource."""

    async def list(self) -> ListResponse[Webhook]:
        """List all webhooks in the workspace."""
        raw = await self._http.request("GET", "/webhooks")
        return self._parse_list_response(raw)

    async def get(self, webhook_id: str) -> Webhook:
        """Get a single webhook by ID."""
        raw = await self._http.request("GET", f"/webhooks/{webhook_id}")
        return self._parse_single_response(raw)

    async def create(
        self,
        *,
        target_url: str,
        subscriptions: list[dict[str, Any]],
    ) -> Webhook:
        """Create a new webhook."""
        body = self._build_create_body(
            target_url=target_url,
            subscriptions=subscriptions,
        )
        raw = await self._http.request("POST", "/webhooks", json=body)
        return self._parse_single_response(raw)

    async def update(
        self,
        webhook_id: str,
        *,
        target_url: str | None = None,
        subscriptions: list[dict[str, Any]] | None = None,
    ) -> Webhook:
        """Update an existing webhook."""
        body = self._build_update_body(
            target_url=target_url,
            subscriptions=subscriptions,
        )
        raw = await self._http.request("PATCH", f"/webhooks/{webhook_id}", json=body)
        return self._parse_single_response(raw)

    async def delete(self, webhook_id: str) -> None:
        """Delete a webhook by ID."""
        await self._http.request("DELETE", f"/webhooks/{webhook_id}")
