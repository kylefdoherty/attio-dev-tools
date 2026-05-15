"""Tests for the Tasks resource (sync and async)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import NotFoundError
from attio.models._base import ListResponse
from attio.models.tasks import Task
from tests.fixtures.factory import (
    MOCK_NOT_FOUND_ERROR,
    MOCK_TASK,
    MOCK_TASK_CREATED,
    MOCK_TASK_DELETE,
    MOCK_TASK_SINGLE,
    MOCK_TASK_UPDATED,
    MOCK_TASKS_LIST,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_tasks"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestTasksResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/tasks").mock(
            return_value=httpx.Response(200, json=MOCK_TASKS_LIST)
        )
        client = _sync_client()
        result = client.tasks.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Task)
        assert result.data[0].content_plaintext == "Send proposal to Acme Corp"
        assert result.data[0].id.task_id == "task_01abc123def456"
        assert result.data[0].is_completed is False
        assert result.data[1].is_completed is True
        client.close()

    @respx.mock
    def test_list_filter_by_completed(self) -> None:
        route = respx.get(f"{BASE_URL}/tasks").mock(
            return_value=httpx.Response(200, json={"data": [MOCK_TASK]})
        )
        client = _sync_client()
        result = client.tasks.list(is_completed=False)

        assert route.called
        request = route.calls[0].request
        assert "is_completed=false" in str(request.url).lower()
        assert len(result.data) == 1
        client.close()

    @respx.mock
    def test_list_filter_by_assignee(self) -> None:
        route = respx.get(f"{BASE_URL}/tasks").mock(
            return_value=httpx.Response(200, json={"data": [MOCK_TASK]})
        )
        client = _sync_client()
        result = client.tasks.list(assignee="wm_01abc123def456")

        assert route.called
        request = route.calls[0].request
        assert "assignee=wm_01abc123def456" in str(request.url)
        assert len(result.data) == 1
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/tasks/task_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_TASK_SINGLE)
        )
        client = _sync_client()
        result = client.tasks.get("task_01abc123def456")

        assert route.called
        assert isinstance(result, Task)
        assert result.content_plaintext == "Send proposal to Acme Corp"
        assert result.is_completed is False
        assert len(result.linked_records) == 1
        assert result.linked_records[0].target_object == "companies"
        assert len(result.assignees) == 1
        assert result.assignees[0].referenced_actor_type == "workspace-member"
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/tasks").mock(
            return_value=httpx.Response(200, json=MOCK_TASK_CREATED)
        )
        client = _sync_client()
        result = client.tasks.create(
            content="Draft agenda",
            format="plaintext",
            deadline_at="2024-07-01T09:00:00.000Z",
            linked_records=[
                {
                    "target_object": "deals",
                    "target_record_id": "rec_03new456abc789",
                }
            ],
            assignees=[
                {
                    "referenced_actor_type": "workspace-member",
                    "referenced_actor_id": "wm_02xyz789ghi012",
                }
            ],
        )

        assert route.called
        assert isinstance(result, Task)
        assert result.content_plaintext == "Draft agenda"
        assert result.is_completed is False

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "content": "Draft agenda",
                "format": "plaintext",
                "is_completed": False,
                "deadline_at": "2024-07-01T09:00:00.000Z",
                "linked_records": [
                    {
                        "target_object": "deals",
                        "target_record_id": "rec_03new456abc789",
                    }
                ],
                "assignees": [
                    {
                        "referenced_actor_type": "workspace-member",
                        "referenced_actor_id": "wm_02xyz789ghi012",
                    }
                ],
            }
        }
        client.close()

    @respx.mock
    def test_update(self) -> None:
        route = respx.patch(f"{BASE_URL}/tasks/task_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_TASK_UPDATED)
        )
        client = _sync_client()
        result = client.tasks.update(
            "task_01abc123def456",
            is_completed=True,
            content="Send proposal to Acme Corp (updated)",
        )

        assert route.called
        assert isinstance(result, Task)
        assert result.is_completed is True
        assert result.content_plaintext == "Send proposal to Acme Corp (updated)"

        # Verify request body only contains specified fields
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "content": "Send proposal to Acme Corp (updated)",
                "is_completed": True,
            }
        }
        client.close()

    @respx.mock
    def test_update_partial(self) -> None:
        route = respx.patch(f"{BASE_URL}/tasks/task_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_TASK_UPDATED)
        )
        client = _sync_client()
        client.tasks.update("task_01abc123def456", is_completed=True)

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"is_completed": True}}
        client.close()

    @respx.mock
    def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/tasks/task_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_TASK_DELETE)
        )
        client = _sync_client()
        result = client.tasks.delete("task_01abc123def456")

        assert route.called
        assert result is None
        client.close()

    @respx.mock
    def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/tasks/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.tasks.get("nonexistent")
        assert exc_info.value.status_code == 404
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestTasksResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/tasks").mock(
            return_value=httpx.Response(200, json=MOCK_TASKS_LIST)
        )
        client = _async_client()
        result = await client.tasks.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Task)
        assert result.data[0].content_plaintext == "Send proposal to Acme Corp"
        await client.close()

    @respx.mock
    async def test_list_filter_by_completed(self) -> None:
        route = respx.get(f"{BASE_URL}/tasks").mock(
            return_value=httpx.Response(200, json={"data": [MOCK_TASK]})
        )
        client = _async_client()
        result = await client.tasks.list(is_completed=False)

        assert route.called
        request = route.calls[0].request
        assert "is_completed=false" in str(request.url).lower()
        assert len(result.data) == 1
        await client.close()

    @respx.mock
    async def test_list_filter_by_assignee(self) -> None:
        route = respx.get(f"{BASE_URL}/tasks").mock(
            return_value=httpx.Response(200, json={"data": [MOCK_TASK]})
        )
        client = _async_client()
        await client.tasks.list(assignee="wm_01abc123def456")

        assert route.called
        request = route.calls[0].request
        assert "assignee=wm_01abc123def456" in str(request.url)
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/tasks/task_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_TASK_SINGLE)
        )
        client = _async_client()
        result = await client.tasks.get("task_01abc123def456")

        assert route.called
        assert isinstance(result, Task)
        assert result.content_plaintext == "Send proposal to Acme Corp"
        assert len(result.linked_records) == 1
        await client.close()

    @respx.mock
    async def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/tasks").mock(
            return_value=httpx.Response(200, json=MOCK_TASK_CREATED)
        )
        client = _async_client()
        result = await client.tasks.create(
            content="Draft agenda",
            deadline_at="2024-07-01T09:00:00.000Z",
        )

        assert route.called
        assert isinstance(result, Task)
        assert result.content_plaintext == "Draft agenda"
        await client.close()

    @respx.mock
    async def test_update(self) -> None:
        route = respx.patch(f"{BASE_URL}/tasks/task_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_TASK_UPDATED)
        )
        client = _async_client()
        result = await client.tasks.update(
            "task_01abc123def456",
            is_completed=True,
        )

        assert route.called
        assert isinstance(result, Task)
        assert result.is_completed is True
        await client.close()

    @respx.mock
    async def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/tasks/task_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_TASK_DELETE)
        )
        client = _async_client()
        result = await client.tasks.delete("task_01abc123def456")

        assert route.called
        assert result is None
        await client.close()

    @respx.mock
    async def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/tasks/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.tasks.get("nonexistent")
        await client.close()
