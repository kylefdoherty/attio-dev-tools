"""Tests for the Meetings resource (sync and async)."""

from __future__ import annotations

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import NotFoundError
from attio.models._base import PaginatedResponse
from attio.models.meetings import Meeting
from tests.fixtures.factory import (
    MOCK_MEETING_SINGLE,
    MOCK_MEETINGS_LIST,
    MOCK_NOT_FOUND_ERROR,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_meetings"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestMeetingsResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/meetings").mock(
            return_value=httpx.Response(200, json=MOCK_MEETINGS_LIST)
        )
        client = _sync_client()
        result = client.meetings.list()

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Meeting)
        assert result.data[0].title == "Q3 Planning"
        assert result.data[0].id.meeting_id == "mtg_01abc123def456"
        assert len(result.data[0].participants) == 2
        assert result.data[0].participants[0].email_address == "jane@example.com"
        assert result.pagination.next_cursor is None
        client.close()

    @respx.mock
    def test_list_with_query_params(self) -> None:
        route = respx.get(f"{BASE_URL}/meetings").mock(
            return_value=httpx.Response(200, json=MOCK_MEETINGS_LIST)
        )
        client = _sync_client()
        client.meetings.list(
            limit=10,
            linked_object="companies",
            linked_record_id="rec_01abc",
            participants=["jane@example.com", "john@example.com"],
            sort="start_time",
            ends_from="2024-04-01T00:00:00Z",
            starts_before="2024-04-30T23:59:59Z",
            timezone="America/New_York",
        )

        assert route.called
        request = route.calls[0].request
        url_str = str(request.url)
        assert "limit=10" in url_str
        assert "linked_object=companies" in url_str
        assert "linked_record_id=rec_01abc" in url_str
        # participants should be comma-separated
        assert "participants=jane%40example.com%2Cjohn%40example.com" in url_str
        assert "sort=start_time" in url_str
        client.close()

    @respx.mock
    def test_list_with_participants_string(self) -> None:
        route = respx.get(f"{BASE_URL}/meetings").mock(
            return_value=httpx.Response(200, json=MOCK_MEETINGS_LIST)
        )
        client = _sync_client()
        client.meetings.list(participants="jane@example.com")

        assert route.called
        request = route.calls[0].request
        assert "participants=jane%40example.com" in str(request.url)
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/meetings/mtg_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_MEETING_SINGLE)
        )
        client = _sync_client()
        result = client.meetings.get("mtg_01abc123def456")

        assert route.called
        assert isinstance(result, Meeting)
        assert result.title == "Q3 Planning"
        assert result.description == "Quarterly planning session"
        assert len(result.linked_records) == 1
        client.close()

    @respx.mock
    def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/meetings/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.meetings.get("nonexistent")
        assert exc_info.value.status_code == 404
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestMeetingsResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/meetings").mock(
            return_value=httpx.Response(200, json=MOCK_MEETINGS_LIST)
        )
        client = _async_client()
        result = await client.meetings.list()

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Meeting)
        assert result.data[0].title == "Q3 Planning"
        await client.close()

    @respx.mock
    async def test_list_with_query_params(self) -> None:
        route = respx.get(f"{BASE_URL}/meetings").mock(
            return_value=httpx.Response(200, json=MOCK_MEETINGS_LIST)
        )
        client = _async_client()
        await client.meetings.list(
            limit=5,
            linked_object="deals",
            participants=["a@b.com"],
        )

        assert route.called
        request = route.calls[0].request
        url_str = str(request.url)
        assert "limit=5" in url_str
        assert "linked_object=deals" in url_str
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/meetings/mtg_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_MEETING_SINGLE)
        )
        client = _async_client()
        result = await client.meetings.get("mtg_01abc123def456")

        assert route.called
        assert isinstance(result, Meeting)
        assert result.title == "Q3 Planning"
        await client.close()

    @respx.mock
    async def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/meetings/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.meetings.get("nonexistent")
        await client.close()
