"""Tests for the Notes resource (sync and async)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import NotFoundError
from attio.models._base import ListResponse
from attio.models.notes import Note
from tests.fixtures.factory import (
    MOCK_NOT_FOUND_ERROR,
    MOCK_NOTE,
    MOCK_NOTE_CREATED,
    MOCK_NOTE_DELETE,
    MOCK_NOTE_SINGLE,
    MOCK_NOTES_LIST,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_notes"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestNotesResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/notes").mock(
            return_value=httpx.Response(200, json=MOCK_NOTES_LIST)
        )
        client = _sync_client()
        result = client.notes.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Note)
        assert result.data[0].title == "Meeting notes"
        assert result.data[0].id.note_id == "note_01abc123def456"
        client.close()

    @respx.mock
    def test_list_with_filters(self) -> None:
        route = respx.get(f"{BASE_URL}/notes").mock(
            return_value=httpx.Response(200, json={"data": [MOCK_NOTE]})
        )
        client = _sync_client()
        result = client.notes.list(
            parent_object="people",
            parent_record_id="rec_01abc123def456",
            limit=10,
            offset=0,
        )

        assert route.called
        request = route.calls[0].request
        assert "parent_object=people" in str(request.url)
        assert "parent_record_id=rec_01abc123def456" in str(request.url)
        assert "limit=10" in str(request.url)
        assert "offset=0" in str(request.url)
        assert len(result.data) == 1
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/notes/note_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_NOTE_SINGLE)
        )
        client = _sync_client()
        result = client.notes.get("note_01abc123def456")

        assert route.called
        assert isinstance(result, Note)
        assert result.title == "Meeting notes"
        assert result.parent_object == "people"
        assert result.format == "plaintext"
        assert result.id.workspace_id == "ws_01abc123def456"
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/notes").mock(
            return_value=httpx.Response(200, json=MOCK_NOTE_CREATED)
        )
        client = _sync_client()
        result = client.notes.create(
            parent_object="deals",
            parent_record_id="rec_03new456abc789",
            title="New note",
            format="plaintext",
            content="Some content here.",
        )

        assert route.called
        assert isinstance(result, Note)
        assert result.title == "New note"
        assert result.parent_object == "deals"

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "parent_object": "deals",
                "parent_record_id": "rec_03new456abc789",
                "title": "New note",
                "format": "plaintext",
                "content": "Some content here.",
            }
        }
        client.close()

    @respx.mock
    def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/notes/note_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_NOTE_DELETE)
        )
        client = _sync_client()
        result = client.notes.delete("note_01abc123def456")

        assert route.called
        assert result is None
        client.close()

    @respx.mock
    def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/notes/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.notes.get("nonexistent")
        assert exc_info.value.status_code == 404
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestNotesResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/notes").mock(
            return_value=httpx.Response(200, json=MOCK_NOTES_LIST)
        )
        client = _async_client()
        result = await client.notes.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Note)
        assert result.data[0].title == "Meeting notes"
        await client.close()

    @respx.mock
    async def test_list_with_filters(self) -> None:
        route = respx.get(f"{BASE_URL}/notes").mock(
            return_value=httpx.Response(200, json={"data": [MOCK_NOTE]})
        )
        client = _async_client()
        result = await client.notes.list(
            parent_object="people",
            parent_record_id="rec_01abc123def456",
        )

        assert route.called
        request = route.calls[0].request
        assert "parent_object=people" in str(request.url)
        assert "parent_record_id=rec_01abc123def456" in str(request.url)
        assert len(result.data) == 1
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/notes/note_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_NOTE_SINGLE)
        )
        client = _async_client()
        result = await client.notes.get("note_01abc123def456")

        assert route.called
        assert isinstance(result, Note)
        assert result.title == "Meeting notes"
        await client.close()

    @respx.mock
    async def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/notes").mock(
            return_value=httpx.Response(200, json=MOCK_NOTE_CREATED)
        )
        client = _async_client()
        result = await client.notes.create(
            parent_object="deals",
            parent_record_id="rec_03new456abc789",
            title="New note",
            content="Some content here.",
        )

        assert route.called
        assert isinstance(result, Note)
        assert result.title == "New note"
        await client.close()

    @respx.mock
    async def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/notes/note_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_NOTE_DELETE)
        )
        client = _async_client()
        result = await client.notes.delete("note_01abc123def456")

        assert route.called
        assert result is None
        await client.close()

    @respx.mock
    async def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/notes/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.notes.get("nonexistent")
        await client.close()
