"""Tests for the Lists resource (sync and async)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import AttioPermissionError, NotFoundError
from attio.models._base import ListResponse
from attio.models.lists import AttioList
from tests.fixtures.factory import (
    MOCK_LIST_CREATED,
    MOCK_LIST_SINGLE,
    MOCK_LIST_UPDATED,
    MOCK_LISTS_LIST,
    MOCK_NOT_FOUND_ERROR,
    MOCK_PERMISSION_ERROR,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_lists"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestListsResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/lists").mock(
            return_value=httpx.Response(200, json=MOCK_LISTS_LIST)
        )
        client = _sync_client()
        result = client.lists.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], AttioList)
        assert result.data[0].api_slug == "sales_pipeline"
        assert result.data[0].id.list_id == "list_01abc123def456"
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/lists/sales_pipeline").mock(
            return_value=httpx.Response(200, json=MOCK_LIST_SINGLE)
        )
        client = _sync_client()
        result = client.lists.get("sales_pipeline")

        assert route.called
        assert isinstance(result, AttioList)
        assert result.api_slug == "sales_pipeline"
        assert result.name == "Sales Pipeline"
        assert result.id.workspace_id == "ws_01abc123def456"
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/lists").mock(
            return_value=httpx.Response(200, json=MOCK_LIST_CREATED)
        )
        client = _sync_client()
        result = client.lists.create(
            name="Onboarding",
            api_slug="onboarding",
            parent_object="companies",
            workspace_access="full-access",
        )

        assert route.called
        assert isinstance(result, AttioList)
        assert result.api_slug == "onboarding"
        assert result.name == "Onboarding"

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "name": "Onboarding",
                "api_slug": "onboarding",
                "parent_object": "companies",
                "workspace_access": "full-access",
            }
        }
        client.close()

    @respx.mock
    def test_create_without_workspace_access(self) -> None:
        route = respx.post(f"{BASE_URL}/lists").mock(
            return_value=httpx.Response(200, json=MOCK_LIST_CREATED)
        )
        client = _sync_client()
        client.lists.create(
            name="Onboarding",
            api_slug="onboarding",
            parent_object="companies",
        )

        request = route.calls[0].request
        body = json.loads(request.content)
        # workspace_access should not be in the body
        assert "workspace_access" not in body["data"]
        client.close()

    @respx.mock
    def test_update(self) -> None:
        route = respx.patch(f"{BASE_URL}/lists/sales_pipeline").mock(
            return_value=httpx.Response(200, json=MOCK_LIST_UPDATED)
        )
        client = _sync_client()
        result = client.lists.update(
            "sales_pipeline",
            name="Updated Pipeline",
            workspace_access="read-only",
        )

        assert route.called
        assert isinstance(result, AttioList)
        assert result.name == "Updated Pipeline"
        assert result.workspace_access == "read-only"

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "name": "Updated Pipeline",
                "workspace_access": "read-only",
            }
        }
        client.close()

    @respx.mock
    def test_update_partial(self) -> None:
        route = respx.patch(f"{BASE_URL}/lists/sales_pipeline").mock(
            return_value=httpx.Response(200, json=MOCK_LIST_UPDATED)
        )
        client = _sync_client()
        client.lists.update("sales_pipeline", name="Updated Pipeline")

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"name": "Updated Pipeline"}}
        client.close()

    @respx.mock
    def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/lists/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.lists.get("nonexistent")
        assert exc_info.value.status_code == 404
        client.close()

    @respx.mock
    def test_list_permission_error(self) -> None:
        respx.get(f"{BASE_URL}/lists").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _sync_client()
        with pytest.raises(AttioPermissionError) as exc_info:
            client.lists.list()
        assert exc_info.value.status_code == 403
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestListsResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/lists").mock(
            return_value=httpx.Response(200, json=MOCK_LISTS_LIST)
        )
        client = _async_client()
        result = await client.lists.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], AttioList)
        assert result.data[0].api_slug == "sales_pipeline"
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/lists/sales_pipeline").mock(
            return_value=httpx.Response(200, json=MOCK_LIST_SINGLE)
        )
        client = _async_client()
        result = await client.lists.get("sales_pipeline")

        assert route.called
        assert isinstance(result, AttioList)
        assert result.api_slug == "sales_pipeline"
        await client.close()

    @respx.mock
    async def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/lists").mock(
            return_value=httpx.Response(200, json=MOCK_LIST_CREATED)
        )
        client = _async_client()
        result = await client.lists.create(
            name="Onboarding",
            api_slug="onboarding",
            parent_object="companies",
            workspace_access="full-access",
        )

        assert route.called
        assert isinstance(result, AttioList)
        assert result.api_slug == "onboarding"
        await client.close()

    @respx.mock
    async def test_update(self) -> None:
        route = respx.patch(f"{BASE_URL}/lists/sales_pipeline").mock(
            return_value=httpx.Response(200, json=MOCK_LIST_UPDATED)
        )
        client = _async_client()
        result = await client.lists.update(
            "sales_pipeline",
            name="Updated Pipeline",
            workspace_access="read-only",
        )

        assert route.called
        assert isinstance(result, AttioList)
        assert result.name == "Updated Pipeline"
        await client.close()

    @respx.mock
    async def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/lists/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.lists.get("nonexistent")
        await client.close()

    @respx.mock
    async def test_list_permission_error(self) -> None:
        respx.get(f"{BASE_URL}/lists").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _async_client()
        with pytest.raises(AttioPermissionError):
            await client.lists.list()
        await client.close()
