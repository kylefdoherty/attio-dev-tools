"""Tests for _http.py — HTTP transport with retry logic and error mapping."""

from __future__ import annotations

import httpx
import pytest
import respx

from attio._config import ClientConfig
from attio._exceptions import (
    AttioAPIError,
    AttioConnectionError,
    AttioPermissionError,
    AttioTimeoutError,
    AttioValidationError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
)
from attio._http import AsyncHttpTransport, HttpTransport

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_abc"


def _config(max_retries: int = 3, retry_delay: float = 0.0, timeout: float = 5.0) -> ClientConfig:
    return ClientConfig(
        api_key=TEST_KEY,
        base_url=BASE_URL,
        max_retries=max_retries,
        retry_delay=retry_delay,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Sync transport tests
# ---------------------------------------------------------------------------


class TestHttpTransportAuthHeader:
    @respx.mock
    def test_auth_header_is_present(self) -> None:
        route = respx.get(f"{BASE_URL}/objects").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        transport = HttpTransport(_config())
        transport.request("GET", "/objects")
        assert route.called
        request = route.calls[0].request
        assert request.headers["authorization"] == f"Bearer {TEST_KEY}"
        assert "attio-python" in request.headers["user-agent"]
        transport.close()


class TestHttpTransportRetry429:
    @respx.mock
    def test_retry_on_429_then_success(self) -> None:
        route = respx.get(f"{BASE_URL}/objects").mock(
            side_effect=[
                httpx.Response(429, json={"message": "rate limited"}, headers={"retry-after": "0"}),
                httpx.Response(200, json={"data": []}),
            ]
        )
        transport = HttpTransport(_config())
        result = transport.request("GET", "/objects")
        assert route.call_count == 2
        assert result == {"data": []}
        transport.close()

    @respx.mock
    def test_429_exhaustion_raises_rate_limit_error(self) -> None:
        respx.get(f"{BASE_URL}/objects").mock(
            return_value=httpx.Response(429, json={"message": "rate limited"}, headers={"retry-after": "0"})
        )
        transport = HttpTransport(_config(max_retries=2))
        with pytest.raises(RateLimitError) as exc_info:
            transport.request("GET", "/objects")
        assert exc_info.value.status_code == 429
        transport.close()


class TestHttpTransport5xxRetry:
    @respx.mock
    def test_retry_on_500_then_success(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            side_effect=[
                httpx.Response(500, json={"message": "server error"}),
                httpx.Response(200, json={"data": "ok"}),
            ]
        )
        transport = HttpTransport(_config())
        result = transport.request("GET", "/test")
        assert route.call_count == 2
        assert result == {"data": "ok"}
        transport.close()

    @respx.mock
    def test_5xx_exhaustion_raises_api_error(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(502, json={"message": "bad gateway"})
        )
        transport = HttpTransport(_config(max_retries=1))
        with pytest.raises(AttioAPIError) as exc_info:
            transport.request("GET", "/test")
        assert exc_info.value.status_code == 502
        transport.close()


class TestHttpTransportNetworkError:
    @respx.mock
    def test_retry_on_network_error_then_success(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            side_effect=[
                httpx.ConnectError("Connection refused"),
                httpx.Response(200, json={"data": "ok"}),
            ]
        )
        transport = HttpTransport(_config())
        result = transport.request("GET", "/test")
        assert route.call_count == 2
        assert result == {"data": "ok"}
        transport.close()

    @respx.mock
    def test_network_error_exhaustion_raises_connection_error(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(side_effect=httpx.ConnectError("Connection refused"))
        transport = HttpTransport(_config(max_retries=1))
        with pytest.raises(AttioConnectionError):
            transport.request("GET", "/test")
        transport.close()


class TestHttpTransportTimeout:
    @respx.mock
    def test_timeout_raises_immediately(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(side_effect=httpx.ReadTimeout("Read timed out"))
        transport = HttpTransport(_config(max_retries=3))
        with pytest.raises(AttioTimeoutError):
            transport.request("GET", "/test")
        transport.close()


class TestHttpTransport4xxNoRetry:
    @respx.mock
    def test_400_no_retry(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(400, json={"message": "bad request", "code": "validation_type"})
        )
        transport = HttpTransport(_config())
        with pytest.raises(AttioValidationError):
            transport.request("GET", "/test")
        assert route.call_count == 1
        transport.close()

    @respx.mock
    def test_401_raises_authentication_error(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(401, json={"message": "unauthorized"})
        )
        transport = HttpTransport(_config())
        with pytest.raises(AuthenticationError):
            transport.request("GET", "/test")
        assert route.call_count == 1
        transport.close()

    @respx.mock
    def test_403_raises_permission_error(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(403, json={"message": "forbidden"})
        )
        transport = HttpTransport(_config())
        with pytest.raises(AttioPermissionError):
            transport.request("GET", "/test")
        assert route.call_count == 1
        transport.close()

    @respx.mock
    def test_404_raises_not_found_error(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(404, json={"message": "not found"})
        )
        transport = HttpTransport(_config())
        with pytest.raises(NotFoundError):
            transport.request("GET", "/test")
        assert route.call_count == 1
        transport.close()

    @respx.mock
    def test_409_raises_conflict_error(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(409, json={"message": "conflict"})
        )
        transport = HttpTransport(_config())
        with pytest.raises(ConflictError):
            transport.request("GET", "/test")
        assert route.call_count == 1
        transport.close()


class TestHttpTransportContextManager:
    @respx.mock
    def test_context_manager(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(return_value=httpx.Response(200, json={"ok": True}))
        with HttpTransport(_config()) as transport:
            result = transport.request("GET", "/test")
            assert result == {"ok": True}


# ---------------------------------------------------------------------------
# Async transport tests
# ---------------------------------------------------------------------------


class TestAsyncHttpTransportAuthHeader:
    @respx.mock
    async def test_auth_header_is_present(self) -> None:
        route = respx.get(f"{BASE_URL}/objects").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        transport = AsyncHttpTransport(_config())
        await transport.request("GET", "/objects")
        assert route.called
        request = route.calls[0].request
        assert request.headers["authorization"] == f"Bearer {TEST_KEY}"
        await transport.close()


class TestAsyncHttpTransportRetry429:
    @respx.mock
    async def test_retry_on_429_then_success(self) -> None:
        route = respx.get(f"{BASE_URL}/objects").mock(
            side_effect=[
                httpx.Response(429, json={"message": "rate limited"}, headers={"retry-after": "0"}),
                httpx.Response(200, json={"data": []}),
            ]
        )
        transport = AsyncHttpTransport(_config())
        result = await transport.request("GET", "/objects")
        assert route.call_count == 2
        assert result == {"data": []}
        await transport.close()

    @respx.mock
    async def test_429_exhaustion_raises_rate_limit_error(self) -> None:
        respx.get(f"{BASE_URL}/objects").mock(
            return_value=httpx.Response(429, json={"message": "rate limited"}, headers={"retry-after": "0"})
        )
        transport = AsyncHttpTransport(_config(max_retries=2))
        with pytest.raises(RateLimitError):
            await transport.request("GET", "/objects")
        await transport.close()


class TestAsyncHttpTransport5xxRetry:
    @respx.mock
    async def test_retry_on_500_then_success(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            side_effect=[
                httpx.Response(500, json={"message": "server error"}),
                httpx.Response(200, json={"data": "ok"}),
            ]
        )
        transport = AsyncHttpTransport(_config())
        result = await transport.request("GET", "/test")
        assert route.call_count == 2
        assert result == {"data": "ok"}
        await transport.close()


class TestAsyncHttpTransportNetworkError:
    @respx.mock
    async def test_retry_on_network_error_then_success(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            side_effect=[
                httpx.ConnectError("Connection refused"),
                httpx.Response(200, json={"data": "ok"}),
            ]
        )
        transport = AsyncHttpTransport(_config())
        result = await transport.request("GET", "/test")
        assert route.call_count == 2
        assert result == {"data": "ok"}
        await transport.close()

    @respx.mock
    async def test_network_error_exhaustion(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(side_effect=httpx.ConnectError("Connection refused"))
        transport = AsyncHttpTransport(_config(max_retries=1))
        with pytest.raises(AttioConnectionError):
            await transport.request("GET", "/test")
        await transport.close()


class TestAsyncHttpTransportTimeout:
    @respx.mock
    async def test_timeout_raises_immediately(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(side_effect=httpx.ReadTimeout("Read timed out"))
        transport = AsyncHttpTransport(_config(max_retries=3))
        with pytest.raises(AttioTimeoutError):
            await transport.request("GET", "/test")
        await transport.close()


class TestAsyncHttpTransport4xxNoRetry:
    @respx.mock
    async def test_400_no_retry(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(400, json={"message": "bad request"})
        )
        transport = AsyncHttpTransport(_config())
        with pytest.raises(AttioValidationError):
            await transport.request("GET", "/test")
        assert route.call_count == 1
        await transport.close()


class TestAsyncHttpTransportContextManager:
    @respx.mock
    async def test_async_context_manager(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(return_value=httpx.Response(200, json={"ok": True}))
        async with AsyncHttpTransport(_config()) as transport:
            result = await transport.request("GET", "/test")
            assert result == {"ok": True}
