"""Tests for the Webhooks resource (sync and async)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import NotFoundError
from attio.models._base import ListResponse
from attio.models.webhooks import Webhook

from tests.fixtures.factory import (
    MOCK_NOT_FOUND_ERROR,
    MOCK_WEBHOOK_CREATED,
    MOCK_WEBHOOK_DELETE,
    MOCK_WEBHOOK_SINGLE,
    MOCK_WEBHOOK_UPDATED,
    MOCK_WEBHOOKS_LIST,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_webhooks"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestWebhooksResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/webhooks").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOKS_LIST)
        )
        client = _sync_client()
        result = client.webhooks.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Webhook)
        assert result.data[0].target_url == "https://example.com/webhooks/attio"
        assert result.data[0].id.webhook_id == "wh_01abc123def456"
        assert result.data[0].status == "active"
        assert len(result.data[0].subscriptions) == 2
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/webhooks/wh_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_SINGLE)
        )
        client = _sync_client()
        result = client.webhooks.get("wh_01abc123def456")

        assert route.called
        assert isinstance(result, Webhook)
        assert result.target_url == "https://example.com/webhooks/attio"
        assert result.status == "active"
        assert result.subscriptions[0].event_type == "record.created"
        assert result.subscriptions[1].filter == {"$object": "people"}
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/webhooks").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_CREATED)
        )
        client = _sync_client()
        result = client.webhooks.create(
            target_url="https://example.com/webhooks/new",
            subscriptions=[
                {"event_type": "note.created", "filter": None},
            ],
        )

        assert route.called
        assert isinstance(result, Webhook)
        assert result.target_url == "https://example.com/webhooks/new"
        assert result.secret == "whsec_test_secret_12345"
        assert result.status == "active"

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "target_url": "https://example.com/webhooks/new",
                "subscriptions": [
                    {"event_type": "note.created", "filter": None},
                ],
            }
        }
        client.close()

    @respx.mock
    def test_update(self) -> None:
        route = respx.patch(f"{BASE_URL}/webhooks/wh_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_UPDATED)
        )
        client = _sync_client()
        result = client.webhooks.update(
            "wh_01abc123def456",
            target_url="https://example.com/webhooks/updated",
            subscriptions=[
                {"event_type": "record.created", "filter": None},
                {"event_type": "record.deleted", "filter": None},
            ],
        )

        assert route.called
        assert isinstance(result, Webhook)
        assert result.target_url == "https://example.com/webhooks/updated"
        assert len(result.subscriptions) == 2

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "target_url": "https://example.com/webhooks/updated",
                "subscriptions": [
                    {"event_type": "record.created", "filter": None},
                    {"event_type": "record.deleted", "filter": None},
                ],
            }
        }
        client.close()

    @respx.mock
    def test_update_partial(self) -> None:
        route = respx.patch(f"{BASE_URL}/webhooks/wh_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_UPDATED)
        )
        client = _sync_client()
        client.webhooks.update(
            "wh_01abc123def456",
            target_url="https://example.com/webhooks/updated",
        )

        request = route.calls[0].request
        body = json.loads(request.content)
        # Only the specified field should be in the body
        assert body == {
            "data": {"target_url": "https://example.com/webhooks/updated"}
        }
        client.close()

    @respx.mock
    def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/webhooks/wh_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_DELETE)
        )
        client = _sync_client()
        result = client.webhooks.delete("wh_01abc123def456")

        assert route.called
        assert result is None
        client.close()

    @respx.mock
    def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/webhooks/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.webhooks.get("nonexistent")
        assert exc_info.value.status_code == 404
        client.close()

    @respx.mock
    def test_full_crud_cycle(self) -> None:
        """Test a full create-read-update-delete cycle."""
        # Create
        respx.post(f"{BASE_URL}/webhooks").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_CREATED)
        )
        client = _sync_client()
        created = client.webhooks.create(
            target_url="https://example.com/webhooks/new",
            subscriptions=[{"event_type": "note.created"}],
        )
        assert created.secret == "whsec_test_secret_12345"
        webhook_id = created.id.webhook_id

        # Read
        respx.get(f"{BASE_URL}/webhooks/{webhook_id}").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_SINGLE)
        )
        fetched = client.webhooks.get(webhook_id)
        assert isinstance(fetched, Webhook)

        # Update
        respx.patch(f"{BASE_URL}/webhooks/{webhook_id}").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_UPDATED)
        )
        updated = client.webhooks.update(
            webhook_id,
            target_url="https://example.com/webhooks/updated",
        )
        assert updated.target_url == "https://example.com/webhooks/updated"

        # Delete
        respx.delete(f"{BASE_URL}/webhooks/{webhook_id}").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_DELETE)
        )
        result = client.webhooks.delete(webhook_id)
        assert result is None
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestWebhooksResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/webhooks").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOKS_LIST)
        )
        client = _async_client()
        result = await client.webhooks.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Webhook)
        assert result.data[0].target_url == "https://example.com/webhooks/attio"
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/webhooks/wh_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_SINGLE)
        )
        client = _async_client()
        result = await client.webhooks.get("wh_01abc123def456")

        assert route.called
        assert isinstance(result, Webhook)
        assert result.target_url == "https://example.com/webhooks/attio"
        await client.close()

    @respx.mock
    async def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/webhooks").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_CREATED)
        )
        client = _async_client()
        result = await client.webhooks.create(
            target_url="https://example.com/webhooks/new",
            subscriptions=[{"event_type": "note.created"}],
        )

        assert route.called
        assert isinstance(result, Webhook)
        assert result.secret == "whsec_test_secret_12345"
        await client.close()

    @respx.mock
    async def test_update(self) -> None:
        route = respx.patch(f"{BASE_URL}/webhooks/wh_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_UPDATED)
        )
        client = _async_client()
        result = await client.webhooks.update(
            "wh_01abc123def456",
            target_url="https://example.com/webhooks/updated",
        )

        assert route.called
        assert isinstance(result, Webhook)
        assert result.target_url == "https://example.com/webhooks/updated"
        await client.close()

    @respx.mock
    async def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/webhooks/wh_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_WEBHOOK_DELETE)
        )
        client = _async_client()
        result = await client.webhooks.delete("wh_01abc123def456")

        assert route.called
        assert result is None
        await client.close()

    @respx.mock
    async def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/webhooks/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.webhooks.get("nonexistent")
        await client.close()
