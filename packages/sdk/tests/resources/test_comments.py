"""Tests for the Comments resource (sync and async)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio.models.comments import Comment

from tests.fixtures.factory import (
    MOCK_COMMENT_DELETE,
    MOCK_COMMENT_ON_ENTRY,
    MOCK_COMMENT_ON_RECORD,
    MOCK_COMMENT_ON_THREAD,
    MOCK_COMMENT_SINGLE,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_comments"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestCommentsResourceSync:
    @respx.mock
    def test_create_on_thread(self) -> None:
        route = respx.post(f"{BASE_URL}/comments").mock(
            return_value=httpx.Response(200, json=MOCK_COMMENT_ON_THREAD)
        )
        client = _sync_client()
        result = client.comments.create(
            thread_id="thread_01abc123def456",
            content="Replying to thread.",
            author={"type": "workspace-member", "id": "wm_01abc123def456"},
        )

        assert route.called
        assert isinstance(result, Comment)
        assert result.content_plaintext == "Replying to thread."
        assert result.thread_id == "thread_01abc123def456"

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "thread_id": "thread_01abc123def456",
                "format": "plaintext",
                "content": "Replying to thread.",
                "author": {"type": "workspace-member", "id": "wm_01abc123def456"},
            }
        }
        client.close()

    @respx.mock
    def test_create_on_record(self) -> None:
        route = respx.post(f"{BASE_URL}/comments").mock(
            return_value=httpx.Response(200, json=MOCK_COMMENT_ON_RECORD)
        )
        client = _sync_client()
        result = client.comments.create(
            record={"object": "people", "record_id": "rec_01abc123def456"},
            content="New comment on record.",
            author={"type": "workspace-member", "id": "wm_01abc123def456"},
        )

        assert route.called
        assert isinstance(result, Comment)
        assert result.content_plaintext == "New comment on record."

        # Verify request body contains record, not thread_id or entry
        request = route.calls[0].request
        body = json.loads(request.content)
        assert "record" in body["data"]
        assert "thread_id" not in body["data"]
        assert "entry" not in body["data"]
        client.close()

    @respx.mock
    def test_create_on_entry(self) -> None:
        route = respx.post(f"{BASE_URL}/comments").mock(
            return_value=httpx.Response(200, json=MOCK_COMMENT_ON_ENTRY)
        )
        client = _sync_client()
        result = client.comments.create(
            entry={"list": "sales_pipeline", "entry_id": "entry_01abc123def456"},
            content="New comment on entry.",
            author={"type": "workspace-member", "id": "wm_01abc123def456"},
        )

        assert route.called
        assert isinstance(result, Comment)
        assert result.content_plaintext == "New comment on entry."
        assert result.entry is not None

        # Verify request body contains entry, not thread_id or record
        request = route.calls[0].request
        body = json.loads(request.content)
        assert "entry" in body["data"]
        assert "thread_id" not in body["data"]
        assert "record" not in body["data"]
        client.close()

    def test_create_no_target_raises(self) -> None:
        client = _sync_client()
        with pytest.raises(ValueError, match="Exactly one of"):
            client.comments.create(
                content="Missing target.",
                author={"type": "workspace-member", "id": "wm_01abc123def456"},
            )
        client.close()

    def test_create_multiple_targets_raises(self) -> None:
        client = _sync_client()
        with pytest.raises(ValueError, match="Exactly one of"):
            client.comments.create(
                thread_id="thread_01abc123def456",
                record={"object": "people", "record_id": "rec_01abc123def456"},
                content="Multiple targets.",
                author={"type": "workspace-member", "id": "wm_01abc123def456"},
            )
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/comments/comment_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_COMMENT_SINGLE)
        )
        client = _sync_client()
        result = client.comments.get("comment_01abc123def456")

        assert route.called
        assert isinstance(result, Comment)
        assert result.id.comment_id == "comment_01abc123def456"
        assert result.content_plaintext == "This looks great, let's proceed."
        client.close()

    @respx.mock
    def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/comments/comment_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_COMMENT_DELETE)
        )
        client = _sync_client()
        result = client.comments.delete("comment_01abc123def456")

        assert route.called
        assert result is None
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestCommentsResourceAsync:
    @respx.mock
    async def test_create_on_thread(self) -> None:
        route = respx.post(f"{BASE_URL}/comments").mock(
            return_value=httpx.Response(200, json=MOCK_COMMENT_ON_THREAD)
        )
        client = _async_client()
        result = await client.comments.create(
            thread_id="thread_01abc123def456",
            content="Replying to thread.",
            author={"type": "workspace-member", "id": "wm_01abc123def456"},
        )

        assert route.called
        assert isinstance(result, Comment)
        assert result.content_plaintext == "Replying to thread."
        await client.close()

    @respx.mock
    async def test_create_on_record(self) -> None:
        route = respx.post(f"{BASE_URL}/comments").mock(
            return_value=httpx.Response(200, json=MOCK_COMMENT_ON_RECORD)
        )
        client = _async_client()
        result = await client.comments.create(
            record={"object": "people", "record_id": "rec_01abc123def456"},
            content="New comment on record.",
            author={"type": "workspace-member", "id": "wm_01abc123def456"},
        )

        assert route.called
        assert isinstance(result, Comment)
        assert result.content_plaintext == "New comment on record."
        await client.close()

    @respx.mock
    async def test_create_on_entry(self) -> None:
        route = respx.post(f"{BASE_URL}/comments").mock(
            return_value=httpx.Response(200, json=MOCK_COMMENT_ON_ENTRY)
        )
        client = _async_client()
        result = await client.comments.create(
            entry={"list": "sales_pipeline", "entry_id": "entry_01abc123def456"},
            content="New comment on entry.",
            author={"type": "workspace-member", "id": "wm_01abc123def456"},
        )

        assert route.called
        assert isinstance(result, Comment)
        assert result.entry is not None
        await client.close()

    async def test_create_no_target_raises(self) -> None:
        client = _async_client()
        with pytest.raises(ValueError, match="Exactly one of"):
            await client.comments.create(
                content="Missing target.",
                author={"type": "workspace-member", "id": "wm_01abc123def456"},
            )
        await client.close()

    async def test_create_multiple_targets_raises(self) -> None:
        client = _async_client()
        with pytest.raises(ValueError, match="Exactly one of"):
            await client.comments.create(
                thread_id="thread_01abc123def456",
                entry={"list": "sales_pipeline", "entry_id": "entry_01abc123def456"},
                content="Multiple targets.",
                author={"type": "workspace-member", "id": "wm_01abc123def456"},
            )
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/comments/comment_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_COMMENT_SINGLE)
        )
        client = _async_client()
        result = await client.comments.get("comment_01abc123def456")

        assert route.called
        assert isinstance(result, Comment)
        assert result.id.comment_id == "comment_01abc123def456"
        await client.close()

    @respx.mock
    async def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/comments/comment_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_COMMENT_DELETE)
        )
        client = _async_client()
        result = await client.comments.delete("comment_01abc123def456")

        assert route.called
        assert result is None
        await client.close()
