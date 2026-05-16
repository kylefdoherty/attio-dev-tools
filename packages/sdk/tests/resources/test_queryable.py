"""Tests for the shared _QueryableMixin / SyncQueryableResource / AsyncQueryableResource base classes.

These tests exercise the base class behaviors (body construction, URL path
assembly, response parsing, HTTP verbs) through minimal concrete subclasses
that do NOT rely on the real Records/Entries resources.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import httpx
import pytest
import respx

from attio._config import ClientConfig
from attio._http import AsyncHttpTransport, HttpTransport
from attio.models._base import AttioModel, ListResponse
from attio.models.common import AttributeValue
from attio.models.records import Sort
from attio.resources._queryable import (
    AsyncQueryableResource,
    SyncQueryableResource,
    _QueryableMixin,
)


# ---------------------------------------------------------------------------
# Minimal model + concrete subclasses for testing
# ---------------------------------------------------------------------------


class WidgetId(AttioModel):
    workspace_id: str
    widget_id: str


class Widget(AttioModel):
    """Tiny model standing in for Record / Entry."""

    id: WidgetId
    name: str
    created_at: datetime


# -- "values"-keyed variant (like Records) --


class SyncWidgetResource(SyncQueryableResource[Widget]):
    _values_key = "values"
    _item_model = Widget

    @staticmethod
    def _collection_path(slug: str) -> str:
        return f"/widgets/{slug}/items"

    @staticmethod
    def _item_path(slug: str, item_id: str) -> str:
        return f"/widgets/{slug}/items/{item_id}"

    # expose the protected methods as public for easier testing
    def list(self, slug: str, **kw: Any) -> ListResponse[Widget]:
        return self._list(slug, **kw)

    def query(self, slug: str, **kw: Any) -> ListResponse[Widget]:
        return self._query(slug, **kw)

    def get(self, slug: str, item_id: str) -> Widget:
        return self._get(slug, item_id)

    def update(self, slug: str, item_id: str, values: dict[str, Any]) -> Widget:
        return self._update(slug, item_id, values)

    def append(self, slug: str, item_id: str, values: dict[str, Any]) -> Widget:
        return self._append(slug, item_id, values)

    def delete(self, slug: str, item_id: str) -> None:
        self._delete(slug, item_id)

    def get_attribute_values(
        self, slug: str, item_id: str, attribute: str, **kw: Any
    ) -> ListResponse[AttributeValue]:
        return self._get_attribute_values(slug, item_id, attribute, **kw)

    def query_all(self, slug: str, **kw: Any):  # noqa: ANN201
        return self._query_all(slug, **kw)


class AsyncWidgetResource(AsyncQueryableResource[Widget]):
    _values_key = "values"
    _item_model = Widget

    @staticmethod
    def _collection_path(slug: str) -> str:
        return f"/widgets/{slug}/items"

    @staticmethod
    def _item_path(slug: str, item_id: str) -> str:
        return f"/widgets/{slug}/items/{item_id}"

    async def list(self, slug: str, **kw: Any) -> ListResponse[Widget]:
        return await self._list(slug, **kw)

    async def query(self, slug: str, **kw: Any) -> ListResponse[Widget]:
        return await self._query(slug, **kw)

    async def get(self, slug: str, item_id: str) -> Widget:
        return await self._get(slug, item_id)

    async def update(self, slug: str, item_id: str, values: dict[str, Any]) -> Widget:
        return await self._update(slug, item_id, values)

    async def append(self, slug: str, item_id: str, values: dict[str, Any]) -> Widget:
        return await self._append(slug, item_id, values)

    async def delete(self, slug: str, item_id: str) -> None:
        await self._delete(slug, item_id)

    async def get_attribute_values(
        self, slug: str, item_id: str, attribute: str, **kw: Any
    ) -> ListResponse[AttributeValue]:
        return await self._get_attribute_values(slug, item_id, attribute, **kw)

    def query_all(self, slug: str, **kw: Any):  # noqa: ANN201
        return self._query_all(slug, **kw)


# -- "entry_values"-keyed variant (like Entries) --


class SyncGadgetResource(SyncQueryableResource[Widget]):
    _values_key = "entry_values"
    _item_model = Widget

    @staticmethod
    def _collection_path(slug: str) -> str:
        return f"/lists/{slug}/gadgets"

    @staticmethod
    def _item_path(slug: str, item_id: str) -> str:
        return f"/lists/{slug}/gadgets/{item_id}"

    def update(self, slug: str, item_id: str, values: dict[str, Any]) -> Widget:
        return self._update(slug, item_id, values)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_queryable"

WIDGET_1: dict[str, Any] = {
    "id": {"workspace_id": "ws_01", "widget_id": "w_01"},
    "name": "Alpha",
    "created_at": "2024-01-01T00:00:00.000Z",
}

WIDGET_2: dict[str, Any] = {
    "id": {"workspace_id": "ws_01", "widget_id": "w_02"},
    "name": "Bravo",
    "created_at": "2024-02-01T00:00:00.000Z",
}

WIDGET_LIST_RESPONSE: dict[str, Any] = {"data": [WIDGET_1, WIDGET_2]}
WIDGET_SINGLE_RESPONSE: dict[str, Any] = {"data": WIDGET_1}
WIDGET_EMPTY_RESPONSE: dict[str, Any] = {"data": []}

MOCK_ATTR_VALUE: dict[str, Any] = {
    "active_from": "2024-01-01T00:00:00.000Z",
    "active_until": None,
    "created_by_actor": {"id": "actor_01", "type": "api-token"},
    "attribute_type": "text",
    "value": "hello@example.com",
}
MOCK_ATTR_VALUES_LIST: dict[str, Any] = {"data": [MOCK_ATTR_VALUE]}


def _config() -> ClientConfig:
    return ClientConfig(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _sync_resource() -> SyncWidgetResource:
    return SyncWidgetResource(HttpTransport(_config()))


def _async_resource() -> AsyncWidgetResource:
    return AsyncWidgetResource(AsyncHttpTransport(_config()))


def _sync_gadget_resource() -> SyncGadgetResource:
    return SyncGadgetResource(HttpTransport(_config()))


# ===================================================================
# 1. _build_query_body
# ===================================================================


class TestBuildQueryBody:
    """Unit tests for _QueryableMixin._build_query_body."""

    def test_empty_when_no_args(self) -> None:
        result = _QueryableMixin._build_query_body()
        assert result == {}

    def test_filter_only(self) -> None:
        result = _QueryableMixin._build_query_body(filter={"name": "test"})
        assert result == {"filter": {"name": "test"}}

    def test_filter_view_id_only(self) -> None:
        result = _QueryableMixin._build_query_body(filter_view_id="view_01")
        assert result == {"filter_view_id": "view_01"}

    def test_sorts_serialized_without_none_fields(self) -> None:
        sorts = [Sort(attribute="created_at", direction="desc")]
        result = _QueryableMixin._build_query_body(sorts=sorts)
        assert result == {
            "sorts": [{"attribute": "created_at", "direction": "desc"}],
        }

    def test_sorts_with_field_included(self) -> None:
        sorts = [Sort(attribute="location", direction="asc", field="city")]
        result = _QueryableMixin._build_query_body(sorts=sorts)
        assert result == {
            "sorts": [{"attribute": "location", "direction": "asc", "field": "city"}],
        }

    def test_limit_only(self) -> None:
        result = _QueryableMixin._build_query_body(limit=50)
        assert result == {"limit": 50}

    def test_offset_only(self) -> None:
        result = _QueryableMixin._build_query_body(offset=10)
        assert result == {"offset": 10}

    def test_all_params(self) -> None:
        sorts = [Sort(attribute="name", direction="asc")]
        result = _QueryableMixin._build_query_body(
            filter={"active": True},
            filter_view_id="view_99",
            sorts=sorts,
            limit=100,
            offset=25,
        )
        assert result == {
            "filter": {"active": True},
            "filter_view_id": "view_99",
            "sorts": [{"attribute": "name", "direction": "asc"}],
            "limit": 100,
            "offset": 25,
        }

    def test_multiple_sorts(self) -> None:
        sorts = [
            Sort(attribute="name", direction="asc"),
            Sort(attribute="created_at", direction="desc"),
        ]
        result = _QueryableMixin._build_query_body(sorts=sorts)
        assert len(result["sorts"]) == 2
        assert result["sorts"][0] == {"attribute": "name", "direction": "asc"}
        assert result["sorts"][1] == {"attribute": "created_at", "direction": "desc"}


# ===================================================================
# 2. _build_values_body -- uses _values_key
# ===================================================================


class TestBuildValuesBody:
    """Verify _build_values_body wraps under the correct key."""

    def test_values_key(self) -> None:
        resource = _sync_resource()
        result = resource._build_values_body({"name": [{"value": "test"}]})
        assert result == {"data": {"values": {"name": [{"value": "test"}]}}}

    def test_entry_values_key(self) -> None:
        resource = _sync_gadget_resource()
        result = resource._build_values_body({"stage": [{"status": "open"}]})
        assert result == {"data": {"entry_values": {"stage": [{"status": "open"}]}}}


# ===================================================================
# 3. _build_list_params
# ===================================================================


class TestBuildListParams:
    def test_none_when_empty(self) -> None:
        result = _QueryableMixin._build_list_params()
        assert result is None

    def test_limit_only(self) -> None:
        result = _QueryableMixin._build_list_params(limit=20)
        assert result == {"limit": 20}

    def test_offset_only(self) -> None:
        result = _QueryableMixin._build_list_params(offset=5)
        assert result == {"offset": 5}

    def test_both(self) -> None:
        result = _QueryableMixin._build_list_params(limit=10, offset=30)
        assert result == {"limit": 10, "offset": 30}


# ===================================================================
# 4. _build_attribute_values_params
# ===================================================================


class TestBuildAttributeValuesParams:
    def test_none_when_defaults(self) -> None:
        result = _QueryableMixin._build_attribute_values_params()
        assert result is None

    def test_show_historic_true(self) -> None:
        result = _QueryableMixin._build_attribute_values_params(show_historic=True)
        assert result == {"show_historic": "true"}

    def test_show_historic_false_omitted(self) -> None:
        result = _QueryableMixin._build_attribute_values_params(show_historic=False)
        assert result is None

    def test_limit_and_offset(self) -> None:
        result = _QueryableMixin._build_attribute_values_params(limit=20, offset=5)
        assert result == {"limit": 20, "offset": 5}

    def test_all_params(self) -> None:
        result = _QueryableMixin._build_attribute_values_params(
            show_historic=True, limit=50, offset=10
        )
        assert result == {"show_historic": "true", "limit": 50, "offset": 10}


# ===================================================================
# 5. Path construction
# ===================================================================


class TestPathConstruction:
    """Verify the concrete subclass URL path helpers."""

    def test_collection_path_values_variant(self) -> None:
        assert SyncWidgetResource._collection_path("things") == "/widgets/things/items"

    def test_item_path_values_variant(self) -> None:
        assert (
            SyncWidgetResource._item_path("things", "id_123")
            == "/widgets/things/items/id_123"
        )

    def test_collection_path_entry_values_variant(self) -> None:
        assert (
            SyncGadgetResource._collection_path("pipeline")
            == "/lists/pipeline/gadgets"
        )

    def test_item_path_entry_values_variant(self) -> None:
        assert (
            SyncGadgetResource._item_path("pipeline", "id_456")
            == "/lists/pipeline/gadgets/id_456"
        )

    def test_base_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            _QueryableMixin._collection_path("x")
        with pytest.raises(NotImplementedError):
            _QueryableMixin._item_path("x", "y")


# ===================================================================
# 6. Response parsing -- correct model type is used
# ===================================================================


class TestResponseParsing:
    def test_parse_list_response(self) -> None:
        resource = _sync_resource()
        result = resource._parse_list_response(WIDGET_LIST_RESPONSE)
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Widget)
        assert result.data[0].name == "Alpha"
        assert result.data[0].id.widget_id == "w_01"

    def test_parse_single_response(self) -> None:
        resource = _sync_resource()
        result = resource._parse_single_response(WIDGET_SINGLE_RESPONSE)
        assert isinstance(result, Widget)
        assert result.name == "Alpha"
        assert result.id.workspace_id == "ws_01"

    def test_parse_attribute_values_response(self) -> None:
        result = _QueryableMixin._parse_attribute_values_response(MOCK_ATTR_VALUES_LIST)
        assert isinstance(result, ListResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], AttributeValue)
        assert result.data[0].attribute_type == "text"

    def test_parse_empty_list(self) -> None:
        resource = _sync_resource()
        result = resource._parse_list_response(WIDGET_EMPTY_RESPONSE)
        assert isinstance(result, ListResponse)
        assert result.data == []


# ===================================================================
# 7. Sync CRUD operations via HTTP (respx)
# ===================================================================


class TestSyncQueryableHTTP:
    """Integration-style tests: concrete subclass -> HTTP -> respx mock."""

    @respx.mock
    def test_list_no_params(self) -> None:
        route = respx.post(f"{BASE_URL}/widgets/things/items/query").mock(
            return_value=httpx.Response(200, json=WIDGET_LIST_RESPONSE)
        )
        resource = _sync_resource()
        result = resource.list("things")

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Widget)
        assert result.data[0].name == "Alpha"

    @respx.mock
    def test_list_with_pagination_params(self) -> None:
        route = respx.post(f"{BASE_URL}/widgets/things/items/query").mock(
            return_value=httpx.Response(200, json=WIDGET_LIST_RESPONSE)
        )
        resource = _sync_resource()
        resource.list("things", limit=10, offset=5)

        body = json.loads(route.calls[0].request.content)
        assert body == {"limit": 10, "offset": 5}

    @respx.mock
    def test_query_sends_post_to_query_endpoint(self) -> None:
        route = respx.post(f"{BASE_URL}/widgets/things/items/query").mock(
            return_value=httpx.Response(200, json=WIDGET_LIST_RESPONSE)
        )
        resource = _sync_resource()
        result = resource.query("things")

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}
        assert isinstance(result, ListResponse)

    @respx.mock
    def test_query_with_all_params(self) -> None:
        route = respx.post(f"{BASE_URL}/widgets/things/items/query").mock(
            return_value=httpx.Response(200, json=WIDGET_LIST_RESPONSE)
        )
        resource = _sync_resource()
        sorts = [Sort(attribute="name", direction="asc")]
        resource.query(
            "things",
            filter={"active": True},
            filter_view_id="view_01",
            sorts=sorts,
            limit=50,
            offset=10,
        )

        body = json.loads(route.calls[0].request.content)
        assert body == {
            "filter": {"active": True},
            "filter_view_id": "view_01",
            "sorts": [{"attribute": "name", "direction": "asc"}],
            "limit": 50,
            "offset": 10,
        }

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/widgets/things/items/w_01").mock(
            return_value=httpx.Response(200, json=WIDGET_SINGLE_RESPONSE)
        )
        resource = _sync_resource()
        result = resource.get("things", "w_01")

        assert route.called
        assert isinstance(result, Widget)
        assert result.name == "Alpha"

    @respx.mock
    def test_update_sends_put_with_values_body(self) -> None:
        route = respx.put(f"{BASE_URL}/widgets/things/items/w_01").mock(
            return_value=httpx.Response(200, json=WIDGET_SINGLE_RESPONSE)
        )
        resource = _sync_resource()
        values = {"name": [{"value": "Updated"}]}
        result = resource.update("things", "w_01", values)

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"data": {"values": {"name": [{"value": "Updated"}]}}}
        assert isinstance(result, Widget)

    @respx.mock
    def test_update_with_entry_values_key(self) -> None:
        """Verify that a resource with _values_key='entry_values' wraps correctly."""
        route = respx.put(f"{BASE_URL}/lists/pipeline/gadgets/g_01").mock(
            return_value=httpx.Response(200, json=WIDGET_SINGLE_RESPONSE)
        )
        resource = _sync_gadget_resource()
        values = {"stage": [{"status": "won"}]}
        resource.update("pipeline", "g_01", values)

        body = json.loads(route.calls[0].request.content)
        assert body == {"data": {"entry_values": {"stage": [{"status": "won"}]}}}

    @respx.mock
    def test_append_sends_patch(self) -> None:
        route = respx.patch(f"{BASE_URL}/widgets/things/items/w_01").mock(
            return_value=httpx.Response(200, json=WIDGET_SINGLE_RESPONSE)
        )
        resource = _sync_resource()
        values = {"tags": [{"value": "VIP"}]}
        result = resource.append("things", "w_01", values)

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"data": {"values": {"tags": [{"value": "VIP"}]}}}
        assert isinstance(result, Widget)

    @respx.mock
    def test_delete_sends_delete_returns_none(self) -> None:
        route = respx.delete(f"{BASE_URL}/widgets/things/items/w_01").mock(
            return_value=httpx.Response(200, json={})
        )
        resource = _sync_resource()
        result = resource.delete("things", "w_01")

        assert route.called
        assert result is None

    @respx.mock
    def test_get_attribute_values_no_params(self) -> None:
        route = respx.get(
            f"{BASE_URL}/widgets/things/items/w_01/attributes/email/values"
        ).mock(return_value=httpx.Response(200, json=MOCK_ATTR_VALUES_LIST))
        resource = _sync_resource()
        result = resource.get_attribute_values("things", "w_01", "email")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], AttributeValue)
        assert result.data[0].attribute_type == "text"

    @respx.mock
    def test_get_attribute_values_with_params(self) -> None:
        route = respx.get(
            f"{BASE_URL}/widgets/things/items/w_01/attributes/email/values"
        ).mock(return_value=httpx.Response(200, json=MOCK_ATTR_VALUES_LIST))
        resource = _sync_resource()
        resource.get_attribute_values(
            "things", "w_01", "email",
            show_historic=True, limit=25, offset=3,
        )

        request = route.calls[0].request
        assert request.url.params["show_historic"] == "true"
        assert request.url.params["limit"] == "25"
        assert request.url.params["offset"] == "3"

    @respx.mock
    def test_query_all_single_page(self) -> None:
        respx.post(f"{BASE_URL}/widgets/things/items/query").mock(
            return_value=httpx.Response(200, json=WIDGET_LIST_RESPONSE)
        )
        resource = _sync_resource()
        items = list(resource.query_all("things", limit=500))

        assert len(items) == 2
        assert all(isinstance(w, Widget) for w in items)

    @respx.mock
    def test_query_all_multi_page(self) -> None:
        """Paginator fetches pages until a partial page is returned."""
        page_1 = {"data": [WIDGET_1]}
        page_2 = {"data": [WIDGET_2]}
        page_3: dict[str, Any] = {"data": []}

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

        route = respx.post(f"{BASE_URL}/widgets/things/items/query").mock(
            side_effect=side_effect
        )
        resource = _sync_resource()
        items = list(resource.query_all("things", limit=1))

        assert len(items) == 2
        assert items[0].name == "Alpha"
        assert items[1].name == "Bravo"
        assert call_count == 3

        # Verify offsets are incremented correctly
        bodies = [json.loads(c.request.content) for c in route.calls]
        assert bodies[0].get("offset", 0) == 0
        assert bodies[1]["offset"] == 1
        assert bodies[2]["offset"] == 2

    @respx.mock
    def test_query_all_passes_filter_and_sorts(self) -> None:
        route = respx.post(f"{BASE_URL}/widgets/things/items/query").mock(
            return_value=httpx.Response(200, json=WIDGET_EMPTY_RESPONSE)
        )
        resource = _sync_resource()
        sorts = [Sort(attribute="name", direction="asc")]
        list(resource.query_all("things", filter={"active": True}, sorts=sorts, limit=100))

        body = json.loads(route.calls[0].request.content)
        assert body["filter"] == {"active": True}
        assert body["sorts"] == [{"attribute": "name", "direction": "asc"}]
        assert body["limit"] == 100


# ===================================================================
# 8. Async CRUD operations via HTTP (respx)
# ===================================================================


class TestAsyncQueryableHTTP:
    """Async variants of the HTTP tests."""

    @respx.mock
    async def test_list(self) -> None:
        route = respx.post(f"{BASE_URL}/widgets/things/items/query").mock(
            return_value=httpx.Response(200, json=WIDGET_LIST_RESPONSE)
        )
        resource = _async_resource()
        result = await resource.list("things")

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Widget)

    @respx.mock
    async def test_list_with_params(self) -> None:
        route = respx.post(f"{BASE_URL}/widgets/things/items/query").mock(
            return_value=httpx.Response(200, json=WIDGET_LIST_RESPONSE)
        )
        resource = _async_resource()
        await resource.list("things", limit=10, offset=5)

        body = json.loads(route.calls[0].request.content)
        assert body == {"limit": 10, "offset": 5}

    @respx.mock
    async def test_query(self) -> None:
        route = respx.post(f"{BASE_URL}/widgets/things/items/query").mock(
            return_value=httpx.Response(200, json=WIDGET_LIST_RESPONSE)
        )
        resource = _async_resource()
        result = await resource.query("things")

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}
        assert isinstance(result, ListResponse)

    @respx.mock
    async def test_query_with_params(self) -> None:
        route = respx.post(f"{BASE_URL}/widgets/things/items/query").mock(
            return_value=httpx.Response(200, json=WIDGET_LIST_RESPONSE)
        )
        resource = _async_resource()
        sorts = [Sort(attribute="name", direction="desc")]
        await resource.query(
            "things",
            filter={"status": "active"},
            sorts=sorts,
            limit=25,
            offset=5,
        )

        body = json.loads(route.calls[0].request.content)
        assert body == {
            "filter": {"status": "active"},
            "sorts": [{"attribute": "name", "direction": "desc"}],
            "limit": 25,
            "offset": 5,
        }

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/widgets/things/items/w_01").mock(
            return_value=httpx.Response(200, json=WIDGET_SINGLE_RESPONSE)
        )
        resource = _async_resource()
        result = await resource.get("things", "w_01")

        assert route.called
        assert isinstance(result, Widget)
        assert result.name == "Alpha"

    @respx.mock
    async def test_update(self) -> None:
        route = respx.put(f"{BASE_URL}/widgets/things/items/w_01").mock(
            return_value=httpx.Response(200, json=WIDGET_SINGLE_RESPONSE)
        )
        resource = _async_resource()
        values = {"name": [{"value": "Updated"}]}
        result = await resource.update("things", "w_01", values)

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"data": {"values": {"name": [{"value": "Updated"}]}}}
        assert isinstance(result, Widget)

    @respx.mock
    async def test_append(self) -> None:
        route = respx.patch(f"{BASE_URL}/widgets/things/items/w_01").mock(
            return_value=httpx.Response(200, json=WIDGET_SINGLE_RESPONSE)
        )
        resource = _async_resource()
        result = await resource.append("things", "w_01", {"tags": [{"value": "VIP"}]})

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"data": {"values": {"tags": [{"value": "VIP"}]}}}
        assert isinstance(result, Widget)

    @respx.mock
    async def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/widgets/things/items/w_01").mock(
            return_value=httpx.Response(200, json={})
        )
        resource = _async_resource()
        result = await resource.delete("things", "w_01")

        assert route.called
        assert result is None

    @respx.mock
    async def test_get_attribute_values(self) -> None:
        route = respx.get(
            f"{BASE_URL}/widgets/things/items/w_01/attributes/email/values"
        ).mock(return_value=httpx.Response(200, json=MOCK_ATTR_VALUES_LIST))
        resource = _async_resource()
        result = await resource.get_attribute_values("things", "w_01", "email")

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], AttributeValue)

    @respx.mock
    async def test_get_attribute_values_with_params(self) -> None:
        route = respx.get(
            f"{BASE_URL}/widgets/things/items/w_01/attributes/email/values"
        ).mock(return_value=httpx.Response(200, json=MOCK_ATTR_VALUES_LIST))
        resource = _async_resource()
        await resource.get_attribute_values(
            "things", "w_01", "email",
            show_historic=True, limit=50, offset=10,
        )

        request = route.calls[0].request
        assert request.url.params["show_historic"] == "true"
        assert request.url.params["limit"] == "50"
        assert request.url.params["offset"] == "10"

    @respx.mock
    async def test_query_all_multi_page(self) -> None:
        page_1 = {"data": [WIDGET_1]}
        page_2 = {"data": [WIDGET_2]}
        page_3: dict[str, Any] = {"data": []}

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

        respx.post(f"{BASE_URL}/widgets/things/items/query").mock(
            side_effect=side_effect
        )
        resource = _async_resource()
        items: list[Widget] = []
        async for item in resource.query_all("things", limit=1):
            items.append(item)

        assert len(items) == 2
        assert items[0].name == "Alpha"
        assert items[1].name == "Bravo"
        assert call_count == 3
