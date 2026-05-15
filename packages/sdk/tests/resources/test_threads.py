"""Tests for the Threads resource (sync and async)."""

from __future__ import annotations

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio.models._base import ListResponse
from attio.models.threads import Thread

from tests.fixtures.factory import (
    MOCK_THREADS_LIST,
    MOCK_THREAD_SINGLE,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_threads"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestThreadsResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/threads").mock(
            return_value=httpx.Response(200, json=MOCK_THREADS_LIST)
        )
        client = _sync_client()
        result = client.threads.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Thread)
        assert result.data[0].id.thread_id == "thread_01abc123def456"
        assert len(result.data[0].comments) == 2
        assert result.data[1].id.thread_id == "thread_02xyz789ghi012"
        assert len(result.data[1].comments) == 0
        client.close()

    @respx.mock
    def test_list_with_query_params(self) -> None:
        route = respx.get(f"{BASE_URL}/threads").mock(
            return_value=httpx.Response(200, json=MOCK_THREADS_LIST)
        )
        client = _sync_client()
        result = client.threads.list(
            record_id="rec_01abc123def456",
            object="people",
            limit=10,
            offset=0,
        )

        assert route.called
        assert isinstance(result, ListResponse)

        # Verify query params were sent
        request = route.calls[0].request
        assert "record_id=rec_01abc123def456" in str(request.url)
        assert "object=people" in str(request.url)
        assert "limit=10" in str(request.url)
        assert "offset=0" in str(request.url)
        client.close()

    @respx.mock
    def test_list_with_entry_params(self) -> None:
        route = respx.get(f"{BASE_URL}/threads").mock(
            return_value=httpx.Response(200, json=MOCK_THREADS_LIST)
        )
        client = _sync_client()
        client.threads.list(
            entry_id="entry_01abc123def456",
            list="sales_pipeline",
        )

        assert route.called
        request = route.calls[0].request
        assert "entry_id=entry_01abc123def456" in str(request.url)
        assert "list=sales_pipeline" in str(request.url)
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/threads/thread_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_THREAD_SINGLE)
        )
        client = _sync_client()
        result = client.threads.get("thread_01abc123def456")

        assert route.called
        assert isinstance(result, Thread)
        assert result.id.thread_id == "thread_01abc123def456"
        assert result.id.workspace_id == "ws_01abc123def456"
        assert len(result.comments) == 2
        assert result.comments[0].content_plaintext == "This looks great, let's proceed."
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestThreadsResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/threads").mock(
            return_value=httpx.Response(200, json=MOCK_THREADS_LIST)
        )
        client = _async_client()
        result = await client.threads.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Thread)
        await client.close()

    @respx.mock
    async def test_list_with_query_params(self) -> None:
        route = respx.get(f"{BASE_URL}/threads").mock(
            return_value=httpx.Response(200, json=MOCK_THREADS_LIST)
        )
        client = _async_client()
        result = await client.threads.list(
            record_id="rec_01abc123def456",
            object="people",
            limit=10,
            offset=0,
        )

        assert route.called
        assert isinstance(result, ListResponse)
        request = route.calls[0].request
        assert "record_id=rec_01abc123def456" in str(request.url)
        assert "object=people" in str(request.url)
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/threads/thread_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_THREAD_SINGLE)
        )
        client = _async_client()
        result = await client.threads.get("thread_01abc123def456")

        assert route.called
        assert isinstance(result, Thread)
        assert result.id.thread_id == "thread_01abc123def456"
        assert len(result.comments) == 2
        await client.close()
