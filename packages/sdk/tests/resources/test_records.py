"""Tests for the Records resource (sync and async)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import AttioPermissionError, NotFoundError
from attio.models._base import ListResponse
from attio.models.common import AttributeValue
from attio.models.records import GlobalSearchResult, Record, RecordEntry, Sort

from tests.fixtures.factory import (
    MOCK_ATTRIBUTE_VALUES_LIST,
    MOCK_DELETE_RESPONSE,
    MOCK_GLOBAL_SEARCH_RESULTS,
    MOCK_NOT_FOUND_ERROR,
    MOCK_PERMISSION_ERROR,
    MOCK_RECORD,
    MOCK_RECORD_2,
    MOCK_RECORD_CREATED,
    MOCK_RECORD_ENTRIES_LIST,
    MOCK_RECORD_SINGLE,
    MOCK_RECORD_UPDATED,
    MOCK_RECORDS_LIST,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_records"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestRecordsResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        result = client.records.list("people")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Record)
        assert result.data[0].id.record_id == "rec_01abc"
        assert result.data[0].web_url == "https://app.attio.com/people/rec_01abc"
        client.close()

    @respx.mock
    def test_list_with_params(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        client.records.list("people", limit=10, offset=5)

        assert route.called
        request = route.calls[0].request
        assert request.url.params["limit"] == "10"
        assert request.url.params["offset"] == "5"
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/people/records/rec_01abc").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_SINGLE)
        )
        client = _sync_client()
        result = client.records.get("people", "rec_01abc")

        assert route.called
        assert isinstance(result, Record)
        assert result.id.record_id == "rec_01abc"
        assert result.id.workspace_id == "ws_01abc"
        assert "name" in result.values
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_CREATED)
        )
        client = _sync_client()
        values = {
            "name": [{"first_name": "Alice", "last_name": "Wonder"}],
        }
        result = client.records.create("people", values=values)

        assert route.called
        assert isinstance(result, Record)
        assert result.id.record_id == "rec_03new"

        # Verify request body wraps values in {"data": {"values": ...}}
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"values": values}}
        client.close()

    @respx.mock
    def test_update(self) -> None:
        route = respx.put(f"{BASE_URL}/objects/people/records/rec_01abc").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_UPDATED)
        )
        client = _sync_client()
        values = {"name": [{"first_name": "Jane", "last_name": "Updated"}]}
        result = client.records.update("people", "rec_01abc", values=values)

        assert route.called
        assert isinstance(result, Record)

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"values": values}}
        client.close()

    @respx.mock
    def test_append(self) -> None:
        route = respx.patch(f"{BASE_URL}/objects/people/records/rec_01abc").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_UPDATED)
        )
        client = _sync_client()
        values = {"tags": [{"option": {"title": "VIP"}}]}
        result = client.records.append("people", "rec_01abc", values=values)

        assert route.called
        assert isinstance(result, Record)

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"values": values}}
        client.close()

    @respx.mock
    def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/objects/people/records/rec_01abc").mock(
            return_value=httpx.Response(200, json=MOCK_DELETE_RESPONSE)
        )
        client = _sync_client()
        result = client.records.delete("people", "rec_01abc")

        assert route.called
        assert result is None
        client.close()

    @respx.mock
    def test_upsert(self) -> None:
        route = respx.put(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_CREATED)
        )
        client = _sync_client()
        values = {
            "email_addresses": [{"email_address": "alice@example.com"}],
            "name": [{"first_name": "Alice", "last_name": "Wonder"}],
        }
        result = client.records.upsert(
            "people",
            matching_attribute="email_addresses",
            values=values,
        )

        assert route.called
        assert isinstance(result, Record)

        # Verify request body includes matching_attribute + values
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "matching_attribute": "email_addresses",
                "values": values,
            }
        }
        client.close()

    @respx.mock
    def test_query(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/people/records/query").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        sorts = [Sort(attribute="created_at", direction="desc")]
        result = client.records.query(
            "people",
            filter={"name": {"$contains": "Jane"}},
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
            "filter": {"name": {"$contains": "Jane"}},
            "sorts": [{"attribute": "created_at", "direction": "desc"}],
            "limit": 100,
            "offset": 0,
        }
        client.close()

    @respx.mock
    def test_query_with_filter_view_id(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/people/records/query").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        client.records.query("people", filter_view_id="view_01abc")

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"filter_view_id": "view_01abc"}
        client.close()

    @respx.mock
    def test_query_minimal(self) -> None:
        """Query with no params sends empty body."""
        route = respx.post(f"{BASE_URL}/objects/people/records/query").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        client.records.query("people")

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {}
        client.close()

    @respx.mock
    def test_get_attribute_values(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/people/records/rec_01abc/attributes/email/values"
        ).mock(
            return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_VALUES_LIST)
        )
        client = _sync_client()
        result = client.records.get_attribute_values(
            "people", "rec_01abc", "email"
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
            f"{BASE_URL}/objects/people/records/rec_01abc/attributes/email/values"
        ).mock(
            return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_VALUES_LIST)
        )
        client = _sync_client()
        client.records.get_attribute_values(
            "people",
            "rec_01abc",
            "email",
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
    def test_list_entries(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/people/records/rec_01abc/entries"
        ).mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_ENTRIES_LIST)
        )
        client = _sync_client()
        result = client.records.list_entries("people", "rec_01abc")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], RecordEntry)
        assert result.data[0].list_api_slug == "sales_pipeline"
        assert result.data[0].entry_id == "entry_01abc"
        client.close()

    @respx.mock
    def test_list_entries_with_params(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/people/records/rec_01abc/entries"
        ).mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_ENTRIES_LIST)
        )
        client = _sync_client()
        client.records.list_entries("people", "rec_01abc", limit=50, offset=10)

        request = route.calls[0].request
        assert request.url.params["limit"] == "50"
        assert request.url.params["offset"] == "10"
        client.close()

    @respx.mock
    def test_global_search(self) -> None:
        # NOTE: global_search uses a DIFFERENT URL pattern — not scoped to one object
        route = respx.post(f"{BASE_URL}/objects/records/search").mock(
            return_value=httpx.Response(200, json=MOCK_GLOBAL_SEARCH_RESULTS)
        )
        client = _sync_client()
        result = client.records.global_search(
            query="Jane", objects=["people"], limit=10
        )

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], GlobalSearchResult)
        assert result.data[0].record_text == "Jane Doe"
        assert result.data[0].object_slug == "people"

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "query": "Jane",
            "objects": ["people"],
            "limit": 10,
        }
        client.close()

    @respx.mock
    def test_global_search_url_pattern(self) -> None:
        """Verify global_search hits /objects/records/search, not /objects/{object}/records/search."""
        route = respx.post(f"{BASE_URL}/objects/records/search").mock(
            return_value=httpx.Response(200, json=MOCK_GLOBAL_SEARCH_RESULTS)
        )
        client = _sync_client()
        client.records.global_search(query="test", objects=["people", "companies"])

        assert route.called
        request = route.calls[0].request
        assert str(request.url).startswith(f"{BASE_URL}/objects/records/search")
        client.close()

    @respx.mock
    def test_query_all_single_page(self) -> None:
        """query_all with results fitting in a single page."""
        route = respx.post(f"{BASE_URL}/objects/people/records/query").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        iterator = client.records.query_all("people", limit=500)
        records = list(iterator)

        assert route.called
        assert len(records) == 2
        assert all(isinstance(r, Record) for r in records)
        client.close()

    @respx.mock
    def test_query_all_multiple_pages(self) -> None:
        """query_all iterates across multiple pages, stopping when partial page received."""
        page_1 = {"data": [MOCK_RECORD]}  # full page (limit=1)
        page_2 = {"data": [MOCK_RECORD_2]}  # full page (limit=1) — but this is last
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

        route = respx.post(f"{BASE_URL}/objects/people/records/query").mock(
            side_effect=side_effect
        )
        client = _sync_client()
        iterator = client.records.query_all("people", limit=1)
        records = list(iterator)

        assert len(records) == 2
        assert records[0].id.record_id == "rec_01abc"
        assert records[1].id.record_id == "rec_02xyz"

        # Verify offset increments correctly: first call offset=0, second offset=1, third offset=2
        assert call_count == 3
        bodies = [json.loads(c.request.content) for c in route.calls]
        assert bodies[0].get("offset", 0) == 0
        assert bodies[1]["offset"] == 1
        assert bodies[2]["offset"] == 2
        client.close()

    @respx.mock
    def test_query_all_with_filter_and_sorts(self) -> None:
        """query_all passes filter and sorts through to each page request."""
        route = respx.post(f"{BASE_URL}/objects/people/records/query").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        client = _sync_client()
        sorts = [Sort(attribute="name", direction="asc")]
        iterator = client.records.query_all(
            "people",
            filter={"status": "active"},
            sorts=sorts,
            limit=100,
        )
        list(iterator)  # consume the iterator

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body["filter"] == {"status": "active"}
        assert body["sorts"] == [{"attribute": "name", "direction": "asc"}]
        assert body["limit"] == 100
        client.close()

    @respx.mock
    def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/objects/people/records/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.records.get("people", "nonexistent")
        assert exc_info.value.status_code == 404
        client.close()

    @respx.mock
    def test_create_permission_error(self) -> None:
        respx.post(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _sync_client()
        with pytest.raises(AttioPermissionError) as exc_info:
            client.records.create("people", values={"name": [{"first_name": "Test"}]})
        assert exc_info.value.status_code == 403
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestRecordsResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _async_client()
        result = await client.records.list("people")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Record)
        assert result.data[0].id.record_id == "rec_01abc"
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/people/records/rec_01abc").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_SINGLE)
        )
        client = _async_client()
        result = await client.records.get("people", "rec_01abc")

        assert route.called
        assert isinstance(result, Record)
        assert result.id.record_id == "rec_01abc"
        await client.close()

    @respx.mock
    async def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_CREATED)
        )
        client = _async_client()
        values = {"name": [{"first_name": "Alice", "last_name": "Wonder"}]}
        result = await client.records.create("people", values=values)

        assert route.called
        assert isinstance(result, Record)
        assert result.id.record_id == "rec_03new"

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"values": values}}
        await client.close()

    @respx.mock
    async def test_update(self) -> None:
        route = respx.put(f"{BASE_URL}/objects/people/records/rec_01abc").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_UPDATED)
        )
        client = _async_client()
        values = {"name": [{"first_name": "Jane", "last_name": "Updated"}]}
        result = await client.records.update("people", "rec_01abc", values=values)

        assert route.called
        assert isinstance(result, Record)

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"values": values}}
        await client.close()

    @respx.mock
    async def test_append(self) -> None:
        route = respx.patch(f"{BASE_URL}/objects/people/records/rec_01abc").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_UPDATED)
        )
        client = _async_client()
        values = {"tags": [{"option": {"title": "VIP"}}]}
        result = await client.records.append("people", "rec_01abc", values=values)

        assert route.called
        assert isinstance(result, Record)
        await client.close()

    @respx.mock
    async def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/objects/people/records/rec_01abc").mock(
            return_value=httpx.Response(200, json=MOCK_DELETE_RESPONSE)
        )
        client = _async_client()
        result = await client.records.delete("people", "rec_01abc")

        assert route.called
        assert result is None
        await client.close()

    @respx.mock
    async def test_upsert(self) -> None:
        route = respx.put(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_CREATED)
        )
        client = _async_client()
        values = {
            "email_addresses": [{"email_address": "alice@example.com"}],
            "name": [{"first_name": "Alice", "last_name": "Wonder"}],
        }
        result = await client.records.upsert(
            "people",
            matching_attribute="email_addresses",
            values=values,
        )

        assert route.called
        assert isinstance(result, Record)

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "matching_attribute": "email_addresses",
                "values": values,
            }
        }
        await client.close()

    @respx.mock
    async def test_query(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/people/records/query").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _async_client()
        sorts = [Sort(attribute="created_at", direction="desc")]
        result = await client.records.query(
            "people",
            filter={"name": {"$contains": "Jane"}},
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
            "filter": {"name": {"$contains": "Jane"}},
            "sorts": [{"attribute": "created_at", "direction": "desc"}],
            "limit": 100,
            "offset": 0,
        }
        await client.close()

    @respx.mock
    async def test_get_attribute_values(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/people/records/rec_01abc/attributes/email/values"
        ).mock(
            return_value=httpx.Response(200, json=MOCK_ATTRIBUTE_VALUES_LIST)
        )
        client = _async_client()
        result = await client.records.get_attribute_values(
            "people", "rec_01abc", "email"
        )

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], AttributeValue)
        await client.close()

    @respx.mock
    async def test_list_entries(self) -> None:
        route = respx.get(
            f"{BASE_URL}/objects/people/records/rec_01abc/entries"
        ).mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_ENTRIES_LIST)
        )
        client = _async_client()
        result = await client.records.list_entries("people", "rec_01abc")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], RecordEntry)
        await client.close()

    @respx.mock
    async def test_global_search(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/records/search").mock(
            return_value=httpx.Response(200, json=MOCK_GLOBAL_SEARCH_RESULTS)
        )
        client = _async_client()
        result = await client.records.global_search(
            query="Jane", objects=["people"], limit=10
        )

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], GlobalSearchResult)
        assert result.data[0].record_text == "Jane Doe"

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"query": "Jane", "objects": ["people"], "limit": 10}
        await client.close()

    @respx.mock
    async def test_query_all_multiple_pages(self) -> None:
        """Async query_all iterates across multiple pages."""
        page_1 = {"data": [MOCK_RECORD]}
        page_2 = {"data": [MOCK_RECORD_2]}
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

        respx.post(f"{BASE_URL}/objects/people/records/query").mock(
            side_effect=side_effect
        )
        client = _async_client()
        iterator = client.records.query_all("people", limit=1)
        records: list[Record] = []
        async for record in iterator:
            records.append(record)

        assert len(records) == 2
        assert records[0].id.record_id == "rec_01abc"
        assert records[1].id.record_id == "rec_02xyz"
        assert call_count == 3
        await client.close()

    @respx.mock
    async def test_get_not_found(self) -> None:
        respx.get(f"{BASE_URL}/objects/people/records/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _async_client()
        with pytest.raises(NotFoundError):
            await client.records.get("people", "nonexistent")
        await client.close()

    @respx.mock
    async def test_create_permission_error(self) -> None:
        respx.post(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _async_client()
        with pytest.raises(AttioPermissionError):
            await client.records.create(
                "people", values={"name": [{"first_name": "Test"}]}
            )
        await client.close()


# ---------------------------------------------------------------------------
# Mixin body construction tests
# ---------------------------------------------------------------------------


class TestRecordsMixin:
    """Test the shared body/param construction logic."""

    def test_build_values_body(self) -> None:
        from attio.resources.records import _RecordsMixin

        result = _RecordsMixin._build_values_body({"name": [{"value": "test"}]})
        assert result == {"data": {"values": {"name": [{"value": "test"}]}}}

    def test_build_upsert_body(self) -> None:
        from attio.resources.records import _RecordsMixin

        result = _RecordsMixin._build_upsert_body(
            "email_addresses",
            {"email_addresses": [{"email_address": "a@b.com"}]},
        )
        assert result == {
            "data": {
                "matching_attribute": "email_addresses",
                "values": {"email_addresses": [{"email_address": "a@b.com"}]},
            }
        }

    def test_build_query_body_empty(self) -> None:
        from attio.resources.records import _RecordsMixin

        result = _RecordsMixin._build_query_body()
        assert result == {}

    def test_build_query_body_full(self) -> None:
        from attio.resources.records import _RecordsMixin

        sorts = [Sort(attribute="created_at", direction="desc")]
        result = _RecordsMixin._build_query_body(
            filter={"name": "test"},
            filter_view_id="view_01",
            sorts=sorts,
            limit=100,
            offset=50,
        )
        assert result == {
            "filter": {"name": "test"},
            "filter_view_id": "view_01",
            "sorts": [{"attribute": "created_at", "direction": "desc"}],
            "limit": 100,
            "offset": 50,
        }

    def test_build_query_body_sort_with_field(self) -> None:
        from attio.resources.records import _RecordsMixin

        sorts = [Sort(attribute="location", direction="asc", field="locality")]
        result = _RecordsMixin._build_query_body(sorts=sorts)
        assert result == {
            "sorts": [
                {"attribute": "location", "direction": "asc", "field": "locality"}
            ],
        }

    def test_build_search_body(self) -> None:
        from attio.resources.records import _RecordsMixin

        result = _RecordsMixin._build_search_body(
            query="Jane", objects=["people", "companies"], limit=10
        )
        assert result == {
            "query": "Jane",
            "objects": ["people", "companies"],
            "limit": 10,
        }

    def test_build_search_body_no_limit(self) -> None:
        from attio.resources.records import _RecordsMixin

        result = _RecordsMixin._build_search_body(
            query="test", objects=["people"]
        )
        assert result == {"query": "test", "objects": ["people"]}

    def test_build_list_params_none(self) -> None:
        from attio.resources.records import _RecordsMixin

        result = _RecordsMixin._build_list_params()
        assert result is None

    def test_build_list_params_with_values(self) -> None:
        from attio.resources.records import _RecordsMixin

        result = _RecordsMixin._build_list_params(limit=10, offset=5)
        assert result == {"limit": 10, "offset": 5}

    def test_build_attribute_values_params_default(self) -> None:
        from attio.resources.records import _RecordsMixin

        result = _RecordsMixin._build_attribute_values_params()
        assert result is None

    def test_build_attribute_values_params_with_show_historic(self) -> None:
        from attio.resources.records import _RecordsMixin

        result = _RecordsMixin._build_attribute_values_params(
            show_historic=True, limit=20, offset=0
        )
        assert result == {"show_historic": "true", "limit": 20, "offset": 0}
