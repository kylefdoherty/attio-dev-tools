"""Tests for the Transcripts resource (sync and async)."""

from __future__ import annotations

import httpx
import respx

from attio import AsyncAttioClient, AttioClient
from attio.models._base import PaginatedResponse
from attio.models.transcripts import TranscriptSegment

from tests.fixtures.factory import MOCK_TRANSCRIPT_LIST

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_transcripts"
MEETING_ID = "mtg_01abc123def456"
RECORDING_ID = "cr_01abc123def456"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestTranscriptsResourceSync:
    @respx.mock
    def test_get(self) -> None:
        route = respx.get(
            f"{BASE_URL}/meetings/{MEETING_ID}/call_recordings/{RECORDING_ID}/transcript"
        ).mock(return_value=httpx.Response(200, json=MOCK_TRANSCRIPT_LIST))
        client = _sync_client()
        result = client.transcripts.get(MEETING_ID, RECORDING_ID)

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 3
        assert isinstance(result.data[0], TranscriptSegment)
        assert result.data[0].speech == "Let's start with the Q3 roadmap."
        assert result.data[0].start_time == 0.0
        assert result.data[0].end_time == 3.5
        assert result.data[0].speaker == "Jane Doe"
        assert result.data[2].speaker is None
        assert result.pagination.next_cursor is None
        client.close()

    @respx.mock
    def test_get_with_params(self) -> None:
        route = respx.get(
            f"{BASE_URL}/meetings/{MEETING_ID}/call_recordings/{RECORDING_ID}/transcript"
        ).mock(return_value=httpx.Response(200, json=MOCK_TRANSCRIPT_LIST))
        client = _sync_client()
        client.transcripts.get(MEETING_ID, RECORDING_ID, limit=10, cursor="cursor_abc")

        assert route.called
        request = route.calls[0].request
        url_str = str(request.url)
        assert "limit=10" in url_str
        assert "cursor=cursor_abc" in url_str
        client.close()

    @respx.mock
    def test_deeply_nested_url(self) -> None:
        """Verify the full nested URL path is constructed correctly."""
        route = respx.get(
            f"{BASE_URL}/meetings/mtg_xyz/call_recordings/cr_abc/transcript"
        ).mock(return_value=httpx.Response(200, json=MOCK_TRANSCRIPT_LIST))
        client = _sync_client()
        client.transcripts.get("mtg_xyz", "cr_abc")

        assert route.called
        request = route.calls[0].request
        assert "/meetings/mtg_xyz/call_recordings/cr_abc/transcript" in str(request.url)
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestTranscriptsResourceAsync:
    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(
            f"{BASE_URL}/meetings/{MEETING_ID}/call_recordings/{RECORDING_ID}/transcript"
        ).mock(return_value=httpx.Response(200, json=MOCK_TRANSCRIPT_LIST))
        client = _async_client()
        result = await client.transcripts.get(MEETING_ID, RECORDING_ID)

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 3
        assert isinstance(result.data[0], TranscriptSegment)
        assert result.data[0].speech == "Let's start with the Q3 roadmap."
        assert result.data[0].speaker == "Jane Doe"
        await client.close()

    @respx.mock
    async def test_get_with_params(self) -> None:
        route = respx.get(
            f"{BASE_URL}/meetings/{MEETING_ID}/call_recordings/{RECORDING_ID}/transcript"
        ).mock(return_value=httpx.Response(200, json=MOCK_TRANSCRIPT_LIST))
        client = _async_client()
        await client.transcripts.get(MEETING_ID, RECORDING_ID, limit=5, cursor="next_page")

        assert route.called
        request = route.calls[0].request
        url_str = str(request.url)
        assert "limit=5" in url_str
        assert "cursor=next_page" in url_str
        await client.close()
