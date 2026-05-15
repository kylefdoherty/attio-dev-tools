"""Tests for the Deals resource (standard object convenience wrapper).

Verifies that DealsResource delegates to RecordsResource with
object_slug='deals' and that the correct URL paths are used.
"""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio.models._base import ListResponse
from attio.models.records import Record

from tests.fixtures.factory import (
    MOCK_RECORD_CREATED,
    MOCK_RECORD_SINGLE,
    MOCK_RECORDS_LIST,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_deals"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestDealsResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        result = client.deals.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Record)
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/records/rec_01abc").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_SINGLE)
        )
        client = _sync_client()
        result = client.deals.get("rec_01abc")

        assert route.called
        assert isinstance(result, Record)
        assert result.id.record_id == "rec_01abc"
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/deals/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_CREATED)
        )
        client = _sync_client()
        values = {"name": [{"value": "Big Deal"}], "deal_value": [{"value": 50000}]}
        result = client.deals.create(values=values)

        assert route.called
        assert isinstance(result, Record)

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"values": values}}
        client.close()

    @respx.mock
    def test_upsert(self) -> None:
        route = respx.put(f"{BASE_URL}/objects/deals/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_CREATED)
        )
        client = _sync_client()
        values = {"name": [{"value": "Big Deal"}]}
        result = client.deals.upsert(matching_attribute="name", values=values)

        assert route.called
        assert isinstance(result, Record)

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "matching_attribute": "name",
                "values": values,
            }
        }
        client.close()

    @respx.mock
    def test_query_uses_deals_slug(self) -> None:
        """Verify the URL uses /objects/deals/records/query."""
        route = respx.post(f"{BASE_URL}/objects/deals/records/query").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        client.deals.query()

        assert route.called
        request = route.calls[0].request
        assert "/objects/deals/records/query" in str(request.url)
        client.close()

    @respx.mock
    def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/objects/deals/records/rec_01abc").mock(
            return_value=httpx.Response(200, json={})
        )
        client = _sync_client()
        result = client.deals.delete("rec_01abc")

        assert route.called
        assert result is None
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestDealsResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _async_client()
        result = await client.deals.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        await client.close()

    @respx.mock
    async def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/deals/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_CREATED)
        )
        client = _async_client()
        values = {"name": [{"value": "Big Deal"}]}
        result = await client.deals.create(values=values)

        assert route.called
        assert isinstance(result, Record)

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"values": values}}
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/deals/records/rec_01abc").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_SINGLE)
        )
        client = _async_client()
        result = await client.deals.get("rec_01abc")

        assert route.called
        assert isinstance(result, Record)
        assert result.id.record_id == "rec_01abc"
        await client.close()
