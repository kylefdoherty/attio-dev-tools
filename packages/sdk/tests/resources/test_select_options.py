"""Tests for the Select Options resource (sync and async)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import AttioPermissionError, NotFoundError
from attio.models._base import ListResponse
from attio.models.select_options import SelectOption

from tests.fixtures.factory import (
    MOCK_NOT_FOUND_ERROR,
    MOCK_PERMISSION_ERROR,
    MOCK_SELECT_OPTIONS_LIST,
    MOCK_SELECT_OPTION_CREATED,
    MOCK_SELECT_OPTION_UPDATED,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_select_options"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestSelectOptionsResourceSync:
    @respx.mock
    def test_list_on_object(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/deals/attributes/priority/options"
        ).mock(return_value=httpx.Response(200, json=MOCK_SELECT_OPTIONS_LIST))
        client = _sync_client()
        result = client.select_options.list("objects", "deals", "priority")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], SelectOption)
        assert result.data[0].title == "High"
        assert result.data[0].id.option_id == "opt_01abc123def456"
        client.close()

    @respx.mock
    def test_list_on_list(self) -> None:
        route = respx.get(
            f"{BASE_URL}/lists/sales_pipeline/attributes/stage/options"
        ).mock(return_value=httpx.Response(200, json=MOCK_SELECT_OPTIONS_LIST))
        client = _sync_client()
        result = client.select_options.list("lists", "sales_pipeline", "stage")

        assert route.called
        assert len(result.data) == 2
        client.close()

    @respx.mock
    def test_list_with_show_archived(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/deals/attributes/priority/options"
        ).mock(return_value=httpx.Response(200, json=MOCK_SELECT_OPTIONS_LIST))
        client = _sync_client()
        client.select_options.list(
            "objects", "deals", "priority", show_archived=True
        )

        assert route.called
        request = route.calls[0].request
        assert "show_archived" in str(request.url)
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(
            f"{BASE_URL}/objects/deals/attributes/priority/options"
        ).mock(return_value=httpx.Response(200, json=MOCK_SELECT_OPTION_CREATED))
        client = _sync_client()
        result = client.select_options.create(
            "objects", "deals", "priority", title="Medium"
        )

        assert route.called
        assert isinstance(result, SelectOption)
        assert result.title == "Medium"

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"title": "Medium"}}
        client.close()

    @respx.mock
    def test_update(self) -> None:
        route = respx.patch(
            f"{BASE_URL}/objects/deals/attributes/priority/options/opt_01abc123def456"
        ).mock(return_value=httpx.Response(200, json=MOCK_SELECT_OPTION_UPDATED))
        client = _sync_client()
        result = client.select_options.update(
            "objects",
            "deals",
            "priority",
            "opt_01abc123def456",
            title="Critical",
        )

        assert route.called
        assert isinstance(result, SelectOption)
        assert result.title == "Critical"

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"title": "Critical"}}
        client.close()

    @respx.mock
    def test_update_archive(self) -> None:
        route = respx.patch(
            f"{BASE_URL}/objects/deals/attributes/priority/options/opt_01abc123def456"
        ).mock(return_value=httpx.Response(200, json=MOCK_SELECT_OPTION_UPDATED))
        client = _sync_client()
        client.select_options.update(
            "objects",
            "deals",
            "priority",
            "opt_01abc123def456",
            is_archived=True,
        )

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"is_archived": True}}
        client.close()

    @respx.mock
    def test_list_not_found(self) -> None:
        respx.get(
            f"{BASE_URL}/objects/nonexistent/attributes/priority/options"
        ).mock(return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR))
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.select_options.list("objects", "nonexistent", "priority")
        assert exc_info.value.status_code == 404
        client.close()

    @respx.mock
    def test_list_permission_error(self) -> None:
        respx.get(
            f"{BASE_URL}/objects/deals/attributes/priority/options"
        ).mock(return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR))
        client = _sync_client()
        with pytest.raises(AttioPermissionError) as exc_info:
            client.select_options.list("objects", "deals", "priority")
        assert exc_info.value.status_code == 403
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestSelectOptionsResourceAsync:
    @respx.mock
    async def test_list_on_object(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/deals/attributes/priority/options"
        ).mock(return_value=httpx.Response(200, json=MOCK_SELECT_OPTIONS_LIST))
        client = _async_client()
        result = await client.select_options.list("objects", "deals", "priority")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], SelectOption)
        assert result.data[0].title == "High"
        await client.close()

    @respx.mock
    async def test_list_on_list(self) -> None:
        route = respx.get(
            f"{BASE_URL}/lists/sales_pipeline/attributes/stage/options"
        ).mock(return_value=httpx.Response(200, json=MOCK_SELECT_OPTIONS_LIST))
        client = _async_client()
        result = await client.select_options.list(
            "lists", "sales_pipeline", "stage"
        )

        assert route.called
        assert len(result.data) == 2
        await client.close()

    @respx.mock
    async def test_create(self) -> None:
        route = respx.post(
            f"{BASE_URL}/objects/deals/attributes/priority/options"
        ).mock(return_value=httpx.Response(200, json=MOCK_SELECT_OPTION_CREATED))
        client = _async_client()
        result = await client.select_options.create(
            "objects", "deals", "priority", title="Medium"
        )

        assert route.called
        assert isinstance(result, SelectOption)
        assert result.title == "Medium"
        await client.close()

    @respx.mock
    async def test_update(self) -> None:
        route = respx.patch(
            f"{BASE_URL}/objects/deals/attributes/priority/options/opt_01abc123def456"
        ).mock(return_value=httpx.Response(200, json=MOCK_SELECT_OPTION_UPDATED))
        client = _async_client()
        result = await client.select_options.update(
            "objects",
            "deals",
            "priority",
            "opt_01abc123def456",
            title="Critical",
        )

        assert route.called
        assert isinstance(result, SelectOption)
        assert result.title == "Critical"
        await client.close()

    @respx.mock
    async def test_list_not_found(self) -> None:
        respx.get(
            f"{BASE_URL}/objects/nonexistent/attributes/priority/options"
        ).mock(return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR))
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.select_options.list("objects", "nonexistent", "priority")
        await client.close()

    @respx.mock
    async def test_list_permission_error(self) -> None:
        respx.get(
            f"{BASE_URL}/objects/deals/attributes/priority/options"
        ).mock(return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR))
        client = _async_client()
        with pytest.raises(AttioPermissionError):
            await client.select_options.list("objects", "deals", "priority")
        await client.close()
