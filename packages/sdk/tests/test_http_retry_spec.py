"""Cross-SDK HTTP retry spec validation tests.

These tests validate that the Python SDK conforms to docs/http-retry-spec.md.
The Node SDK has a mirror test suite in packages/node-sdk/tests/http-retry-spec.test.ts.
Both suites MUST cover the same scenarios.
"""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest
import respx

from attio._config import ClientConfig
from attio._exceptions import (
    AttioAPIError,
    AttioConnectionError,
    AttioTimeoutError,
    RateLimitError,
)
from attio._http import AsyncHttpTransport, HttpTransport

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_spec"


def _config(
    max_retries: int = 3,
    retry_delay: float = 0.01,
    timeout: float = 5.0,
) -> ClientConfig:
    return ClientConfig(
        api_key=TEST_KEY,
        base_url=BASE_URL,
        max_retries=max_retries,
        retry_delay=retry_delay,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Spec scenario 1: retry_on_429_then_success
# ---------------------------------------------------------------------------


class TestSpec429RetryThenSuccess:
    """First request returns 429 with Retry-After: 0, second returns 200."""

    @respx.mock
    def test_sync(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            side_effect=[
                httpx.Response(429, json={"message": "rate limited"}, headers={"retry-after": "0"}),
                httpx.Response(200, json={"data": "ok"}),
            ]
        )
        transport = HttpTransport(_config())
        result = transport.request("GET", "/test")
        assert route.call_count == 2
        assert result == {"data": "ok"}
        transport.close()

    @respx.mock
    async def test_async(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            side_effect=[
                httpx.Response(429, json={"message": "rate limited"}, headers={"retry-after": "0"}),
                httpx.Response(200, json={"data": "ok"}),
            ]
        )
        transport = AsyncHttpTransport(_config())
        result = await transport.request("GET", "/test")
        assert route.call_count == 2
        assert result == {"data": "ok"}
        await transport.close()


# ---------------------------------------------------------------------------
# Spec scenario 2: retry_on_5xx_then_success
# ---------------------------------------------------------------------------


class TestSpec5xxRetryThenSuccess:
    """First request returns 500, second returns 200."""

    @respx.mock
    def test_sync(self) -> None:
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
    async def test_async(self) -> None:
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


# ---------------------------------------------------------------------------
# Spec scenario 3: retry_on_network_error_then_success
# ---------------------------------------------------------------------------


class TestSpecNetworkErrorRetryThenSuccess:
    """First request raises connection error, second returns 200."""

    @respx.mock
    def test_sync(self) -> None:
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
    async def test_async(self) -> None:
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


# ---------------------------------------------------------------------------
# Spec scenario 4: 429_exhaustion_raises_rate_limit_error
# ---------------------------------------------------------------------------


class TestSpec429Exhaustion:
    """All attempts return 429. RateLimitError is raised."""

    @respx.mock
    def test_sync(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(
                429, json={"message": "rate limited"}, headers={"retry-after": "0"}
            )
        )
        transport = HttpTransport(_config(max_retries=2))
        with pytest.raises(RateLimitError) as exc_info:
            transport.request("GET", "/test")
        assert exc_info.value.status_code == 429
        transport.close()

    @respx.mock
    async def test_async(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(
                429, json={"message": "rate limited"}, headers={"retry-after": "0"}
            )
        )
        transport = AsyncHttpTransport(_config(max_retries=2))
        with pytest.raises(RateLimitError) as exc_info:
            await transport.request("GET", "/test")
        assert exc_info.value.status_code == 429
        await transport.close()


# ---------------------------------------------------------------------------
# Spec scenario 5: 5xx_exhaustion_raises_api_error
# ---------------------------------------------------------------------------


class TestSpec5xxExhaustion:
    """All attempts return 502. API error with status 502 is raised."""

    @respx.mock
    def test_sync(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(502, json={"message": "bad gateway"})
        )
        transport = HttpTransport(_config(max_retries=1))
        with pytest.raises(AttioAPIError) as exc_info:
            transport.request("GET", "/test")
        assert exc_info.value.status_code == 502
        assert route.call_count == 2  # initial + 1 retry
        transport.close()

    @respx.mock
    async def test_async(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(502, json={"message": "bad gateway"})
        )
        transport = AsyncHttpTransport(_config(max_retries=1))
        with pytest.raises(AttioAPIError) as exc_info:
            await transport.request("GET", "/test")
        assert exc_info.value.status_code == 502
        assert route.call_count == 2  # initial + 1 retry
        await transport.close()


# ---------------------------------------------------------------------------
# Spec scenario 6: network_error_exhaustion
# ---------------------------------------------------------------------------


class TestSpecNetworkErrorExhaustion:
    """All attempts raise connection errors. ConnectionError is raised."""

    @respx.mock
    def test_sync(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        transport = HttpTransport(_config(max_retries=1))
        with pytest.raises(AttioConnectionError):
            transport.request("GET", "/test")
        assert route.call_count == 2  # initial + 1 retry
        transport.close()

    @respx.mock
    async def test_async(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        transport = AsyncHttpTransport(_config(max_retries=1))
        with pytest.raises(AttioConnectionError):
            await transport.request("GET", "/test")
        assert route.call_count == 2  # initial + 1 retry
        await transport.close()


# ---------------------------------------------------------------------------
# Spec scenario 7: 4xx_no_retry
# ---------------------------------------------------------------------------


class TestSpec4xxNoRetry:
    """Request returns 400. Exactly 1 attempt, validation error raised."""

    @respx.mock
    def test_sync(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(400, json={"message": "bad request", "code": "validation_type"})
        )
        transport = HttpTransport(_config(max_retries=3))
        with pytest.raises(AttioAPIError):
            transport.request("GET", "/test")
        assert route.call_count == 1
        transport.close()

    @respx.mock
    async def test_async(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            return_value=httpx.Response(400, json={"message": "bad request", "code": "validation_type"})
        )
        transport = AsyncHttpTransport(_config(max_retries=3))
        with pytest.raises(AttioAPIError):
            await transport.request("GET", "/test")
        assert route.call_count == 1
        await transport.close()


# ---------------------------------------------------------------------------
# Spec scenario 8: timeout_no_retry
# ---------------------------------------------------------------------------


class TestSpecTimeoutNoRetry:
    """Request times out. No retry, timeout error raised."""

    @respx.mock
    def test_sync(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            side_effect=httpx.ReadTimeout("Read timed out")
        )
        transport = HttpTransport(_config(max_retries=3))
        with pytest.raises(AttioTimeoutError):
            transport.request("GET", "/test")
        assert route.call_count == 1
        transport.close()

    @respx.mock
    async def test_async(self) -> None:
        route = respx.get(f"{BASE_URL}/test").mock(
            side_effect=httpx.ReadTimeout("Read timed out")
        )
        transport = AsyncHttpTransport(_config(max_retries=3))
        with pytest.raises(AttioTimeoutError):
            await transport.request("GET", "/test")
        assert route.call_count == 1
        await transport.close()


# ---------------------------------------------------------------------------
# Spec scenario 9: retry_after_header_respected
# ---------------------------------------------------------------------------


class TestSpecRetryAfterHeaderRespected:
    """429 with Retry-After header -- verify the delay uses the header value."""

    @respx.mock
    def test_sync_uses_retry_after_header(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(
            side_effect=[
                httpx.Response(429, json={"message": "rate limited"}, headers={"retry-after": "0.05"}),
                httpx.Response(200, json={"data": "ok"}),
            ]
        )
        transport = HttpTransport(_config(retry_delay=999.0))

        with patch("attio._http.time.sleep") as mock_sleep:
            transport.request("GET", "/test")
            # Should use the header value (0.05), not the retry_delay (999.0)
            mock_sleep.assert_called_once()
            delay = mock_sleep.call_args[0][0]
            assert delay == pytest.approx(0.05, abs=0.01)
        transport.close()

    @respx.mock
    async def test_async_uses_retry_after_header(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(
            side_effect=[
                httpx.Response(429, json={"message": "rate limited"}, headers={"retry-after": "0.05"}),
                httpx.Response(200, json={"data": "ok"}),
            ]
        )
        transport = AsyncHttpTransport(_config(retry_delay=999.0))

        with patch("attio._http.asyncio.sleep") as mock_sleep:
            mock_sleep.return_value = None
            await transport.request("GET", "/test")
            mock_sleep.assert_called_once()
            delay = mock_sleep.call_args[0][0]
            assert delay == pytest.approx(0.05, abs=0.01)
        await transport.close()


# ---------------------------------------------------------------------------
# Spec scenario 10: 5xx_uses_exponential_backoff
# ---------------------------------------------------------------------------


class TestSpec5xxExponentialBackoff:
    """Verify delays follow retry_delay * 2^attempt for 5xx errors."""

    @respx.mock
    def test_sync_backoff_delays(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(
            side_effect=[
                httpx.Response(500, json={"message": "error"}),
                httpx.Response(500, json={"message": "error"}),
                httpx.Response(200, json={"data": "ok"}),
            ]
        )
        transport = HttpTransport(_config(retry_delay=0.1, max_retries=3))

        with patch("attio._http.time.sleep") as mock_sleep:
            transport.request("GET", "/test")
            assert mock_sleep.call_count == 2
            # attempt 0: delay = 0.1 * 2^0 = 0.1
            assert mock_sleep.call_args_list[0][0][0] == pytest.approx(0.1, abs=0.01)
            # attempt 1: delay = 0.1 * 2^1 = 0.2
            assert mock_sleep.call_args_list[1][0][0] == pytest.approx(0.2, abs=0.01)
        transport.close()

    @respx.mock
    async def test_async_backoff_delays(self) -> None:
        respx.get(f"{BASE_URL}/test").mock(
            side_effect=[
                httpx.Response(500, json={"message": "error"}),
                httpx.Response(500, json={"message": "error"}),
                httpx.Response(200, json={"data": "ok"}),
            ]
        )
        transport = AsyncHttpTransport(_config(retry_delay=0.1, max_retries=3))

        with patch("attio._http.asyncio.sleep") as mock_sleep:
            mock_sleep.return_value = None
            await transport.request("GET", "/test")
            assert mock_sleep.call_count == 2
            assert mock_sleep.call_args_list[0][0][0] == pytest.approx(0.1, abs=0.01)
            assert mock_sleep.call_args_list[1][0][0] == pytest.approx(0.2, abs=0.01)
        await transport.close()
