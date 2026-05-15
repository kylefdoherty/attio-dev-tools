"""Tests for the Statuses resource (sync and async)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import AttioPermissionError, NotFoundError
from attio.models._base import ListResponse
from attio.models.select_options import Status

from tests.fixtures.factory import (
    MOCK_NOT_FOUND_ERROR,
    MOCK_PERMISSION_ERROR,
    MOCK_STATUSES_LIST,
    MOCK_STATUS_CREATED,
    MOCK_STATUS_UPDATED,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_statuses"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestStatusesResourceSync:
    @respx.mock
    def test_list_on_object(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUSES_LIST))
        client = _sync_client()
        result = client.statuses.list("objects", "deals", "stage")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Status)
        assert result.data[0].title == "Open"
        assert result.data[0].id.status_id == "sta_01abc123def456"
        assert result.data[0].celebration_enabled is False
        client.close()

    @respx.mock
    def test_list_on_list(self) -> None:
        route = respx.get(
            f"{BASE_URL}/lists/sales_pipeline/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUSES_LIST))
        client = _sync_client()
        result = client.statuses.list("lists", "sales_pipeline", "stage")

        assert route.called
        assert len(result.data) == 2
        client.close()

    @respx.mock
    def test_list_with_show_archived(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUSES_LIST))
        client = _sync_client()
        client.statuses.list("objects", "deals", "stage", show_archived=True)

        assert route.called
        request = route.calls[0].request
        assert "show_archived" in str(request.url)
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUS_CREATED))
        client = _sync_client()
        result = client.statuses.create(
            "objects", "deals", "stage", title="In Progress"
        )

        assert route.called
        assert isinstance(result, Status)
        assert result.title == "In Progress"

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "title": "In Progress",
                "celebration_enabled": False,
            }
        }
        client.close()

    @respx.mock
    def test_create_with_options(self) -> None:
        route = respx.post(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUS_CREATED))
        client = _sync_client()
        client.statuses.create(
            "objects",
            "deals",
            "stage",
            title="In Progress",
            celebration_enabled=True,
            target_time_in_status="P7D",
        )

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "title": "In Progress",
                "celebration_enabled": True,
                "target_time_in_status": "P7D",
            }
        }
        client.close()

    @respx.mock
    def test_update(self) -> None:
        route = respx.patch(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses/sta_01abc123def456"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUS_UPDATED))
        client = _sync_client()
        result = client.statuses.update(
            "objects",
            "deals",
            "stage",
            "sta_01abc123def456",
            title="Closed",
            celebration_enabled=True,
            target_time_in_status="P30D",
        )

        assert route.called
        assert isinstance(result, Status)
        assert result.title == "Closed"
        assert result.celebration_enabled is True

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "title": "Closed",
                "celebration_enabled": True,
                "target_time_in_status": "P30D",
            }
        }
        client.close()

    @respx.mock
    def test_update_partial(self) -> None:
        route = respx.patch(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses/sta_01abc123def456"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUS_UPDATED))
        client = _sync_client()
        client.statuses.update(
            "objects",
            "deals",
            "stage",
            "sta_01abc123def456",
            is_archived=True,
        )

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"is_archived": True}}
        client.close()

    @respx.mock
    def test_list_not_found(self) -> None:
        respx.get(
            f"{BASE_URL}/objects/nonexistent/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR))
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.statuses.list("objects", "nonexistent", "stage")
        assert exc_info.value.status_code == 404
        client.close()

    @respx.mock
    def test_list_permission_error(self) -> None:
        respx.get(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR))
        client = _sync_client()
        with pytest.raises(AttioPermissionError) as exc_info:
            client.statuses.list("objects", "deals", "stage")
        assert exc_info.value.status_code == 403
        client.close()

    @respx.mock
    def test_celebration_enabled(self) -> None:
        """Verify the celebration_enabled field is properly parsed."""
        route = respx.get(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUSES_LIST))
        client = _sync_client()
        result = client.statuses.list("objects", "deals", "stage")

        assert result.data[0].celebration_enabled is False
        assert result.data[1].celebration_enabled is True
        assert result.data[1].title == "Won"
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestStatusesResourceAsync:
    @respx.mock
    async def test_list_on_object(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUSES_LIST))
        client = _async_client()
        result = await client.statuses.list("objects", "deals", "stage")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Status)
        assert result.data[0].title == "Open"
        await client.close()

    @respx.mock
    async def test_list_on_list(self) -> None:
        route = respx.get(
            f"{BASE_URL}/lists/sales_pipeline/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUSES_LIST))
        client = _async_client()
        result = await client.statuses.list("lists", "sales_pipeline", "stage")

        assert route.called
        assert len(result.data) == 2
        await client.close()

    @respx.mock
    async def test_create(self) -> None:
        route = respx.post(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUS_CREATED))
        client = _async_client()
        result = await client.statuses.create(
            "objects", "deals", "stage", title="In Progress"
        )

        assert route.called
        assert isinstance(result, Status)
        assert result.title == "In Progress"
        await client.close()

    @respx.mock
    async def test_create_with_options(self) -> None:
        route = respx.post(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUS_CREATED))
        client = _async_client()
        await client.statuses.create(
            "objects",
            "deals",
            "stage",
            title="In Progress",
            celebration_enabled=True,
            target_time_in_status="P7D",
        )

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body["data"]["celebration_enabled"] is True
        assert body["data"]["target_time_in_status"] == "P7D"
        await client.close()

    @respx.mock
    async def test_update(self) -> None:
        route = respx.patch(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses/sta_01abc123def456"
        ).mock(return_value=httpx.Response(200, json=MOCK_STATUS_UPDATED))
        client = _async_client()
        result = await client.statuses.update(
            "objects",
            "deals",
            "stage",
            "sta_01abc123def456",
            title="Closed",
            celebration_enabled=True,
        )

        assert route.called
        assert isinstance(result, Status)
        assert result.title == "Closed"
        await client.close()

    @respx.mock
    async def test_list_not_found(self) -> None:
        respx.get(
            f"{BASE_URL}/objects/nonexistent/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR))
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.statuses.list("objects", "nonexistent", "stage")
        await client.close()

    @respx.mock
    async def test_list_permission_error(self) -> None:
        respx.get(
            f"{BASE_URL}/objects/deals/attributes/stage/statuses"
        ).mock(return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR))
        client = _async_client()
        with pytest.raises(AttioPermissionError):
            await client.statuses.list("objects", "deals", "stage")
        await client.close()
