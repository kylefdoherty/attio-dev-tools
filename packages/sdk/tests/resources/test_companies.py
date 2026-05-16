"""Tests for the Companies resource (standard object convenience wrapper).

Verifies that CompaniesResource delegates to RecordsResource with
object_slug='companies' and that the correct URL paths are used.
"""

from __future__ import annotations

import json

import httpx
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
TEST_KEY = "test_key_companies"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestCompaniesResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/companies/records/query").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        result = client.companies.list()

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], Record)
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/objects/companies/records/rec_01abc").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_SINGLE)
        )
        client = _sync_client()
        result = client.companies.get("rec_01abc")

        assert route.called
        assert isinstance(result, Record)
        assert result.id.record_id == "rec_01abc"
        client.close()

    @respx.mock
    def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/companies/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_CREATED)
        )
        client = _sync_client()
        values = {"name": [{"value": "Acme Corp"}]}
        result = client.companies.create(values=values)

        assert route.called
        assert isinstance(result, Record)

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"values": values}}
        client.close()

    @respx.mock
    def test_upsert(self) -> None:
        route = respx.put(f"{BASE_URL}/objects/companies/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_CREATED)
        )
        client = _sync_client()
        values = {"domains": [{"domain": "acme.com"}], "name": [{"value": "Acme"}]}
        result = client.companies.upsert(
            matching_attribute="domains", values=values
        )

        assert route.called
        assert isinstance(result, Record)

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "matching_attribute": "domains",
                "values": values,
            }
        }
        client.close()

    @respx.mock
    def test_query_uses_companies_slug(self) -> None:
        """Verify the URL uses /objects/companies/records/query."""
        route = respx.post(f"{BASE_URL}/objects/companies/records/query").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _sync_client()
        client.companies.query()

        assert route.called
        request = route.calls[0].request
        assert "/objects/companies/records/query" in str(request.url)
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestCompaniesResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/companies/records/query").mock(
            return_value=httpx.Response(200, json=MOCK_RECORDS_LIST)
        )
        client = _async_client()
        result = await client.companies.list()

        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}
        assert isinstance(result, ListResponse)
        assert len(result.data) == 2
        await client.close()

    @respx.mock
    async def test_create(self) -> None:
        route = respx.post(f"{BASE_URL}/objects/companies/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_CREATED)
        )
        client = _async_client()
        values = {"name": [{"value": "Acme Corp"}]}
        result = await client.companies.create(values=values)

        assert route.called
        assert isinstance(result, Record)

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"data": {"values": values}}
        await client.close()

    @respx.mock
    async def test_upsert(self) -> None:
        route = respx.put(f"{BASE_URL}/objects/companies/records").mock(
            return_value=httpx.Response(200, json=MOCK_RECORD_CREATED)
        )
        client = _async_client()
        values = {"domains": [{"domain": "acme.com"}], "name": [{"value": "Acme"}]}
        result = await client.companies.upsert(
            matching_attribute="domains", values=values
        )

        assert route.called
        assert isinstance(result, Record)
        await client.close()
