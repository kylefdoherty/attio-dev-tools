"""Tests for the Entries resource (sync and async)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import AttioPermissionError, NotFoundError
from attio.models._base import ListResponse
from attio.models.common import AttributeValue
from attio.models.entries import Entry
from attio.models.records import Sort
from tests.fixtures.factory import (
    MOCK_ATTRIBUTE_VALUES_LIST,
    MOCK_DELETE_RESPONSE,
    MOCK_ENTRIES_LIST,
    MOCK_ENTRY,
    MOCK_ENTRY_2,
    MOCK_ENTRY_CREATED,
    MOCK_ENTRY_SINGLE,
    MOCK_ENTRY_UPDATED,
    MOCK_NOT_FOUND_ERROR,
    MOCK_PERMISSION_ERROR,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_entries"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestEntriesResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.post(f"{BASE_URL}/lists/sales_pipeline/entries/query").mock(
            return_value=httpx.Response(200, json=MOCK_ENTRIES_LIST)
        )
        client = _sync_client()
        result = client.entries.list("sales_pipeline")

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Entry)
        assert result.data[0].id.entry_id == "entry_01abc"
        assert result.data[0].parent_record_id == "rec_01abc"
        assert result.data[0].parent_object == "people"
        assert "stage" in result.data[0].entry_values
        client.close()

    @respx.mock
    def test_list_with_params(self) -> None:
        route = respx.post(f"{BASE_URL}/lists/sales_pipeline/entries/query").mock(
            return_value=httpx.Response(200, json=MOCK_ENTRIES_LIST)
        )
        client = _sync_client()
        client.entries.list("sales_pipeline", limit=10, offset=5)

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"limit": 10, "offset": 5}
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(
            f"{BASE_URL}/lists/sales_pipeline/entries/entry_01abc"
        ).mock(return_value=httpx.Response(200, json=MOCK_ENTRY_SINGLE))
        client = _sync_client()
        result = client.entries.get("sales_pipeline", "entry_01abc")

        assert route.called
        assert isinstance(result, Entry)
        assert result.id.entry_id == "entry_01abc"
        assert result.id.workspace_id == "ws_01abc"
        assert result.id.list_id == "list_01abc"
        assert "stage" in result.entry_values
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/lists/sales_pipeline/entries").mock(
            return_value=httpx.Response(200, json=MOCK_ENTRY_CREATED)
        )
        client = _sync_client()
        entry_values = {
            "stage": [{"status": {"title": "Open"}}],
        }
        result = client.entries.create(
            "sales_pipeline",
            parent_record_id="rec_03new",
            parent_object="companies",
            entry_values=entry_values,
        )

        assert route.called
        assert isinstance(result, Entry)
        assert result.id.entry_id == "entry_03new"
        assert result.parent_record_id == "rec_03new"
        assert result.parent_object == "companies"

        # Verify request body includes parent_record_id, parent_object, and entry_values
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "parent_record_id": "rec_03new",
                "parent_object": "companies",
                "entry_values": entry_values,
            }
        }
        client.close()

    @respx.mock
    def test_create_without_entry_values(self) -> None:
        route = respx.post(f"{BASE_URL}/lists/sales_pipeline/entries").mock(
            return_value=httpx.Response(200, json=MOCK_ENTRY_CREATED)
        )
        client = _sync_client()
        result = client.entries.create(
            "sales_pipeline",
            parent_record_id="rec_03new",
            parent_object="companies",
        )

        assert route.called
        assert isinstance(result, Entry)

        # Verify body does not include entry_values when not provided
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "parent_record_id": "rec_03new",
                "parent_object": "companies",
            }
        }
        client.close()

    @respx.mock
    def test_update(self) -> None:
        route = respx.put(
            f"{BASE_URL}/lists/sales_pipeline/entries/entry_01abc"
        ).mock(return_value=httpx.Response(200, json=MOCK_ENTRY_UPDATED))
        client = _sync_client()
        entry_values = {"stage": [{"status": {"title": "Won"}}]}
        result = client.entries.update(
            "sales_pipeline", "entry_01abc", entry_values=entry_values
        )

        assert route.called
        assert isinstance(result, Entry)

        # Verify request body wraps entry_values in {"data": {"entry_values": ...}}
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"entry_values": entry_values}}
        client.close()

    @respx.mock
    def test_append(self) -> None:
        route = respx.patch(
            f"{BASE_URL}/lists/sales_pipeline/entries/entry_01abc"
        ).mock(return_value=httpx.Response(200, json=MOCK_ENTRY_UPDATED))
        client = _sync_client()
        entry_values = {"tags": [{"option": {"title": "VIP"}}]}
        result = client.entries.append(
            "sales_pipeline", "entry_01abc", entry_values=entry_values
        )

        assert route.called
        assert isinstance(result, Entry)

        # Verify request body wraps entry_values
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"entry_values": entry_values}}
        client.close()

    @respx.mock
    def test_delete(self) -> None:
        route = respx.delete(
            f"{BASE_URL}/lists/sales_pipeline/entries/entry_01abc"
        ).mock(return_value=httpx.Response(200, json=MOCK_DELETE_RESPONSE))
        client = _sync_client()
        result = client.entries.delete("sales_pipeline", "entry_01abc")

        assert route.called
        assert result is None
        client.close()

    @respx.mock
    def test_upsert(self) -> None:
        route = respx.put(f"{BASE_URL}/lists/sales_pipeline/entries").mock(
            return_value=httpx.Response(200, json=MOCK_ENTRY_CREATED)
        )
        client = _sync_client()
        entry_values = {"stage": [{"status": {"title": "Open"}}]}
        result = client.entries.upsert(
            "sales_pipeline",
            parent_record_id="rec_03new",
            parent_object="companies",
            entry_values=entry_values,
        )

        assert route.called
        assert isinstance(result, Entry)

        # Verify request body includes parent_record_id, parent_object, and entry_values
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "parent_record_id": "rec_03new",
                "parent_object": "companies",
                "entry_values": entry_values,
            }
        }
        client.close()

    @respx.mock
    def test_upsert_without_entry_values(self) -> None:
        route = respx.put(f"{BASE_URL}/lists/sales_pipeline/entries").mock(
            return_value=httpx.Response(200, json=MOCK_ENTRY_CREATED)
        )
        client = _sync_client()
        result = client.entries.upsert(
            "sales_pipeline",
            parent_record_id="rec_03new",
            parent_object="companies",
        )

        assert route.called
        assert isinstance(result, Entry)

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "parent_record_id": "rec_03new",
                "parent_object": "companies",
            }
        }
        client.close()

    @respx.mock
    def test_query(self) -> None:
        route = respx.post(
            f"{BASE_URL}/lists/sales_pipeline/entries/query"
        ).mock(return_value=httpx.Response(200, json=MOCK_ENTRIES_LIST))
        client = _sync_client()
        sorts = [Sort(attribute="created_at", direction="desc")]
        result = client.entries.query(
            "sales_pipeline",
            filter={"stage": {"$eq": "Open"}},
            sorts=sorts,
            limit=100,
            offset=0,
        )

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "filter": {"stage": {"$eq": "Open"}},
            "sorts": [{"attribute": "created_at", "direction": "desc"}],
            "limit": 100,
            "offset": 0,
        }
        client.close()

    @respx.mock
    def test_query_with_filter_view_id(self) -> None:
        route = respx.post(
            f"{BASE_URL}/lists/sales_pipeline/entries/query"
        ).mock(return_value=httpx.Response(200, json=MOCK_ENTRIES_LIST))
        client = _sync_client()
        client.entries.query("sales_pipeline", filter_view_id="view_01abc")

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"filter_view_id": "view_01abc"}
        client.close()

    @respx.mock
    def test_query_minimal(self) -> None:
        """Query with no params sends empty body."""
        route = respx.post(
            f"{BASE_URL}/lists/sales_pipeline/entries/query"
        ).mock(return_value=httpx.Response(200, json=MOCK_ENTRIES_LIST))
        client = _sync_client()
        client.entries.query("sales_pipeline")

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {}
        client.close()

    @respx.mock
    def test_get_attribute_values(self) -> None:
        route = respx.get(
            f"{BASE_URL}/lists/sales_pipeline/entries/entry_01abc/attributes/stage/values"
        ).mock(return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_VALUES_LIST))
        client = _sync_client()
        result = client.entries.get_attribute_values(
            "sales_pipeline", "entry_01abc", "stage"
        )

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], AttributeValue)
        assert result.data[0].attribute_type == "text"
        client.close()

    @respx.mock
    def test_get_attribute_values_with_params(self) -> None:
        route = respx.get(
            f"{BASE_URL}/lists/sales_pipeline/entries/entry_01abc/attributes/stage/values"
        ).mock(return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_VALUES_LIST))
        client = _sync_client()
        client.entries.get_attribute_values(
            "sales_pipeline",
            "entry_01abc",
            "stage",
            show_historic=True,
            limit=50,
            offset=10,
        )

        request = route.calls[0].request
        assert request.url.params["show_historic"] == "true"
        assert request.url.params["limit"] == "50"
        assert request.url.params["offset"] == "10"
        client.close()

    @respx.mock
    def test_query_all_single_page(self) -> None:
        """query_all with results fitting in a single page."""
        route = respx.post(
            f"{BASE_URL}/lists/sales_pipeline/entries/query"
        ).mock(return_value=httpx.Response(200, json=MOCK_ENTRIES_LIST))
        client = _sync_client()
        iterator = client.entries.query_all("sales_pipeline", limit=500)
        entries = list(iterator)

        assert route.called
        assert len(entries) == 2
        assert all(isinstance(e, Entry) for e in entries)
        client.close()

    @respx.mock
    def test_query_all_multiple_pages(self) -> None:
        """query_all iterates across multiple pages, stopping when partial page received."""
        page_1 = {"data": [MOCK_ENTRY]}  # full page (limit=1)
        page_2 = {"data": [MOCK_ENTRY_2]}  # full page (limit=1) -- but this is last
        page_3 = {"data": []}  # empty page signals end

        call_count = 0

        def side_effect(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(200, json=page_1)
            elif call_count == 2:
                return httpx.Response(200, json=page_2)
            else:
                return httpx.Response(200, json=page_3)

        route = respx.post(
            f"{BASE_URL}/lists/sales_pipeline/entries/query"
        ).mock(side_effect=side_effect)
        client = _sync_client()
        iterator = client.entries.query_all("sales_pipeline", limit=1)
        entries = list(iterator)

        assert len(entries) == 2
        assert entries[0].id.entry_id == "entry_01abc"
        assert entries[1].id.entry_id == "entry_02xyz"

        # Verify offset increments correctly
        assert call_count == 3
        bodies = [json.loads(c.request.content) for c in route.calls]
        assert bodies[0].get("offset", 0) == 0
        assert bodies[1]["offset"] == 1
        assert bodies[2]["offset"] == 2
        client.close()

    @respx.mock
    def test_query_all_with_filter_and_sorts(self) -> None:
        """query_all passes filter and sorts through to each page request."""
        route = respx.post(
            f"{BASE_URL}/lists/sales_pipeline/entries/query"
        ).mock(return_value=httpx.Response(200, json={"data": []}))
        client = _sync_client()
        sorts = [Sort(attribute="stage", direction="asc")]
        iterator = client.entries.query_all(
            "sales_pipeline",
            filter={"status": "active"},
            sorts=sorts,
            limit=100,
        )
        list(iterator)  # consume the iterator

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body["filter"] == {"status": "active"}
        assert body["sorts"] == [{"attribute": "stage", "direction": "asc"}]
        assert body["limit"] == 100
        client.close()

    @respx.mock
    def test_get_not_found(self) -> None:
        respx.get(
            f"{BASE_URL}/lists/sales_pipeline/entries/nonexistent"
        ).mock(return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR))
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.entries.get("sales_pipeline", "nonexistent")
        assert exc_info.value.status_code == 404
        client.close()

    @respx.mock
    def test_create_permission_error(self) -> None:
        respx.post(f"{BASE_URL}/lists/sales_pipeline/entries").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _sync_client()
        with pytest.raises(AttioPermissionError) as exc_info:
            client.entries.create(
                "sales_pipeline",
                parent_record_id="rec_01abc",
                parent_object="people",
            )
        assert exc_info.value.status_code == 403
        client.close()

    @respx.mock
    def test_entry_values_field_name(self) -> None:
        """Verify that the response model uses entry_values (not values)."""
        route = respx.get(
            f"{BASE_URL}/lists/sales_pipeline/entries/entry_01abc"
        ).mock(return_value=httpx.Response(200, json=MOCK_ENTRY_SINGLE))
        client = _sync_client()
        result = client.entries.get("sales_pipeline", "entry_01abc")

        assert route.called
        assert hasattr(result, "entry_values")
        assert isinstance(result.entry_values, dict)
        assert "stage" in result.entry_values
        assert isinstance(result.entry_values["stage"], list)
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestEntriesResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.post(f"{BASE_URL}/lists/sales_pipeline/entries/query").mock(
            return_value=httpx.Response(200, json=MOCK_ENTRIES_LIST)
        )
        client = _async_client()
        result = await client.entries.list("sales_pipeline")

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Entry)
        assert result.data[0].id.entry_id == "entry_01abc"
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(
            f"{BASE_URL}/lists/sales_pipeline/entries/entry_01abc"
        ).mock(return_value=httpx.Response(200, json=MOCK_ENTRY_SINGLE))
        client = _async_client()
        result = await client.entries.get("sales_pipeline", "entry_01abc")

        assert route.called
        assert isinstance(result, Entry)
        assert result.id.entry_id == "entry_01abc"
        assert "stage" in result.entry_values
        await client.close()

    @respx.mock
    async def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/lists/sales_pipeline/entries").mock(
            return_value=httpx.Response(200, json=MOCK_ENTRY_CREATED)
        )
        client = _async_client()
        entry_values = {"stage": [{"status": {"title": "Open"}}]}
        result = await client.entries.create(
            "sales_pipeline",
            parent_record_id="rec_03new",
            parent_object="companies",
            entry_values=entry_values,
        )

        assert route.called
        assert isinstance(result, Entry)
        assert result.id.entry_id == "entry_03new"

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "parent_record_id": "rec_03new",
                "parent_object": "companies",
                "entry_values": entry_values,
            }
        }
        await client.close()

    @respx.mock
    async def test_update(self) -> None:
        route = respx.put(
            f"{BASE_URL}/lists/sales_pipeline/entries/entry_01abc"
        ).mock(return_value=httpx.Response(200, json=MOCK_ENTRY_UPDATED))
        client = _async_client()
        entry_values = {"stage": [{"status": {"title": "Won"}}]}
        result = await client.entries.update(
            "sales_pipeline", "entry_01abc", entry_values=entry_values
        )

        assert route.called
        assert isinstance(result, Entry)

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"entry_values": entry_values}}
        await client.close()

    @respx.mock
    async def test_append(self) -> None:
        route = respx.patch(
            f"{BASE_URL}/lists/sales_pipeline/entries/entry_01abc"
        ).mock(return_value=httpx.Response(200, json=MOCK_ENTRY_UPDATED))
        client = _async_client()
        entry_values = {"tags": [{"option": {"title": "VIP"}}]}
        result = await client.entries.append(
            "sales_pipeline", "entry_01abc", entry_values=entry_values
        )

        assert route.called
        assert isinstance(result, Entry)
        await client.close()

    @respx.mock
    async def test_delete(self) -> None:
        route = respx.delete(
            f"{BASE_URL}/lists/sales_pipeline/entries/entry_01abc"
        ).mock(return_value=httpx.Response(200, json=MOCK_DELETE_RESPONSE))
        client = _async_client()
        result = await client.entries.delete("sales_pipeline", "entry_01abc")

        assert route.called
        assert result is None
        await client.close()

    @respx.mock
    async def test_upsert(self) -> None:
        route = respx.put(f"{BASE_URL}/lists/sales_pipeline/entries").mock(
            return_value=httpx.Response(200, json=MOCK_ENTRY_CREATED)
        )
        client = _async_client()
        entry_values = {"stage": [{"status": {"title": "Open"}}]}
        result = await client.entries.upsert(
            "sales_pipeline",
            parent_record_id="rec_03new",
            parent_object="companies",
            entry_values=entry_values,
        )

        assert route.called
        assert isinstance(result, Entry)

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "parent_record_id": "rec_03new",
                "parent_object": "companies",
                "entry_values": entry_values,
            }
        }
        await client.close()

    @respx.mock
    async def test_query(self) -> None:
        route = respx.post(
            f"{BASE_URL}/lists/sales_pipeline/entries/query"
        ).mock(return_value=httpx.Response(200, json=MOCK_ENTRIES_LIST))
        client = _async_client()
        sorts = [Sort(attribute="created_at", direction="desc")]
        result = await client.entries.query(
            "sales_pipeline",
            filter={"stage": {"$eq": "Open"}},
            sorts=sorts,
            limit=100,
            offset=0,
        )

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "filter": {"stage": {"$eq": "Open"}},
            "sorts": [{"attribute": "created_at", "direction": "desc"}],
            "limit": 100,
            "offset": 0,
        }
        await client.close()

    @respx.mock
    async def test_get_attribute_values(self) -> None:
        route = respx.get(
            f"{BASE_URL}/lists/sales_pipeline/entries/entry_01abc/attributes/stage/values"
        ).mock(return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_VALUES_LIST))
        client = _async_client()
        result = await client.entries.get_attribute_values(
            "sales_pipeline", "entry_01abc", "stage"
        )

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], AttributeValue)
        await client.close()

    @respx.mock
    async def test_query_all_multiple_pages(self) -> None:
        """Async query_all iterates across multiple pages."""
        page_1 = {"data": [MOCK_ENTRY]}
        page_2 = {"data": [MOCK_ENTRY_2]}
        page_3 = {"data": []}

        call_count = 0

        def side_effect(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(200, json=page_1)
            elif call_count == 2:
                return httpx.Response(200, json=page_2)
            else:
                return httpx.Response(200, json=page_3)

        respx.post(
            f"{BASE_URL}/lists/sales_pipeline/entries/query"
        ).mock(side_effect=side_effect)
        client = _async_client()
        iterator = client.entries.query_all("sales_pipeline", limit=1)
        entries: list[Entry] = []
        async for entry in iterator:
            entries.append(entry)

        assert len(entries) == 2
        assert entries[0].id.entry_id == "entry_01abc"
        assert entries[1].id.entry_id == "entry_02xyz"
        assert call_count == 3
        await client.close()

    @respx.mock
    async def test_get_not_found(self) -> None:
        respx.get(
            f"{BASE_URL}/lists/sales_pipeline/entries/nonexistent"
        ).mock(return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR))
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.entries.get("sales_pipeline", "nonexistent")
        await client.close()

    @respx.mock
    async def test_create_permission_error(self) -> None:
        respx.post(f"{BASE_URL}/lists/sales_pipeline/entries").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _async_client()
        with pytest.raises(AttioPermissionError):
            await client.entries.create(
                "sales_pipeline",
                parent_record_id="rec_01abc",
                parent_object="people",
            )
        await client.close()


# ---------------------------------------------------------------------------
# Mixin body construction tests
# ---------------------------------------------------------------------------


class TestEntriesMixin:
    """Test the shared body/param construction logic."""

    def test_build_entry_values_body(self) -> None:
        from attio.resources.entries import _EntriesMixin

        result = _EntriesMixin._build_entry_values_body(
            {"stage": [{"status": {"title": "Open"}}]}
        )
        assert result == {
            "data": {"entry_values": {"stage": [{"status": {"title": "Open"}}]}}
        }

    def test_build_create_body(self) -> None:
        from attio.resources.entries import _EntriesMixin

        result = _EntriesMixin._build_create_body(
            "rec_01abc",
            "people",
            {"stage": [{"status": {"title": "Open"}}]},
        )
        assert result == {
            "data": {
                "parent_record_id": "rec_01abc",
                "parent_object": "people",
                "entry_values": {"stage": [{"status": {"title": "Open"}}]},
            }
        }

    def test_build_create_body_without_entry_values(self) -> None:
        from attio.resources.entries import _EntriesMixin

        result = _EntriesMixin._build_create_body("rec_01abc", "people")
        assert result == {
            "data": {
                "parent_record_id": "rec_01abc",
                "parent_object": "people",
            }
        }

    def test_build_upsert_body(self) -> None:
        from attio.resources.entries import _EntriesMixin

        result = _EntriesMixin._build_upsert_body(
            "rec_01abc",
            "people",
            {"stage": [{"status": {"title": "Open"}}]},
        )
        assert result == {
            "data": {
                "parent_record_id": "rec_01abc",
                "parent_object": "people",
                "entry_values": {"stage": [{"status": {"title": "Open"}}]},
            }
        }

    def test_build_upsert_body_without_entry_values(self) -> None:
        from attio.resources.entries import _EntriesMixin

        result = _EntriesMixin._build_upsert_body("rec_01abc", "people")
        assert result == {
            "data": {
                "parent_record_id": "rec_01abc",
                "parent_object": "people",
            }
        }

    def test_build_query_body_empty(self) -> None:
        from attio.resources.entries import _EntriesMixin

        result = _EntriesMixin._build_query_body()
        assert result == {}

    def test_build_query_body_full(self) -> None:
        from attio.resources.entries import _EntriesMixin

        sorts = [Sort(attribute="created_at", direction="desc")]
        result = _EntriesMixin._build_query_body(
            filter={"stage": "Open"},
            filter_view_id="view_01",
            sorts=sorts,
            limit=100,
            offset=50,
        )
        assert result == {
            "filter": {"stage": "Open"},
            "filter_view_id": "view_01",
            "sorts": [{"attribute": "created_at", "direction": "desc"}],
            "limit": 100,
            "offset": 50,
        }

    def test_build_list_params_none(self) -> None:
        from attio.resources.entries import _EntriesMixin

        result = _EntriesMixin._build_list_params()
        assert result is None

    def test_build_list_params_with_values(self) -> None:
        from attio.resources.entries import _EntriesMixin

        result = _EntriesMixin._build_list_params(limit=10, offset=5)
        assert result == {"limit": 10, "offset": 5}

    def test_build_attribute_values_params_default(self) -> None:
        from attio.resources.entries import _EntriesMixin

        result = _EntriesMixin._build_attribute_values_params()
        assert result is None

    def test_build_attribute_values_params_with_show_historic(self) -> None:
        from attio.resources.entries import _EntriesMixin

        result = _EntriesMixin._build_attribute_values_params(
            show_historic=True, limit=20, offset=0
        )
        assert result == {"show_historic": "true", "limit": 20, "offset": 0}
