"""HTTP transport layer for the Attio SDK.

Provides both synchronous and asynchronous transports with retry logic,
rate limit handling, and proper error mapping.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from attio._config import USER_AGENT, ClientConfig
from attio._exceptions import (
    AttioConnectionError,
    AttioTimeoutError,
    _raise_for_status,
)
from attio._types import JsonDict


def _should_retry(status_code: int) -> bool:
    """Return True if the status code is retryable (429 or 5xx)."""
    return status_code == 429 or status_code >= 500


def _build_headers(api_key: str) -> dict[str, str]:
    """Build the default headers for API requests."""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }


class HttpTransport:
    """Synchronous HTTP transport wrapping httpx.Client."""

    def __init__(self, config: ClientConfig) -> None:
        self._config = config
        self._client = httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=_build_headers(config.api_key),
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> JsonDict:
        """Make an HTTP request with retry logic. Returns the parsed JSON response."""
        last_exception: Exception | None = None

        for attempt in range(self._config.max_retries + 1):
            try:
                response = self._client.request(
                    method,
                    path,
                    params=params,
                    json=json,
                )
            except httpx.TimeoutException as exc:
                raise AttioTimeoutError(
                    f"Request timed out: {method} {path}",
                    status_code=0,
                ) from exc
            except httpx.ConnectError as exc:
                last_exception = exc
                if attempt < self._config.max_retries:
                    delay = self._config.retry_delay * (2**attempt)
                    time.sleep(delay)
                    continue
                raise AttioConnectionError(
                    f"Connection error: {exc}",
                    status_code=0,
                ) from exc

            # Handle retryable status codes
            if _should_retry(response.status_code) and attempt < self._config.max_retries:
                if response.status_code == 429:
                    retry_after_header = response.headers.get("retry-after")
                    delay = float(retry_after_header) if retry_after_header else self._config.retry_delay
                else:
                    delay = self._config.retry_delay * (2**attempt)
                time.sleep(delay)
                continue

            # Raise for non-2xx (non-retryable or retries exhausted)
            _raise_for_status(response)

            result: JsonDict = response.json()
            return result

        # Should not be reached, but just in case
        if last_exception is not None:
            raise AttioConnectionError(
                f"Request failed after {self._config.max_retries} retries: {last_exception}",
                status_code=0,
            ) from last_exception
        raise AttioConnectionError(
            f"Request failed after {self._config.max_retries} retries",
            status_code=0,
        )

    def request_multipart(
        self,
        method: str,
        path: str,
        *,
        data: dict[str, Any] | None = None,
        files: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> JsonDict:
        """Make a multipart form data request with retry logic."""
        last_exception: Exception | None = None

        # Build headers without Content-Type (httpx sets it for multipart)
        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "User-Agent": USER_AGENT,
        }

        for attempt in range(self._config.max_retries + 1):
            try:
                response = self._client.request(
                    method,
                    path,
                    data=data,
                    files=files,
                    params=params,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                raise AttioTimeoutError(
                    f"Request timed out: {method} {path}",
                    status_code=0,
                ) from exc
            except httpx.ConnectError as exc:
                last_exception = exc
                if attempt < self._config.max_retries:
                    delay = self._config.retry_delay * (2**attempt)
                    time.sleep(delay)
                    continue
                raise AttioConnectionError(
                    f"Connection error: {exc}",
                    status_code=0,
                ) from exc

            if _should_retry(response.status_code) and attempt < self._config.max_retries:
                if response.status_code == 429:
                    retry_after_header = response.headers.get("retry-after")
                    delay = float(retry_after_header) if retry_after_header else self._config.retry_delay
                else:
                    delay = self._config.retry_delay * (2**attempt)
                time.sleep(delay)
                continue

            _raise_for_status(response)
            result: JsonDict = response.json()
            return result

        if last_exception is not None:
            raise AttioConnectionError(
                f"Request failed after {self._config.max_retries} retries: {last_exception}",
                status_code=0,
            ) from last_exception
        raise AttioConnectionError(
            f"Request failed after {self._config.max_retries} retries",
            status_code=0,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> HttpTransport:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncHttpTransport:
    """Asynchronous HTTP transport wrapping httpx.AsyncClient."""

    def __init__(self, config: ClientConfig) -> None:
        self._config = config
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=_build_headers(config.api_key),
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> JsonDict:
        """Make an async HTTP request with retry logic. Returns the parsed JSON response."""
        last_exception: Exception | None = None

        for attempt in range(self._config.max_retries + 1):
            try:
                response = await self._client.request(
                    method,
                    path,
                    params=params,
                    json=json,
                )
            except httpx.TimeoutException as exc:
                raise AttioTimeoutError(
                    f"Request timed out: {method} {path}",
                    status_code=0,
                ) from exc
            except httpx.ConnectError as exc:
                last_exception = exc
                if attempt < self._config.max_retries:
                    delay = self._config.retry_delay * (2**attempt)
                    await asyncio.sleep(delay)
                    continue
                raise AttioConnectionError(
                    f"Connection error: {exc}",
                    status_code=0,
                ) from exc

            if _should_retry(response.status_code) and attempt < self._config.max_retries:
                if response.status_code == 429:
                    retry_after_header = response.headers.get("retry-after")
                    delay = float(retry_after_header) if retry_after_header else self._config.retry_delay
                else:
                    delay = self._config.retry_delay * (2**attempt)
                await asyncio.sleep(delay)
                continue

            _raise_for_status(response)
            result: JsonDict = response.json()
            return result

        if last_exception is not None:
            raise AttioConnectionError(
                f"Request failed after {self._config.max_retries} retries: {last_exception}",
                status_code=0,
            ) from last_exception
        raise AttioConnectionError(
            f"Request failed after {self._config.max_retries} retries",
            status_code=0,
        )

    async def request_multipart(
        self,
        method: str,
        path: str,
        *,
        data: dict[str, Any] | None = None,
        files: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> JsonDict:
        """Make an async multipart form data request with retry logic."""
        last_exception: Exception | None = None

        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "User-Agent": USER_AGENT,
        }

        for attempt in range(self._config.max_retries + 1):
            try:
                response = await self._client.request(
                    method,
                    path,
                    data=data,
                    files=files,
                    params=params,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                raise AttioTimeoutError(
                    f"Request timed out: {method} {path}",
                    status_code=0,
                ) from exc
            except httpx.ConnectError as exc:
                last_exception = exc
                if attempt < self._config.max_retries:
                    delay = self._config.retry_delay * (2**attempt)
                    await asyncio.sleep(delay)
                    continue
                raise AttioConnectionError(
                    f"Connection error: {exc}",
                    status_code=0,
                ) from exc

            if _should_retry(response.status_code) and attempt < self._config.max_retries:
                if response.status_code == 429:
                    retry_after_header = response.headers.get("retry-after")
                    delay = float(retry_after_header) if retry_after_header else self._config.retry_delay
                else:
                    delay = self._config.retry_delay * (2**attempt)
                await asyncio.sleep(delay)
                continue

            _raise_for_status(response)
            result: JsonDict = response.json()
            return result

        if last_exception is not None:
            raise AttioConnectionError(
                f"Request failed after {self._config.max_retries} retries: {last_exception}",
                status_code=0,
            ) from last_exception
        raise AttioConnectionError(
            f"Request failed after {self._config.max_retries} retries",
            status_code=0,
        )

    async def close(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncHttpTransport:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
