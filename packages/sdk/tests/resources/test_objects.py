"""Tests for the Objects resource (sync and async)."""

from __future__ import annotations

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import AttioPermissionError, NotFoundError
from attio.models._base import ListResponse
from attio.models.objects import Object

from tests.fixtures.factory import (
    MOCK_NOT_FOUND_ERROR,
    MOCK_OBJECT,
    MOCK_OBJECT_CREATED,
    MOCK_OBJECT_SINGLE,
    MOCK_OBJECT_UPDATED,
    MOCK_OBJECTS_LIST,
    MOCK_PERMISSION_ERROR,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_objects"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestObjectsResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/objects").mock(
            return_value=httpx.Response(200, json=MOCK_OBJECTS_LIST)
        )
        client = _sync_client()
        result = client.objects.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Object)
        assert result.data[0].api_slug == "deals"
        assert result.data[0].id.object_id == "obj_01abc123def456"
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals").mock(
            return_value=httpx.Response(200, json=MOCK_OBJECT_SINGLE)
        )
        client = _sync_client()
        result = client.objects.get("deals")

        assert route.called
        assert isinstance(result, Object)
        assert result.api_slug == "deals"
        assert result.id.workspace_id == "ws_01abc123def456"
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/objects").mock(
            return_value=httpx.Response(200, json=MOCK_OBJECT_CREATED)
        )
        client = _sync_client()
        result = client.objects.create(
            api_slug="projects",
            singular_noun="Project",
            plural_noun="Projects",
        )

        assert route.called
        assert isinstance(result, Object)
        assert result.api_slug == "projects"
        assert result.singular_noun == "Project"
        assert result.plural_noun == "Projects"

        # Verify request body
        request = route.calls[0].request
        import json

        body = json.loads(request.content)
        assert body == {
            "data": {
                "api_slug": "projects",
                "singular_noun": "Project",
                "plural_noun": "Projects",
            }
        }
        client.close()

    @respx.mock
    def test_update(self) -> None:
        route = respx.put(f"{BASE_URL}/objects/deals").mock(
            return_value=httpx.Response(200, json=MOCK_OBJECT_UPDATED)
        )
        client = _sync_client()
        result = client.objects.update(
            "deals",
            singular_noun="Opportunity",
            plural_noun="Opportunities",
        )

        assert route.called
        assert isinstance(result, Object)
        assert result.singular_noun == "Opportunity"
        assert result.plural_noun == "Opportunities"

        # Verify request body
        request = route.calls[0].request
        import json

        body = json.loads(request.content)
        assert body == {
            "data": {
                "singular_noun": "Opportunity",
                "plural_noun": "Opportunities",
            }
        }
        client.close()

    @respx.mock
    def test_update_partial(self) -> None:
        route = respx.put(f"{BASE_URL}/objects/deals").mock(
            return_value=httpx.Response(200, json=MOCK_OBJECT_UPDATED)
        )
        client = _sync_client()
        client.objects.update("deals", singular_noun="Opportunity")

        request = route.calls[0].request
        import json

        body = json.loads(request.content)
        # Only the specified field should be in the body
        assert body == {"data": {"singular_noun": "Opportunity"}}
        client.close()

    @respx.mock
    def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/objects/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.objects.get("nonexistent")
        assert exc_info.value.status_code == 404
        client.close()

    @respx.mock
    def test_list_permission_error(self) -> None:
        respx.get(f"{BASE_URL}/objects").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _sync_client()
        with pytest.raises(AttioPermissionError) as exc_info:
            client.objects.list()
        assert exc_info.value.status_code == 403
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestObjectsResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/objects").mock(
            return_value=httpx.Response(200, json=MOCK_OBJECTS_LIST)
        )
        client = _async_client()
        result = await client.objects.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Object)
        assert result.data[0].api_slug == "deals"
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals").mock(
            return_value=httpx.Response(200, json=MOCK_OBJECT_SINGLE)
        )
        client = _async_client()
        result = await client.objects.get("deals")

        assert route.called
        assert isinstance(result, Object)
        assert result.api_slug == "deals"
        await client.close()

    @respx.mock
    async def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/objects").mock(
            return_value=httpx.Response(200, json=MOCK_OBJECT_CREATED)
        )
        client = _async_client()
        result = await client.objects.create(
            api_slug="projects",
            singular_noun="Project",
            plural_noun="Projects",
        )

        assert route.called
        assert isinstance(result, Object)
        assert result.api_slug == "projects"
        await client.close()

    @respx.mock
    async def test_update(self) -> None:
        route = respx.put(f"{BASE_URL}/objects/deals").mock(
            return_value=httpx.Response(200, json=MOCK_OBJECT_UPDATED)
        )
        client = _async_client()
        result = await client.objects.update(
            "deals",
            singular_noun="Opportunity",
            plural_noun="Opportunities",
        )

        assert route.called
        assert isinstance(result, Object)
        assert result.singular_noun == "Opportunity"
        await client.close()

    @respx.mock
    async def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/objects/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.objects.get("nonexistent")
        await client.close()

    @respx.mock
    async def test_list_permission_error(self) -> None:
        respx.get(f"{BASE_URL}/objects").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _async_client()
        with pytest.raises(AttioPermissionError):
            await client.objects.list()
        await client.close()
