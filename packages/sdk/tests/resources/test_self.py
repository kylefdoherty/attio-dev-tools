"""Tests for the Self resource (sync and async)."""

from __future__ import annotations

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import AuthenticationError
from attio.models.self_info import SelfInfo
from tests.fixtures.factory import MOCK_SELF_INFO

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_self"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestSelfResourceSync:
    @respx.mock
    def test_identify(self) -> None:
        route = respx.get(f"{BASE_URL}/self").mock(
            return_value=httpx.Response(200, json=MOCK_SELF_INFO)
        )
        client = _sync_client()
        result = client.self_.identify()

        assert route.called
        assert isinstance(result, SelfInfo)
        assert result.active is True
        assert result.workspace_id == "ws_01abc123def456"
        assert result.workspace_name == "Test Workspace"
        assert result.workspace_slug == "test-workspace"
        assert result.scope == "object_configuration:read record_permission:read"
        assert result.token_type == "Bearer"
        assert result.iss == "attio.com"
        client.close()

    @respx.mock
    def test_identify_auth_error(self) -> None:
        respx.get(f"{BASE_URL}/self").mock(
            return_value=httpx.Response(
                401,
                json={
                    "status_code": 401,
                    "type": "invalid_request_error",
                    "code": "unauthorized",
                    "message": "Invalid API key.",
                },
            )
        )
        client = _sync_client()
        with pytest.raises(AuthenticationError) as exc_info:
            client.self_.identify()
        assert exc_info.value.status_code == 401
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestSelfResourceAsync:
    @respx.mock
    async def test_identify(self) -> None:
        route = respx.get(f"{BASE_URL}/self").mock(
            return_value=httpx.Response(200, json=MOCK_SELF_INFO)
        )
        client = _async_client()
        result = await client.self_.identify()

        assert route.called
        assert isinstance(result, SelfInfo)
        assert result.active is True
        assert result.workspace_id == "ws_01abc123def456"
        assert result.workspace_name == "Test Workspace"
        await client.close()

    @respx.mock
    async def test_identify_auth_error(self) -> None:
        respx.get(f"{BASE_URL}/self").mock(
            return_value=httpx.Response(
                401,
                json={
                    "status_code": 401,
                    "type": "invalid_request_error",
                    "code": "unauthorized",
                    "message": "Invalid API key.",
                },
            )
        )
        client = _async_client()
        with pytest.raises(AuthenticationError):
            await client.self_.identify()
        await client.close()
