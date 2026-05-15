"""Tests for the Call Recordings resource (sync and async)."""

from __future__ import annotations

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import NotFoundError
from attio.models._base import PaginatedResponse
from attio.models.call_recordings import CallRecording
from tests.fixtures.factory import (
    MOCK_CALL_RECORDING_SINGLE,
    MOCK_CALL_RECORDINGS_LIST,
    MOCK_NOT_FOUND_ERROR,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_call_recordings"
MEETING_ID = "mtg_01abc123def456"
RECORDING_ID = "cr_01abc123def456"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestCallRecordingsResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(
            f"{BASE_URL}/meetings/{MEETING_ID}/call_recordings"
        ).mock(return_value=httpx.Response(200, json=MOCK_CALL_RECORDINGS_LIST))
        client = _sync_client()
        result = client.call_recordings.list(MEETING_ID)

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], CallRecording)
        assert result.data[0].id.call_recording_id == "cr_01abc123def456"
        assert result.data[0].status == "completed"
        assert result.data[0].meeting_id == MEETING_ID
        assert result.data[1].status == "processing"
        assert result.pagination.next_cursor is None
        client.close()

    @respx.mock
    def test_list_with_params(self) -> None:
        route = respx.get(
            f"{BASE_URL}/meetings/{MEETING_ID}/call_recordings"
        ).mock(return_value=httpx.Response(200, json=MOCK_CALL_RECORDINGS_LIST))
        client = _sync_client()
        client.call_recordings.list(MEETING_ID, limit=5, cursor="cursor_abc")

        assert route.called
        request = route.calls[0].request
        url_str = str(request.url)
        assert "limit=5" in url_str
        assert "cursor=cursor_abc" in url_str
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(
            f"{BASE_URL}/meetings/{MEETING_ID}/call_recordings/{RECORDING_ID}"
        ).mock(return_value=httpx.Response(200, json=MOCK_CALL_RECORDING_SINGLE))
        client = _sync_client()
        result = client.call_recordings.get(MEETING_ID, RECORDING_ID)

        assert route.called
        assert isinstance(result, CallRecording)
        assert result.id.call_recording_id == RECORDING_ID
        assert result.status == "completed"
        assert result.web_url is not None
        client.close()

    @respx.mock
    def test_get_not_found(self) -> None:
        respx.get(
            f"{BASE_URL}/meetings/{MEETING_ID}/call_recordings/nonexistent"
        ).mock(return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR))
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.call_recordings.get(MEETING_ID, "nonexistent")
        assert exc_info.value.status_code == 404
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestCallRecordingsResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(
            f"{BASE_URL}/meetings/{MEETING_ID}/call_recordings"
        ).mock(return_value=httpx.Response(200, json=MOCK_CALL_RECORDINGS_LIST))
        client = _async_client()
        result = await client.call_recordings.list(MEETING_ID)

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], CallRecording)
        assert result.data[0].status == "completed"
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(
            f"{BASE_URL}/meetings/{MEETING_ID}/call_recordings/{RECORDING_ID}"
        ).mock(return_value=httpx.Response(200, json=MOCK_CALL_RECORDING_SINGLE))
        client = _async_client()
        result = await client.call_recordings.get(MEETING_ID, RECORDING_ID)

        assert route.called
        assert isinstance(result, CallRecording)
        assert result.id.call_recording_id == RECORDING_ID
        await client.close()

    @respx.mock
    async def test_get_not_found(self) -> None:
        respx.get(
            f"{BASE_URL}/meetings/{MEETING_ID}/call_recordings/nonexistent"
        ).mock(return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR))
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.call_recordings.get(MEETING_ID, "nonexistent")
        await client.close()
