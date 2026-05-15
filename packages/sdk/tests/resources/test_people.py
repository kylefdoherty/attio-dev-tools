"""Tests for the People resource (standard object convenience wrapper).

These verify that PeopleResource correctly delegates to RecordsResource
with object_slug='people'. We don't re-test all records logic — just
confirm the delegation and correct URL.
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
TEST_KEY = "test_key_people"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestPeopleResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        result = client.people.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Record)
        assert result.data[0].id.record_id == "rec_01abc"
        client.close()

    @respx.mock
    def test_list_with_params(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        client.people.list(limit=10, offset=5)

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
        result = client.people.get("rec_01abc")

        assert route.called
        assert isinstance(result, Record)
        assert result.id.record_id == "rec_01abc"
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_CREATED)
        )
        client = _sync_client()
        values = {"name": [{"first_name": "Alice", "last_name": "Wonder"}]}
        result = client.people.create(values=values)

        assert route.called
        assert isinstance(result, Record)
        assert result.id.record_id == "rec_03new"

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"values": values}}
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
        result = client.people.upsert(
            matching_attribute="email_addresses", values=values
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
        client.close()

    @respx.mock
    def test_query(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/people/records/query").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        result = client.people.query(
            filter={"name": {"$contains": "Jane"}}, limit=50
        )

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body["filter"] == {"name": {"$contains": "Jane"}}
        assert body["limit"] == 50
        client.close()

    @respx.mock
    def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/objects/people/records/rec_01abc").mock(
            return_value=httpx.Response(200, json={})
        )
        client = _sync_client()
        result = client.people.delete("rec_01abc")

        assert route.called
        assert result is None
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestPeopleResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/people/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _async_client()
        result = await client.people.list()

        assert route.called
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Record)
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/people/records/rec_01abc").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_SINGLE)
        )
        client = _async_client()
        result = await client.people.get("rec_01abc")

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
        result = await client.people.create(values=values)

        assert route.called
        assert isinstance(result, Record)
        assert result.id.record_id == "rec_03new"

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"values": values}}
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
        result = await client.people.upsert(
            matching_attribute="email_addresses", values=values
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
