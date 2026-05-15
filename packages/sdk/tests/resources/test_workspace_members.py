"""Tests for the Workspace Members resource (sync and async)."""

from __future__ import annotations

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import AttioPermissionError, NotFoundError
from attio.models._base import ListResponse
from attio.models.workspace_members import WorkspaceMember

from tests.fixtures.factory import (
    MOCK_NOT_FOUND_ERROR,
    MOCK_PERMISSION_ERROR,
    MOCK_WORKSPACE_MEMBER_SINGLE,
    MOCK_WORKSPACE_MEMBERS_LIST,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_workspace_members"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestWorkspaceMembersResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/workspace_members").mock(
            return_value=httpx.Response(200, json=MOCK_WORKSPACE_MEMBERS_LIST)
        )
        client = _sync_client()
        result = client.workspace_members.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], WorkspaceMember)
        assert result.data[0].first_name == "Jane"
        assert result.data[0].last_name == "Doe"
        assert result.data[0].email_address == "jane.doe@example.com"
        assert result.data[0].id.workspace_member_id == "wm_01abc123def456"
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/workspace_members/wm_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_WORKSPACE_MEMBER_SINGLE)
        )
        client = _sync_client()
        result = client.workspace_members.get("wm_01abc123def456")

        assert route.called
        assert isinstance(result, WorkspaceMember)
        assert result.first_name == "Jane"
        assert result.access_level == "admin"
        assert result.avatar_url == "https://example.com/avatar/jane.png"
        client.close()

    @respx.mock
    def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/workspace_members/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.workspace_members.get("nonexistent")
        assert exc_info.value.status_code == 404
        client.close()

    @respx.mock
    def test_list_permission_error(self) -> None:
        respx.get(f"{BASE_URL}/workspace_members").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _sync_client()
        with pytest.raises(AttioPermissionError) as exc_info:
            client.workspace_members.list()
        assert exc_info.value.status_code == 403
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestWorkspaceMembersResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/workspace_members").mock(
            return_value=httpx.Response(200, json=MOCK_WORKSPACE_MEMBERS_LIST)
        )
        client = _async_client()
        result = await client.workspace_members.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], WorkspaceMember)
        assert result.data[0].first_name == "Jane"
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/workspace_members/wm_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_WORKSPACE_MEMBER_SINGLE)
        )
        client = _async_client()
        result = await client.workspace_members.get("wm_01abc123def456")

        assert route.called
        assert isinstance(result, WorkspaceMember)
        assert result.first_name == "Jane"
        assert result.access_level == "admin"
        await client.close()

    @respx.mock
    async def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/workspace_members/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.workspace_members.get("nonexistent")
        await client.close()

    @respx.mock
    async def test_list_permission_error(self) -> None:
        respx.get(f"{BASE_URL}/workspace_members").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _async_client()
        with pytest.raises(AttioPermissionError):
            await client.workspace_members.list()
        await client.close()
