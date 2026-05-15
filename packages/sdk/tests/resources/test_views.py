"""Tests for the Views resource (sync and async)."""

from __future__ import annotations

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import AttioPermissionError, NotFoundError
from attio.models._base import PaginatedResponse
from attio.models.views import View

from tests.fixtures.factory import (
    MOCK_NOT_FOUND_ERROR,
    MOCK_PERMISSION_ERROR,
    MOCK_VIEWS_EMPTY,
    MOCK_VIEWS_FOR_LIST,
    MOCK_VIEWS_FOR_OBJECT,
    MOCK_VIEWS_FOR_OBJECT_PAGE_1,
    MOCK_VIEWS_FOR_OBJECT_PAGE_2,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_views"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestViewsResourceSync:
    @respx.mock
    def test_list_for_object(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/views").mock(
            return_value=httpx.Response(200, json=MOCK_VIEWS_FOR_OBJECT)
        )
        client = _sync_client()
        result = client.views.list_for_object("deals")

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], View)
        assert result.data[0].title == "All Deals"
        assert result.data[0].id.view_id == "view_01abc123def456"
        assert result.pagination.next_cursor is None
        client.close()

    @respx.mock
    def test_list_for_object_with_params(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/views").mock(
            return_value=httpx.Response(200, json=MOCK_VIEWS_FOR_OBJECT)
        )
        client = _sync_client()
        result = client.views.list_for_object(
            "deals",
            show_archived=True,
            limit=10,
            cursor="some_cursor",
        )

        assert route.called
        request = route.calls[0].request
        assert request.url.params["show_archived"] == "true"
        assert request.url.params["limit"] == "10"
        assert request.url.params["cursor"] == "some_cursor"
        assert len(result.data) == 2
        client.close()

    @respx.mock
    def test_list_for_list(self) -> None:
        route = respx.get(f"{BASE_URL}/lists/sales_pipeline/views").mock(
            return_value=httpx.Response(200, json=MOCK_VIEWS_FOR_LIST)
        )
        client = _sync_client()
        result = client.views.list_for_list("sales_pipeline")

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert result.data[0].title == "Pipeline View"
        assert result.data[0].id.view_id == "view_03list456abc789"
        client.close()

    @respx.mock
    def test_list_for_object_empty(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/views").mock(
            return_value=httpx.Response(200, json=MOCK_VIEWS_EMPTY)
        )
        client = _sync_client()
        result = client.views.list_for_object("deals")

        assert route.called
        assert len(result.data) == 0
        assert result.pagination.next_cursor is None
        client.close()

    @respx.mock
    def test_list_for_object_permission_error(self) -> None:
        respx.get(f"{BASE_URL}/objects/deals/views").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _sync_client()
        with pytest.raises(AttioPermissionError) as exc_info:
            client.views.list_for_object("deals")
        assert exc_info.value.status_code == 403
        client.close()

    @respx.mock
    def test_list_all_for_object(self) -> None:
        """Test auto-pagination through multiple pages."""
        respx.get(f"{BASE_URL}/objects/deals/views").mock(
            side_effect=[
                httpx.Response(200, json=MOCK_VIEWS_FOR_OBJECT_PAGE_1),
                httpx.Response(200, json=MOCK_VIEWS_FOR_OBJECT_PAGE_2),
            ]
        )
        client = _sync_client()
        views = list(client.views.list_all_for_object("deals"))

        assert len(views) == 2
        assert views[0].title == "All Deals"
        assert views[1].title == "Active Deals"
        client.close()

    @respx.mock
    def test_list_all_for_list(self) -> None:
        respx.get(f"{BASE_URL}/lists/sales_pipeline/views").mock(
            return_value=httpx.Response(200, json=MOCK_VIEWS_FOR_LIST)
        )
        client = _sync_client()
        views = list(client.views.list_all_for_list("sales_pipeline"))

        assert len(views) == 1
        assert views[0].title == "Pipeline View"
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestViewsResourceAsync:
    @respx.mock
    async def test_list_for_object(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/views").mock(
            return_value=httpx.Response(200, json=MOCK_VIEWS_FOR_OBJECT)
        )
        client = _async_client()
        result = await client.views.list_for_object("deals")

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], View)
        assert result.data[0].title == "All Deals"
        await client.close()

    @respx.mock
    async def test_list_for_list(self) -> None:
        route = respx.get(f"{BASE_URL}/lists/sales_pipeline/views").mock(
            return_value=httpx.Response(200, json=MOCK_VIEWS_FOR_LIST)
        )
        client = _async_client()
        result = await client.views.list_for_list("sales_pipeline")

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert result.data[0].title == "Pipeline View"
        await client.close()

    @respx.mock
    async def test_list_for_object_with_params(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/views").mock(
            return_value=httpx.Response(200, json=MOCK_VIEWS_FOR_OBJECT)
        )
        client = _async_client()
        await client.views.list_for_object(
            "deals",
            show_archived=True,
            limit=10,
            cursor="some_cursor",
        )

        request = route.calls[0].request
        assert request.url.params["show_archived"] == "true"
        assert request.url.params["limit"] == "10"
        assert request.url.params["cursor"] == "some_cursor"
        await client.close()

    @respx.mock
    async def test_list_all_for_object(self) -> None:
        """Test async auto-pagination through multiple pages."""
        respx.get(f"{BASE_URL}/objects/deals/views").mock(
            side_effect=[
                httpx.Response(200, json=MOCK_VIEWS_FOR_OBJECT_PAGE_1),
                httpx.Response(200, json=MOCK_VIEWS_FOR_OBJECT_PAGE_2),
            ]
        )
        client = _async_client()
        views = []
        async for view in client.views.list_all_for_object("deals"):
            views.append(view)

        assert len(views) == 2
        assert views[0].title == "All Deals"
        assert views[1].title == "Active Deals"
        await client.close()

    @respx.mock
    async def test_list_all_for_list(self) -> None:
        respx.get(f"{BASE_URL}/lists/sales_pipeline/views").mock(
            return_value=httpx.Response(200, json=MOCK_VIEWS_FOR_LIST)
        )
        client = _async_client()
        views = []
        async for view in client.views.list_all_for_list("sales_pipeline"):
            views.append(view)

        assert len(views) == 1
        assert views[0].title == "Pipeline View"
        await client.close()

    @respx.mock
    async def test_list_for_object_permission_error(self) -> None:
        respx.get(f"{BASE_URL}/objects/deals/views").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _async_client()
        with pytest.raises(AttioPermissionError):
            await client.views.list_for_object("deals")
        await client.close()
