"""Tests for the Attributes resource (sync and async)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import AttioPermissionError, NotFoundError
from attio.models._base import ListResponse
from attio.models.attributes import Attribute

from tests.fixtures.factory import (
    MOCK_ATTRIBUTE,
    MOCK_ATTRIBUTES_LIST,
    MOCK_ATTRIBUTE_CREATED,
    MOCK_ATTRIBUTE_SINGLE,
    MOCK_ATTRIBUTE_UPDATED,
    MOCK_NOT_FOUND_ERROR,
    MOCK_PERMISSION_ERROR,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_attributes"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestAttributesResourceSync:
    @respx.mock
    def test_list_on_object(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/attributes").mock(
            return_value=httpx.Response(200, json=MOCK_ATTRIBUTES_LIST)
        )
        client = _sync_client()
        result = client.attributes.list("objects", "deals")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Attribute)
        assert result.data[0].api_slug == "deal_value"
        assert result.data[0].id.attribute_id == "attr_01abc123def456"
        client.close()

    @respx.mock
    def test_list_on_list(self) -> None:
        route = respx.get(f"{BASE_URL}/lists/sales_pipeline/attributes").mock(
            return_value=httpx.Response(200, json=MOCK_ATTRIBUTES_LIST)
        )
        client = _sync_client()
        result = client.attributes.list("lists", "sales_pipeline")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        client.close()

    @respx.mock
    def test_list_with_params(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/attributes").mock(
            return_value=httpx.Response(200, json=MOCK_ATTRIBUTES_LIST)
        )
        client = _sync_client()
        client.attributes.list(
            "objects", "deals", limit=10, offset=5, show_archived=True
        )

        assert route.called
        request = route.calls[0].request
        assert "limit=10" in str(request.url)
        assert "offset=5" in str(request.url)
        assert "show_archived" in str(request.url)
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/deals/attributes/deal_value"
        ).mock(return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_SINGLE))
        client = _sync_client()
        result = client.attributes.get("objects", "deals", "deal_value")

        assert route.called
        assert isinstance(result, Attribute)
        assert result.api_slug == "deal_value"
        assert result.title == "Deal Value"
        assert result.type == "currency"
        assert result.id.workspace_id == "ws_01abc123def456"
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/deals/attributes").mock(
            return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_CREATED)
        )
        client = _sync_client()
        result = client.attributes.create(
            "objects",
            "deals",
            title="Priority",
            description="Task priority level",
            api_slug="priority",
            type="select",
            is_required=True,
            is_unique=False,
            is_multiselect=False,
        )

        assert route.called
        assert isinstance(result, Attribute)
        assert result.api_slug == "priority"
        assert result.title == "Priority"

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "title": "Priority",
                "description": "Task priority level",
                "api_slug": "priority",
                "type": "select",
                "is_required": True,
                "is_unique": False,
                "is_multiselect": False,
                "config": {},
            }
        }
        client.close()

    @respx.mock
    def test_create_with_config(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/deals/attributes").mock(
            return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_CREATED)
        )
        client = _sync_client()
        client.attributes.create(
            "objects",
            "deals",
            title="Priority",
            api_slug="priority",
            type="select",
            is_required=True,
            is_unique=False,
            is_multiselect=False,
            config={"currency": {"default_currency_code": "EUR"}},
        )

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body["data"]["config"] == {
            "currency": {"default_currency_code": "EUR"}
        }
        client.close()

    @respx.mock
    def test_update(self) -> None:
        route = respx.patch(
            f"{BASE_URL}/objects/deals/attributes/deal_value"
        ).mock(return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_UPDATED))
        client = _sync_client()
        result = client.attributes.update(
            "objects",
            "deals",
            "deal_value",
            title="Deal Amount",
            is_required=True,
        )

        assert route.called
        assert isinstance(result, Attribute)
        assert result.title == "Deal Amount"

        # Verify request body only includes provided fields
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "title": "Deal Amount",
                "is_required": True,
            }
        }
        client.close()

    @respx.mock
    def test_update_partial(self) -> None:
        route = respx.patch(
            f"{BASE_URL}/objects/deals/attributes/deal_value"
        ).mock(return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_UPDATED))
        client = _sync_client()
        client.attributes.update(
            "objects", "deals", "deal_value", is_archived=True
        )

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"is_archived": True}}
        client.close()

    @respx.mock
    def test_get_not_found(self) -> None:
        respx.get(
            f"{BASE_URL}/objects/deals/attributes/nonexistent"
        ).mock(return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR))
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.attributes.get("objects", "deals", "nonexistent")
        assert exc_info.value.status_code == 404
        client.close()

    @respx.mock
    def test_list_permission_error(self) -> None:
        respx.get(f"{BASE_URL}/objects/deals/attributes").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _sync_client()
        with pytest.raises(AttioPermissionError) as exc_info:
            client.attributes.list("objects", "deals")
        assert exc_info.value.status_code == 403
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestAttributesResourceAsync:
    @respx.mock
    async def test_list_on_object(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/attributes").mock(
            return_value=httpx.Response(200, json=MOCK_ATTRIBUTES_LIST)
        )
        client = _async_client()
        result = await client.attributes.list("objects", "deals")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Attribute)
        assert result.data[0].api_slug == "deal_value"
        await client.close()

    @respx.mock
    async def test_list_on_list(self) -> None:
        route = respx.get(f"{BASE_URL}/lists/sales_pipeline/attributes").mock(
            return_value=httpx.Response(200, json=MOCK_ATTRIBUTES_LIST)
        )
        client = _async_client()
        result = await client.attributes.list("lists", "sales_pipeline")

        assert route.called
        assert len(result.data) == 2
        await client.close()

    @respx.mock
    async def test_list_with_params(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/attributes").mock(
            return_value=httpx.Response(200, json=MOCK_ATTRIBUTES_LIST)
        )
        client = _async_client()
        await client.attributes.list(
            "objects", "deals", limit=10, offset=5, show_archived=True
        )

        request = route.calls[0].request
        assert "limit=10" in str(request.url)
        assert "offset=5" in str(request.url)
        assert "show_archived" in str(request.url)
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/deals/attributes/deal_value"
        ).mock(return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_SINGLE))
        client = _async_client()
        result = await client.attributes.get("objects", "deals", "deal_value")

        assert route.called
        assert isinstance(result, Attribute)
        assert result.api_slug == "deal_value"
        await client.close()

    @respx.mock
    async def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/deals/attributes").mock(
            return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_CREATED)
        )
        client = _async_client()
        result = await client.attributes.create(
            "objects",
            "deals",
            title="Priority",
            description="Task priority level",
            api_slug="priority",
            type="select",
            is_required=True,
            is_unique=False,
            is_multiselect=False,
        )

        assert route.called
        assert isinstance(result, Attribute)
        assert result.api_slug == "priority"
        await client.close()

    @respx.mock
    async def test_update(self) -> None:
        route = respx.patch(
            f"{BASE_URL}/objects/deals/attributes/deal_value"
        ).mock(return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_UPDATED))
        client = _async_client()
        result = await client.attributes.update(
            "objects",
            "deals",
            "deal_value",
            title="Deal Amount",
            is_required=True,
        )

        assert route.called
        assert isinstance(result, Attribute)
        assert result.title == "Deal Amount"
        await client.close()

    @respx.mock
    async def test_get_not_found(self) -> None:
        respx.get(
            f"{BASE_URL}/objects/deals/attributes/nonexistent"
        ).mock(return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR))
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.attributes.get("objects", "deals", "nonexistent")
        await client.close()

    @respx.mock
    async def test_list_permission_error(self) -> None:
        respx.get(f"{BASE_URL}/objects/deals/attributes").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _async_client()
        with pytest.raises(AttioPermissionError):
            await client.attributes.list("objects", "deals")
        await client.close()
